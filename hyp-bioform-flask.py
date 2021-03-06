from flask import Flask, make_response, request, render_template
import hypbioform

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# @app.route('/transform', methods=["POST"])
# def transform_view():
#     file = request.files['data_file']
#     if not file:
#         return "No file"

#     file_contents = file.stream.read().decode("utf-8")

#     result = transform(file_contents)

#     response = make_response(result)
#     response.headers["Content-Disposition"] = "attachment; filename=result.csv"
#     return response

def format_response(response, name):
    response.headers["Content-type"] = "text/csv"
    response.headers["Content-Disposition"] = "attachment; filename={}.csv".format(name)
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route('/seniors')
def get_senior_csv():
    result = hypbioform.get_seniors()
    response = make_response(result)    
    return format_response(response, 'bioforms')

@app.route('/groups')
def get_groups_csv():
    result = hypbioform.get_groups()
    response = make_response(result)
    return format_response(response, 'groups')

@app.route('/profs')
def get_profs_csv():
    result = hypbioform.get_profs()
    response = make_response(result)
    return format_response(response, 'profs')

@app.route('/prof_counts')
def get_prof_counts_csv():
    result = hypbioform.get_prof_counts()
    response = make_response(result)
    return format_response(response, 'prof_counts')

if __name__ == '__main__':
   app.run(debug=False)       
