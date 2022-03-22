import pickle
import os
from re import sub
from flask import Flask, send_from_directory, request, redirect, url_for, render_template, jsonify, json
from werkzeug.utils import secure_filename
import pandas as pd
import subprocess
import asyncio
import glob
import base64


loop = asyncio.get_event_loop()


UPLOAD_FOLDER = 'static/uploads'
IMAGE_FOLDER = 'files'
TEMPLATE_FOLDER = 'templates'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Homepage
@app.route('/')
def home():
    return render_template('home.html')


# Function for checking extension of uploaded files
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Async function running model.py and evaluate.py
async def run_model(filename):
    print('inside run_model')
    subprocess.run(["python", filename])


# 404 Handler
@app.errorhandler(404)
def not_found(e):
    return render_template('error_404.html')


# Function for uploading population, test, test-control and performance file on server
@app.route('/upload', methods=['POST'])
def upload():
    if 'files[]' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp

    files = request.files.getlist('files[]')
    errors = {}
    success = False
    my_list = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            df = pd.read_csv('./static/uploads/' + filename)
            my_list = df.columns.values.tolist()
            my_list.insert(0, filename)
            success = True
        else:
            errors[file.filename] = 'File type is not allowed'

    if success:
        resp = jsonify({'message': 'Files successfully uploaded', 'features': my_list})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify(errors)
        resp.status_code = 400
        return resp


# Function sending selected features data
@app.route('/send_data', methods=['POST'])
def send_data():
    file_data = json.loads(request.data)
    population = file_data['population']
    test = file_data['test']
    print(population)
    print(test)
    pdf = pd.read_csv('./static/uploads/' + population[0])
    tdf = pd.read_csv('./static/uploads/' + test[0])
    pop_data = pd.DataFrame()
    test_data = pd.DataFrame()
    for column in population[1:]:
        pop_data[column] = pdf[column]
    for column in population[1:]:
        test_data[column] = tdf[column]
    print(pop_data)
    print(test_data)
    pop_data.to_csv('./files/population.csv',index=False)
    test_data.to_csv('./files/test.csv',index=False)
    loop.run_until_complete(run_model("model.py"))
    print('loop completed')
    images = {}
    for filename in glob.iglob(IMAGE_FOLDER + '**/*.png', recursive=True):
        with open(filename, mode='rb') as file:
            img = file.read()
            images[os.path.basename(filename).split('.')[0]] = base64.encodebytes(img).decode('utf-8')
    for key in images:
        print(key)
    return jsonify(images)


# Function for fetching features
@app.route('/get_dummy', methods=['POST'])
def get_dummy():
    file_data = json.loads(request.data)
    pfilename = file_data['population'] + '.csv'
    tfilename = file_data['test'] + '.csv'
    df = pd.read_csv('./static/uploads/' + pfilename)
    my_list = df.columns.values.tolist()
    my_list.insert(0, pfilename)
    my_list.insert(1, tfilename)
    resp = jsonify({'features': my_list})
    return resp


# Function for running evaluate.py
@app.route('/run_evaluate', methods=['POST'])
def run_evaluate():
    print('inside evaluate')
    loop.run_until_complete(run_model("evaluate.py"))
    print('Evaluate Complete')
    with open('static/uploads/eval.txt') as file:
        data = json.load(file)
    print(type(data))
    file.close()
    return data


# Function for writing week and cost in files
@app.route('/write', methods=['POST'])
def write_file():
    data = json.loads(request.data)
    print(data)
    if data['action'] == 'file_name_append':
        file_obj = open('static/uploads/file.txt', 'a')
        file_obj.write(data['data']+'\n')
    elif data['action'] == 'file_name_write':
        file_obj = open('static/uploads/file.txt', 'w')
        file_obj.write(data['data']+'\n')
    elif data['action'] == 'write_cost':
        file_obj = open('static/uploads/data.txt', 'w')
        file_obj.write(data['data']['cost_or_week']+'\n')
    elif data['action'] == 'write_weeks':
        file_obj = open('static/uploads/data.txt', 'r')
        cost = file_obj.readline()
        file_obj.close()
        file_obj = open('static/uploads/data.txt', 'w')
        file_obj.write(cost + data['data']['cost_or_week']+'\n')
    file_obj.close()
    resp = jsonify({'action': 'done'})
    return resp


# Function for saving result and result2 (html files)
@app.route('/saveaspdf', methods=['POST'])
def saveaspdf():
    data = json.loads(request.data)
    file = open('static/css/style.css', 'r')
    css = file.read()
    css2 = '''
    #result, #result2 {
        display: block;
    }
    '''
    html = '''<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
        <link rel="stylesheet" href="../css/style.css">
        <style> 
        {css}
        {css2}
        </style>
        <script src="https://kit.fontawesome.com/67361f458b.js" crossorigin="anonymous"></script>
        <title>{title}</title>
    </head>
    <body id="insights_body" onload="window.print()">
        <div id="{result}">
    '''.format(css=css, css2=css2, result=data['result'], title=data['title'])
    html = html + data['div']
    html = html + '''
    </div>
    </body>
    </html>
    '''
    file_name = 'static/files/' + data['filename']
    print(file_name)
    file_obj = open(file_name, 'w', encoding="utf-8")
    file_obj.write(html)
    resp = jsonify({'action': 'done'})
    return resp


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config["CACHE_TYPE"] = "null"
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=5678, debug=False)