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

# model = pickle.load(open('model.pkl', 'rb'))

UPLOAD_FOLDER = 'static/uploads'
IMAGE_FOLDER = 'files'
TEMPLATE_FOLDER = 'templates'
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/model')
def model():
    return render_template('index.html')

@app.route('/evaluate')
def evaluate():
    return render_template('evaluate.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


async def run_model(filename):
    print('inside run_model')
    subprocess.run(["python", filename])


@app.errorhandler(404)
def not_found(e):
    return render_template('error_404.html')


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

    # if success and errors:
    #     errors['message'] = 'File(s) successfully uploaded'
    #     resp = jsonify(errors)
    #     resp.status_code = 206
    #     return resp
    if success:
        resp = jsonify({'message': 'Files successfully uploaded', 'features': my_list})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify(errors)
        resp.status_code = 400
        return resp


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
    # d_data = [pop_data, test_data]
    # receive_data(pop_data, test_data)
    loop.run_until_complete(run_model("model.py"))
    print('loop completed')
    images = {}
    for filename in glob.iglob(IMAGE_FOLDER + '**/*.png', recursive=True):
        # print(os.path.basename(filename))
        with open(filename, mode='rb') as file:
            img = file.read()
            images[os.path.basename(filename).split('.')[0]] = base64.encodebytes(img).decode('utf-8')
    for key in images:
        print(key)
    # page = {'page': render_template('tiles.html')}
    # resp = {'message': 'thanks'}
    return jsonify(images)
    # return pop_data.to_json()


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


@app.route('/show/tiles')
def get_tiles():
    return render_template('tiles.html')


@app.route('/files/<filename>')
def get_image(filename):
    # print('inside get_image')
    # print(send_from_directory(IMAGE_FOLDER, filename))
    return send_from_directory(IMAGE_FOLDER, filename, as_attachment=True)


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
    elif data['action'] == 'data_write':
        file_obj = open('static/uploads/data.txt', 'w')
        file_obj.write(data['data']['cost']+'\n')
        file_obj.write(data['data']['weeks']+'\n')
    file_obj.close()
    resp = jsonify({'action': 'done'})
    return resp


# app.run('localhost', 9001)


if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config["CACHE_TYPE"] = "null"
    app.run(debug=True)