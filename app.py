from flask import Flask, request, render_template, send_file, redirect, url_for
import geograpy
import slate3k as slate
import re
import docx
import zipfile
import pandas as pd

app = Flask(__name__)


@app.route('/', methods=['GET'])
def hello_world():
    form_name = 'Form'
    df = pd.read_csv('static/Results.csv')
    if df.size > 1:
        form_name += 'Clear'
    return render_template('flask-hello-world/' + form_name + '.html',
                           size=len(df)), 200


@app.route('/', methods=['POST'])
def hello_world_post():
    try:
        df = pd.read_csv('static/Results.csv')[
            ['File_Name', 'Email', 'Phone', 'Location']]
        for f in request.files.getlist('file_upload'):
            try:
                text = ''
                if f.content_type == 'application/pdf':
                    pages = slate.PDF(f)
                    for page in pages:
                        text += page
                else:
                    doc = None
                    try:
                        doc = docx.Document(f)
                    except zipfile.BadZipFile:
                        pass

                    for paragraph in doc.paragraphs:
                        text += paragraph.text

                email_pattern = re.compile(
                    '([a-zA-Z0-9._]+@(?:[a-zA-Z]+.)+[a-zA-Z]+)')
                phone_pattern = re.compile('(?:\\+?91-?\\s?)?((?:\\d-?){10})')

                email = ''
                phone = ''
                email_match = email_pattern.findall(text)
                phone_match = phone_pattern.findall(text)
                # if email_match is not None:
                #     email = email_match.group()
                # if phone_match is not None:
                #     phone = phone_match.group()

                try:
                    places_match = geograpy.get_place_context(text=text)
                    cities = places_match.cities
                except:
                    cities = []
                if not (df['File_Name'] == f.filename).any():
                    df = df.append(
                        {'File_Name': f.filename, 'Email': email_match,
                         'Phone': phone_match, 'Location': cities},
                        ignore_index=True)
                else:
                    df.loc[df['File_Name'] == f.filename, :] = [f.filename,
                                                                email_match,
                                                                phone_match,
                                                                cities]
                # return {'email': email_match, 'phone': phone_match,
                #         'location': cities, 'status': 200}
            except:
                # return {'response': 'File(s) not uploaded correctly', 'status': 400}
                pass
        df.to_csv('static/Results.csv')
        return send_file('static/Results.csv',
                         mimetype='text/csv',
                         attachment_filename='Resumes.csv',
                         as_attachment=True), 200
    except:
        return {'response': 'File(s) not uploaded correctly'}, 400


@app.route('/clear/', methods=['POST'])
def clear():
    df = pd.DataFrame(columns=['File_Name', 'Email', 'Phone', 'Location'])
    df.to_csv('static/Results.csv')
    return redirect('/', code=302)


@app.route('/download/', methods=['POST'])
def download_history():
    return send_file('static/Results.csv', mimetype='text/csv',
                     attachment_filename='Resumes.csv', as_attachment=True), 200


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
