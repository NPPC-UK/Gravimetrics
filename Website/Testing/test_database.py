import pytest
import sys
import pandas as pd
import os
sys.path.append('./site/')

pwd = os.environ['PASSWORD']


@pytest.fixture
def run_site():
    """
    Generates connection to use
    """
    from flask import Flask, render_template, request, redirect, url_for, session
    from login_manager import login_user
    app = Flask(__name__)
    app.secret_key = '8080'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(host='0.0.0.0', port=9666, debug=False)
    yield app


def test_create_connection():
    from conn_manager import get_dbinfo, create_connection
    assert create_connection('gravi') is not None


def test_login():
    from login_manager import login_user
    assert login_user(run_site, 'nah31@aber.ac.uk', pwd)


def test_create_new_experiment():
    from data_manager import create_new_experiment
    df = pd.read_csv('./Testing/Testing_W041_load.csv')
    create_new_experiment(df)


def test_create_new_experiment_same_dates():
    from data_manager import create_new_experiment
    df = pd.read_csv('./Testing/Testing_W041_load.csv')
    df.columns = ['TEST_Same_Dates1', '2022-01-01', '2023-01-01']
    df[df.columns[0]] = df[df.columns[0]]+'66'
    create_new_experiment(df)

    df.columns = ['TEST_Same_Dates2', '2022-01-01', '2023-01-01']
    df[df.columns[0]] = df[df.columns[0]]+'99'
    create_new_experiment(df)


def test_update_target_weights():
    from data_manager import create_new_experiment, update_target_weights
    df = pd.read_csv('./Testing/Testing_W041_load.csv')
    df.columns = ['TEST1', '2022-01-01', '2023-01-01']
    df[df.columns[0]] = df[df.columns[0]]+'1'
    create_new_experiment(df)
    df[df.columns[1]] = df[df.columns[1]]+1
    update_target_weights(df)


def test_end_experiment():
    from data_manager import create_new_experiment, end_experiment
    df = pd.read_csv('./Testing/Testing_W041_load.csv')
    df.columns = ['TEST2', '2020-08-20', '2023-03-03']
    df[df.columns[0]] = df[df.columns[0]]+'2'
    create_new_experiment(df)
    end_experiment('TEST2')


def test_get_experiment_plants():
    from data_manager import create_new_experiment, get_experiment_plants
    df = pd.read_csv('./Testing/Testing_W041_load.csv')
    df.columns = ['TEST3', '2022-04-04', '2024-03-03']
    df[df.columns[0]] = df[df.columns[0]]+'3'
    create_new_experiment(df)
    plants = get_experiment_plants('TEST3')


def test_get_watering_history():
    from data_manager import create_new_experiment, get_watering_history
    df = pd.read_csv('./Testing/Testing_W041_load.csv')
    df.columns = ['TEST4', '2023-04-04', '2025-03-03']
    df[df.columns[0]] = df[df.columns[0]]+'4'
    create_new_experiment(df)
    plants = get_watering_history(40)


def test_get_balance_history():
    from data_manager import create_new_experiment, get_balance_history
    df = pd.read_csv('./Testing/Testing_W041_load.csv')
    df.columns = ['TEST5', '2026-04-04', '2029-03-03']
    df[df.columns[0]] = df[df.columns[0]]+'5'
    create_new_experiment(df)
    plants = get_balance_history(40)


def test_get_all_watering_history():
    from data_manager import create_new_experiment, get_all_water_data
    df = pd.read_csv('./Testing/Testing_W041_load.csv')
    df.columns = ['TEST6', '2024-04-04', '2028-03-03']
    df[df.columns[0]] = df[df.columns[0]]+'6'
    create_new_experiment(df)
    plants = get_all_water_data('TEST6')


def test_get_all_balance_history():
    from data_manager import create_new_experiment, get_all_balance_data
    df = pd.read_csv('./Testing/Testing_W041_load.csv')
    df.columns = ['TEST7', '2027-04-04', '2030-03-03']
    df[df.columns[0]] = df[df.columns[0]]+'7'
    create_new_experiment(df)
    plants = get_all_balance_data('TEST7')
