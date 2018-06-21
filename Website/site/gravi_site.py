#!/usr/bin/python3

from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from functools import wraps
import pandas as pd
from login_manager import login_user
from data_manager import get_experiments, get_experiment_plants, get_all_water_data, get_all_balance_data, end_experiment, create_new_experiment, update_target_weights
app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['csv'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_uploaded_file_as_df():
    # Max said it was okay!
    # We Trust people!
    df = pd.DataFrame()
    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        resp = False
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No selected file')
        resp = False
    if file and allowed_file(file.filename):
        print(file.filename)
        resp = True
        df = pd.read_csv(request.files.get('file'))
    else:
        resp = 'Bad upload file'
    return (resp, df)


def checkuser(func):
    """Checks whether user is logged in or passes to login page."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper


@app.route("/", defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
@checkuser
def index(path):
    exps = get_experiments()
    return render_template('index.html', experiments=exps, path=path)


@app.route("/new_experiment",  methods=['GET', 'POST'])
@checkuser
def new_experiment():
    resp = None
    if request.method == 'POST':
        resp, df = get_uploaded_file_as_df()
        if resp:
            resp = create_new_experiment(df, owner=session['username'][:3])
    return render_template('new_experiment.html',
                           resp=resp)


@app.route("/data")
@checkuser
def data():
    exp = request.args.get("experiment")
    data_type = request.args.get("type")
    if 'end' in data_type.lower():
        end_experiment(exp)
    df = get_all_water_data(
        exp) if 'water' in data_type.lower() else get_all_balance_data(exp)
    resp = make_response(df.to_csv())
    resp.headers["Content-Disposition"] = "attachment; filename=export.csv"
    resp.headers["Content-Type"] = "text/csv"
    return resp


@app.route("/experiment", methods=['GET', 'POST'])
@checkuser
def view_experiment():
    resp = None
    exp = request.args.get("experiment")
    plants_df = get_experiment_plants(exp)
    if request.method == 'POST':
        resp, df = get_uploaded_file_as_df()
        if resp:
            resp = update_target_weights(df)
    return render_template('experiment.html',
                           experiment=exp,
                           error=resp,
                           plants=plants_df)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'GET':
        # When this page is visited we want to log out the user
        if 'username' in session:
            session.pop('username', None)
    if request.method == 'POST':
        session['username'] = request.form['username']

        pwd = request.form['password']
        if login_user(app, session['username'], pwd):
            return redirect(url_for('index'))
        else:
            error = 'Invalid Credentials. Please try again.'
    return render_template('login.html', error=error)


if __name__ == "__main__":
    app.secret_key = '8080'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host='0.0.0.0', port=9666, debug=False)
