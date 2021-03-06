#!/usr/bin/env python

from datetime import datetime
from io import StringIO
import numpy as np
import pandas as pd
import os
import re
from requests import session

# UTC times
SENIOR_BIOFORM_OPEN_DATE = '2017-04-01 00:00:00'

payload = {
        'action': 'btnlogin',
        '_username': os.environ['TYPEFORM_USERNAME'],
        '_password': os.environ['TYPEFORM_PASSWORD']
    }

houses = ['Adams', 'Cabot', 'Currier', 'Dudley', 'Dunster', 'Eliot', 'Kirkland',
          'Leverett', 'Lowell', 'Mather', 'Pforzheimer', 'Quincy', 'Winthrop']

#### SENIORS ####
'''removes extracurriculars with brackets in their name (e.g. Harvard Yearbook Publications [HYP])'''
def remove_brackets(string):
    return re.sub('[ ][\[].*?[\]]', '', string)

'''capitalizes first letter of each word very carefully'''
def title(string):
    if string:
        string = ' '.join(word[0].upper() + word[1:] for word in string.split())
        for word in ['and', 'the', 'in', 'of', 'on', 'at', 'by', 'to', 'off', 'for', 'between', 'with', 'through', 'out', 'a', 'an']:
            string = string.replace(' {} '.format(word.capitalize()), ' {} '.format(word))
        string = string[0].upper() + string[1:]
    return string

def get_full_name(row):
    full_name = row['First Name'].title() + ' '
    if row['Middle Name']:
        if len(row['Middle Name']) == 1:
            full_name += row['Middle Name'] + '. '
        else:
            full_name += row['Middle Name'] + ' '
    full_name += row['Last Name']
    if row['Suffix']:
        if 'J' in row['Suffix'].upper():
            full_name += ', Jr.'# + row['Suffix']
        else:
            full_name += ' ' + row['Suffix']
    return full_name   

def edit_school_name(schoolname):
    # bunch of rules
    schoolname = schoolname.replace(' Junior High School', ' High School')
    schoolname = schoolname.replace(' Senior High School', ' High School')
    schoolname = schoolname.replace(' Senior High School', ' High School')
    schoolname = schoolname.replace('Saint ', 'St. ')
    schoolname = schoolname.replace('Mount ', 'Mt. ')
    schoolname = schoolname.replace(' HS', ' High School')
    schoolname = schoolname.replace(' & ', ' and ')
    schoolname = schoolname.replace(' HS', ' High School')
    schoolname = schoolname.replace(' H.S.', ' High School')
    schoolname = schoolname.replace(' H. S.', ' High School')

    if schoolname == 'Andover' or 'Phillips Andover' in schoolname:
        schoolname = 'Phillips Academy'
    elif schoolname == 'Exeter' or 'Phillips Exeter' in schoolname:
        schoolname = 'Phillips Exeter Academy'
    elif schoolname == 'Collegiate':
        schoolname = 'Collegiate School'
    schoolname = schoolname.replace('Thomas Jefferson High School for Science and Technology', 'Thomas Jefferson High School')

    return schoolname

def edit_city_name(city):
    if city.lower() in ['new york city', 'ny', 'nyc']:
        city = 'New York'

    return city

def edit_country_name(country):
    if country.lower() in ['u.k.', 'uk', 'northern ireland', 'scotland', 'wales', 'england']:
        country = 'United Kingdom'

    return country

def get_bio_string(row):
    bio = ''
    if row['Date of Birth']:
        birthdate = datetime.strptime(row['Date of Birth'], '%Y-%m-%d')
        if birthdate.year < 1900:
            birthdate = birthdate.replace(year=1900)
        birthdate = birthdate.strftime('%B %-d, %Y')
        # birthdate.replace(' 0', ' ')
        bio += 'Born on: {}. '.format(birthdate)

    if row['Secondary School Name']:
        schoolname = edit_school_name(row['Secondary School Name'])

        bio += 'Secondary School: ' + title(schoolname) + '. '

    # if need to automatically capitalize, then str.title() will work
    if row['Town/City']: 
        city = edit_city_name(row['Town/City'])
        country = edit_country_name(row['Country'])
        
        
        bio += 'Hometown: ' + title(city) + ', ' + row['State/Territory'] + title(country) + '. '

    # could be done more efficiently but whatever
    bio += 'Field of Concentration: ' 
    if row['Concentration Type'] == 'Regular':
        bio += row['Concentration']
    elif row['Concentration Type'] == 'Joint':
        # need to go to Typeform to find this number
        bio += row['Joint Concentration in'] + ' & ' + row['Joint Concentration in {{answer_44252884}} and']
    else:
        bio += row['Concentration.1']
    bio += '. '

    if row['Secondary Field']:
        bio += 'Secondary Field: ' + row['Secondary Field'] + '. '

    for prize in ['Detur Prize', 
                  'Junior Phi Beta Kappa', 
                  'Phi Beta Kappa', 
                  'John Harvard Scholar', 
                  'Harvard College Scholar']:
        if row[prize]:
            bio += prize + '. '

    # extracurriculars
    activities = ['Varsity Sport', 'House Activity', 'Activity', 'Club Sport', 'Officer/Leadership Position', 'On-Campus Job', 'Lab or Department Name']
    ec_list = list(row.select(lambda x: x.split('.')[0] in activities))

    if ec_list:
        ec = []

        for i in xrange(0, len(ec_list), 2):
            if ec_list[i] and ec_list[i + 1]:
                ec.append(ec_list[i] + ' (' + title(ec_list[i + 1]) + ')')
            elif ec_list[i]:
                ec.append(ec_list[i])

        # PBHA processing
        pbha = [element.replace('PBHA (', '').replace('Phillips Brooks House Association (', '')
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
                if element.startswith('Harvard Crimson'):
                    element = element.replace('Harvard Crimson', 'The Harvard Crimson')
                if 'Harvard Crimson' in element:
                    element = element.replace(' (Associate Editor)', '') 
                    element = element.replace(', Associate Editor', '') 
                    element = element.replace('Associate Editor, ', '')         
                element = element.replace('Harvard Yearbook Publications, Inc.', 'Harvard Yearbook Publications')
                if element.startswith('Intramurals'):
                    element = element.replace('House ', '')
                    for house in houses:
                        element = element.replace(house + ' ', '')


                ec_str += element + '. '
            
        ec_str = ec_str.replace('  ', ' ')
        ec_str = remove_brackets(ec_str)
        bio += ec_str
    return bio[:525]

def get_senior_info(row):
    new_info = [get_full_name(row), 
                get_bio_string(row), 
                row['House'][:-6], 
                row['First Name'], 
                row['Last Name'],
                row['Email'],
                row['Submit Date (UTC)']
               ]
    return pd.Series(new_info)

def download_seniors():

    with session() as c:
        c.post('https://admin.typeform.com/login_check', data=payload)
        response = c.get('https://admin.typeform.com/form/3146280/analyze/csv')
            
    seniors = pd.read_csv(StringIO(response.text), dtype=str, encoding='utf-8')

    # keep only this year's bioforms
    seniors = seniors[seniors['Start Date (UTC)'] > SENIOR_BIOFORM_OPEN_DATE]

    # replace all NaNs
    seniors = seniors.fillna('')

    # strip all leading and trailing whitespace
    seniors = seniors.applymap(lambda x: x.strip('. '))

    # drop all the yes/no stuff
    seniors = seniors.select(lambda x: not x.startswith('Are you '), axis=1)

    # drop duplicates (overrides with most recent submission)
    seniors = seniors.drop_duplicates(subset=['Email'], keep='last')

    return seniors

def get_seniors():
    seniors = download_seniors()

    # construct output row
    seniors = seniors.apply(get_senior_info, axis=1)
    seniors.columns = ['fullname', 'bio', 'house', 'first_name', 'last_name', 'email', 'time_submitted']
    
    return seniors.to_csv(index_label='id', encoding='utf-8')
#### END SENIORS ####

#### GROUPS ####
def format_officers(row):
    # officer formatting
    officer_list = list(row.select(lambda x: x.startswith('Officer Position') or x.endswith('Full Name')))
    officers = []
    for i in xrange(0, len(officer_list), 2):
        if officer_list[i] and officer_list[i + 1]:
            officers.append(title(officer_list[i]) + ': ' + title(officer_list[i + 1]) + '; ')
    
    return ''.join(officers)[:-2]

def get_groups_info(row):
    new_info = [remove_brackets(row['Group Name']), 
                row['Organization Description'][:750], 
                format_officers(row),
                row['Submit Date (UTC)']
               ]
    return pd.Series(new_info)

def get_groups():
    with session() as c:
        c.post('https://admin.typeform.com/login_check', data=payload)
        response = c.get('https://admin.typeform.com/form/3146326/analyze/csv')

    groups = pd.read_csv(StringIO(response.text), dtype=str, encoding='utf-8')

    # keep only this year's bioforms
    groups = groups[groups['Start Date (UTC)'] > SENIOR_BIOFORM_OPEN_DATE]

    # replace all NaNs
    groups = groups.fillna('')

    # strip all leading and trailing whitespace
    groups = groups.applymap(lambda x: x.strip())

    # drop duplicates (overrides with most recent submission)
    groups = groups.drop_duplicates(subset=['Group Name'], keep='last')
    
    # construct output row
    groups = groups.apply(get_groups_info, axis=1)
    groups.columns = ['name', 'blurb', 'officers', 'time_submit']
    
    return groups.to_csv(index_label='id', encoding='utf-8')
#### END GROUPS ####

#### PROFS ####
def process_profs():
    seniors = download_seniors()

    profs = seniors[['Professor\'s First Name', 
                     'Professor\'s Last Name',
                     'Professor\'s Email', 
                     'Professor\'s Department']]
    profs.columns = ['first_name', 'last_name', 'email', 'dept']

    # omit everyone who skipped the question
    to_omit = ['', 'n/a', 'omit', ' ', '  ', '.', '-', 'x', 'na', 'a', 'asdf', 'X', 'first', 'First', 'no', 'No']
    profs = profs.applymap(lambda x : np.nan if x in to_omit else x).dropna()

    # sort alphabetically
    profs = profs.sort_values(['last_name', 'first_name'], axis=0)

    return profs
    
def get_profs():
    profs = process_profs()
    profs.columns = ['first_name', 'last_name', 'email', 'dept']
    
    return profs.to_csv(encoding='utf-8')   

def get_prof_counts():

    profs = process_profs()
    prof_counts = profs['last_name'].value_counts()
    
    return prof_counts.to_csv(encoding='utf-8')
#### END PROFS ####
