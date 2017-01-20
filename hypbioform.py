#!/usr/bin/env python

import numpy as np
import pandas as pd
import os
import re
import time
import wget

home = os.path.expanduser("~")

#### SENIORS ####
def remove_brackets(string):
    return re.sub('[ ][\[].*?[\]]', '', string)

def get_full_name(row):
    full_name = row['First Name'] + ' '
    if row['Middle Name'] != '':
        full_name += row['Middle Name'] + ' '
    full_name += row['Last Name']
    if row['Suffix'] != '':
        full_name += ', ' + row['Suffix']
    return full_name   

def get_bio_string(row):
    bio = ''
    if row['Date of Birth'] != '':
        birthdate = time.strptime(row['Date of Birth'], '%m-%d-%Y')
        birthdate = time.strftime('%B %-d, %Y', birthdate)
        # birthdate.replace(' 0', ' ')
        bio += 'Born on: ' + birthdate + '. '

    if row['Secondary School Name'] != '':
        bio += 'Secondary School: ' + row['Secondary School Name'].title() + '. '

    # if need to automatically capitalize, then str.title() will work
    if row['Town/City'] != '': 
        bio += 'Hometown: ' + row['Town/City'].title() + ', ' + row['State/Province'] + row['Country'] + '. '

    # could be done more efficiently but whatever
    bio += 'Concentration: ' 
    if row['Concentration Type'] == 'Regular':
        bio += row['Concentration']
    elif row['Concentration Type'] == 'Joint':
        bio += row['Concentration'] + ' & ' + row['Concentration.1']
    else:
        bio += row['Concentration.2']
    bio += '. '

    if row['Secondary Field'] != '':
        bio += 'Secondary Field: ' + row['Secondary Field'] + '. '

    if row['Choose all that apply'] != '':
        bio += row['Choose all that apply'].replace(';', '.') + '. '

    # extracurriculars
    ec = [row['Intercollegiate Sports'], row['House Activities'], row['Harvard Activities'], row['Club Sports']]
    ec = [element for element in ec if element != '']
    if ec != []:
        ec = ' '.join(ec).strip()
        ec = ec.strip()[10:-1].split('; Activity: ')
        ec = [activity.replace(', Officer/Leadership Position: ', ' (').strip() + ')' for activity in ec]
        
        # PBHA processing
        pbha = [element.replace('Phillips Brooks House Association (', '')
                .replace(')', '')
                .replace(' [PBHA]', '') 
                for element in ec
                if '[PBHA]' in element]
        pbha = [element.replace(' (', ': ') + ';' for element in pbha]
        pbha = 'Phillips Brooks House Association (' + ' '.join(pbha)[:-1] + '). '

        ec_str = ''
        for element in ec:
            if '[PBHA]' in element:
                ec_str += pbha
                pbha = ''
                # do something
            else:
                # fix Elena's problems
                if element == 'Harvard Crimson':
                    element = 'The Harvard Crimson'
                if element == 'Harvard Yearbook Publications, Inc.':
                    element = 'Harvard Yearbook Publications'
                ec_str += element + '. '
        ec_str = remove_brackets(ec_str)
        bio += ec_str
    return bio

def get_senior_info(row):
    new_info = [get_full_name(row), 
                get_bio_string(row), 
                row['House'], 
                row['First Name'], 
                row['Last Name'],
                row['E-mail'],
                row['Submission Date']
               ]
    return pd.Series(new_info)
#### END SENIORS ####

#### GROUPS ####
def format_officers(row):
    # officer formatting
    officers = row['Officers']
    officer_str = ''
    
    if officers != '':
        officers = officers[10:-1].split('; Position: ')
        officers = [officer.replace(', Full Name: ', ': ') + '; ' for officer in officers]
        for element in officers:
            officer_str += element
        officer_str = officer_str[:-2]
    return officer_str

def get_groups_info(row):
    new_info = [row['Group Name'], 
                row['Organization Description'], 
                format_officers(row),
                row['Submission Date']
               ]
    return pd.Series(new_info)
#### END GROUPS ####

#### PROFS ####

#### END PROFS ####

def download_seniors():
    if os.path.exists(home + '/Desktop/Senior-Bioform.csv'):
        os.remove(home + '/Desktop/Senior-Bioform.csv')

    wget.download('https://www.jotform.com/csv/70045832837054', home + '/Desktop/Senior-Bioform.csv')
    seniors = pd.read_csv(home + '/Desktop/Senior-Bioform.csv', dtype=str)

    # replace all NaNs
    seniors = seniors.fillna('')

    # strip all leading and trailing whitespace
    seniors = seniors.applymap(lambda x: x.strip())

    return seniors

def get_seniors():
    seniors = download_seniors()

    # construct output row
    seniors = seniors.apply(lambda row: get_senior_info(row), axis=1)
    seniors.columns = ['fullname', 'bio', 'house', 'first_name', 'last_name', 'email', 'time_submitted']
    
    os.remove(home + '/Desktop/Senior-Bioform.csv')

    return seniors.to_csv(index_label='id')

def get_groups():
    if os.path.exists(home + '/Desktop/Group-Info.csv'):
        os.remove(home + '/Desktop/Group-Info.csv')
    wget.download('https://www.jotform.com/csv/70047800855051', home + '/Desktop/Group-Info.csv')

    groups = pd.read_csv(home + '/Desktop/Group-Info.csv', dtype=str)

    # replace all NaNs
    groups = groups.fillna('')

    # strip all leading and trailing whitespace
    groups = groups.applymap(lambda x: x.strip())

    # construct output row
    groups = groups.apply(lambda row: get_groups_info(row), axis=1)
    groups.columns = ['name', 'blurb', 'officers', 'time_submit']
    
    os.remove(home + '/Desktop/Group-Info.csv')

    return groups.to_csv(index_label='id')

def process_profs():
    seniors = download_seniors()

    profs = seniors[['Professor\'s Name (First Name)', 
                     'Professor\'s Name (Last Name)',
                     'Professor\'s E-mail', 
                     'Professor\'s Department']]
    profs.columns = ['first_name', 'last_name', 'email', 'dept']

    # omit everyone who skipped the question
    to_omit = ['', 'n/a', 'omit', ' ', '  ', '.', '-', 'x', 'na', 'a', 'asdf', 'X']
    profs = profs.applymap(lambda x : np.nan if x in to_omit else x).dropna()

    # sort alphabetically
    profs = profs.sort_values(['last_name', 'first_name'], axis=0)

    return profs
    
def get_profs():
    profs = process_profs()
    profs.columns = ['first_name', 'last_name', 'email', 'dept']
    
    os.remove(home + '/Desktop/Senior-Bioform.csv')

    return profs.to_csv()   

def get_prof_counts():

    profs = process_profs()
    prof_counts = profs['last_name'].value_counts()
    
    os.remove(home + '/Desktop/Senior-Bioform.csv')

    return prof_counts.to_csv()

# print '\nFormatted CSVs of the following are now in your Desktop folder:'
# print 'senior bioforms (bioforms.csv)'
# print 'group bioforms (groups.csv)'
# print 'professors (profs.csv)'
# print 'professors\' last names ordered by popularity (prof_ranks.csv)'
# print 'Close this window to continue.'
