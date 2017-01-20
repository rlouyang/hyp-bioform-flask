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

@app.route('/seniors')
def get_senior_csv():
    # result = get_senior()
    result = hypbioform.get_seniors()

    response = make_response(result)
    response.headers["Content-Disposition"] = "attachment; filename=bioforms.csv"
    response.headers["Cache-Control"] = "must-revalidate"
    response.headers["Pragma"] = "must-revalidate"
    response.headers["Content-type"] = "application/csv"
    return response

@app.route('/groups')
def get_groups_csv():
    # result = get_senior()
    result = hypbioform.get_groups()

    response = make_response(result)
    response.headers["Content-Disposition"] = "attachment; filename=groups.csv"
    response.headers["Cache-Control"] = "must-revalidate"
    response.headers["Pragma"] = "must-revalidate"
    response.headers["Content-type"] = "application/csv"
    return response

@app.route('/profs')
def get_profs_csv():
    # result = get_senior()
    result = hypbioform.get_profs()

    response = make_response(result)
    response.headers["Content-Disposition"] = "attachment; filename=profs.csv"
    response.headers["Cache-Control"] = "must-revalidate"
    response.headers["Pragma"] = "must-revalidate"
    response.headers["Content-type"] = "application/csv"
    return response

@app.route('/prof_counts')
def get_prof_counts_csv():
    # result = get_senior()
    result = hypbioform.get_prof_counts()

    response = make_response(result)
    response.headers["Content-Disposition"] = "attachment; filename=prof_counts.csv"
    response.headers["Cache-Control"] = "must-revalidate"
    response.headers["Pragma"] = "must-revalidate"
    response.headers["Content-type"] = "application/csv"
    return response 

if __name__ == '__main__':
   app.run(debug=True)       
