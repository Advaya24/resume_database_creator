import re
import traceback
import zipfile
import docx2txt as docx
import pandas as pd
import slate3k as slate
from flask import Flask, redirect, render_template, request, send_file
from flask_cors import CORS
import string

app = Flask(__name__)
CORS(app)


@app.route('/', methods=['GET'])
def hello_world():
    form_name = 'Form'
    df = pd.read_csv('static/Results.csv')
    if df.size > 1:
        form_name += 'Clear'
    return render_template('resume_database_creator/' + form_name + '.html',
                           size=len(df)), 200


@app.route('/', methods=['POST'])
def hello_world_post():
    try:
        df = pd.read_csv('static/Results.csv')[
            ['File_Name', 'Name', 'Email', 'Phone', 'Location']]
        for f in request.files.getlist('file_upload'):
            try:
                text = ''
                if f.content_type == 'application/pdf':
                    pages = slate.PDF(f)
                    for page in pages:
                        text += page
                else:
                    try:
                        text = docx.process(f)
                        # doc = docx.Document(f)
                    except zipfile.BadZipFile:
                        pass

                    # for paragraph in doc.paragraphs:
                    #     text += paragraph.text

                email_pattern = re.compile(
                    '([a-zA-Z0-9._]+@(?:[a-zA-Z]+.)+[a-zA-Z]+)')
                phone_pattern = re.compile('(?:\\+?91-?\\s?)?((?:\\d-?){10})')
                name_pattern = re.compile('(((?: )?(?:[a-zA-Z])+)+)')

                email = ''
                phone = ''
                name = ''
                email_match = email_pattern.findall(text)
                phone_match = phone_pattern.findall(text)
                name_match = name_pattern.match(f.filename)

                if name_match is not None:
                    name = name_match.group()
                if len(email_match) > 0:
                    email = email_match[0]
                if len(phone_match) > 0:
                    phone = phone_match[0]

                # try:
                #     # places_match = geograpy.get_place_context(text=text)
                #     # places_match = GeoText(text)
                #     # cities = places_match.cities
                # except:
                #     cities = ''
                all_cities = pd.read_csv('static/cities.csv')[
                    'name_of_city'].to_list()
                cities = []
                for word in text.split():
                    word = word.translate(
                        str.maketrans('', '', string.punctuation))
                    if word.capitalize() in all_cities:
                        cities.append(word.capitalize())
                if len(cities) == 0:
                    cities = ''

                if not (df['File_Name'] == f.filename).any():
                    df = df.append(
                        {'File_Name': f.filename, 'Name': name, 'Email': email,
                         'Phone': phone, 'Location': cities}, ignore_index=True)
                else:
                    df.loc[df['File_Name'] == f.filename, :] = [f.filename,
                                                                name,
                                                                email,
                                                                phone,
                                                                cities]
                # return {'email': email_match, 'phone': phone_match,
                #         'location': cities, 'status': 200}
            except Exception as e:
                # traceback_str = ''.join(traceback.format_tb(e.__traceback__))
                # return {'traceback': traceback_str, 'Name': f.filename,
                #         'status': 400}, 400
                print(f.filename)
                print(''.join(traceback.format_tb(e.__traceback__)))
        df.to_csv('static/Results.csv')
        return send_file('static/Results.csv',
                         mimetype='text/csv',
                         attachment_filename='Resumes.csv',
                         as_attachment=True), 200
    except:
        return {'response': 'File(s) not uploaded correctly'}, 400


@app.route('/clear/', methods=['POST'])
def clear():
    df = pd.DataFrame(
        columns=['File_Name', 'Name', 'Email', 'Phone', 'Location'])
    df.to_csv('static/Results.csv')
    return redirect('/', code=302)


@app.route('/download/', methods=['POST'])
def download_history():
    return send_file('static/Results.csv', mimetype='text/csv',
                     attachment_filename='Resumes.csv', as_attachment=True), 200


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
