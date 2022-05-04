
from time import sleep
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
from sqlalchemy import create_engine, exc
from spark_tasks import upload, batch
import shutil
from threading import Thread

app = Flask(__name__, static_url_path="", static_folder="wordclouds")

engine = create_engine("mysql+pymysql://root:admin@mariadb:3306/data_frequency")

wait_seconds = 5
connection_ok = False
while not connection_ok:
    try:
        engine.connect()
        connection_ok = True
    except exc.SQLAlchemyError:
        print(f"Attempting MariaDB connection again in {wait_seconds}")
        sleep(wait_seconds)

engine.execute('''
    CREATE OR REPLACE TABLE df (
    word char(100) primary key,
    df int
    )
    COLLATE utf8_bin;
        ''')

engine.execute('''
    CREATE OR REPLACE TABLE tf (
        name char(100), word char(100), counts int,
        primary key(name,word))
        COLLATE utf8_bin;
        ''')

engine.execute('''
    CREATE OR REPLACE TABLE tfidf (
        name char(100), word char(100), tfidf int,
        primary key(name,word))
        COLLATE utf8_bin;
        ''')

ALLOWED_EXTENSIONS = {'txt'}
try:
    shutil.rmtree('uploads')
    shutil.rmtree('wordclouds')
except Exception:
    pass

if not os.path.exists('uploads'):
    os.makedirs('uploads')
if not os.path.exists('wordclouds'):
    os.makedirs('wordclouds')

shutil.copyfile('loading.gif', './wordclouds/loading.gif')

app.config['UPLOAD_FOLDER'] = './uploads'
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024 #Allow up to 64 megabyte uploads
wc_dict = {}
show_wc = ""
bj_started = False

def make_tree(path):
    tree = dict(name=os.path.basename(path), children=[])
    try: lst = os.listdir(path)
    except OSError:
        pass #ignore errors
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn):
                tree['children'].append(make_tree(fn))
            else:
                tree['children'].append(dict(name=name))
    return tree

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def toogle_wc(filename):
    global show_wc
    if filename == show_wc:
        show_wc = ""
    else:
        show_wc = filename

def drop_table_entry(filename):
    engine.execute('''
    DELETE FROM tf WHERE name="{}";
        '''.format(filename))

@app.context_processor
def handle_context():
    return dict(os=os)

@app.route('/')
def index():
    return render_template('upload.html', tree=make_tree('./uploads'),
     wc_image=wc_dict, current_wc = show_wc,
     bj_started=bj_started)

@app.route('/', methods=['POST'])
def handle_post():
    global show_wc, bj_started
    if 'delete_file_button' in request.form:
        try:
            filename = list(request.form.values())[0]
            os.remove("./uploads/"+filename)
            filename_png = os.path.splitext(filename)[0] + ".png"
            os.remove("./wordclouds/"+filename_png)
            drop_table_entry(os.path.splitext(filename)[0])
            wc_dict.pop(filename, None)
        except OSError:
            pass
        redirect(url_for('index'))
    elif 'toogle_tc_button' in request.form:
        toogle_wc(list(request.form.values())[0])
        redirect(url_for('index'))
    elif 'file_upload_button' in request.form:
        if 'files[]' not in request.files:
            return redirect(url_for('index'))
        files = request.files.getlist('files[]')
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                thread = Thread(target=upload, args=(file_path, ))
                thread.daemon = True
                thread.start()
                filename_png = os.path.splitext(filename)[0] + ".png"
                wc_dict[filename] = filename_png
                toogle_wc(filename)
        return redirect(url_for('index'))
    elif 'start_bj' in request.form:
        if os.path.exists("./wordclouds/global.png"):
            os.remove("./wordclouds/global.png")
        thread = Thread(target=batch)
        thread.daemon = True
        thread.start()
        bj_started = True
    elif 'rm_uploads' in request.form:
        for f in os.listdir("./uploads"):
            if not f.endswith(".txt"):
                continue
            os.remove(os.path.join(mydir, f))
    return redirect(url_for('index'))