import pandas as pd
import requests
import dotenv
import os

env = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_path=env)
URL = os.getenv('url')
TOKEN = os.getenv('token')
report = pd.DataFrame(columns=['Ответственный', 'Проект', 'Задача', 'Затраченное время', 'Запланированное время'])
headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {TOKEN}'}


def convert(seconds):
    mm, ss = divmod(seconds, 60)
    hh, mm = divmod(mm, 60)

    return "%d:%02d:%02d" % (hh, mm, ss)


def upload_file(loadfile, savefile, replace=False):
    global URL, headers, TOKEN
    res = requests.get(f'{URL}/upload?path={savefile}&overwrite={replace}', headers=headers).json()
    print(res)
    with open(loadfile, 'rb') as f:
        try:
            requests.put(res['href'], files={'file': f})
        except KeyError:
            print(res)


def add_to_report(acc_name, project_name, task_name, el_time, t_plan):
    global report
    report.loc[len(report)] = {'Ответственный': acc_name, 'Проект': project_name,
                               'Задача': task_name, 'Затраченное время': int(el_time), 'Запланированное время': t_plan}


def save_report():
    global report
    path = "report.xlsx"
    report = report.drop_duplicates()
    report = report.sort_values(by='Ответственный')
    rep_dict = {v: report.loc[report["Ответственный"] == v, "Затраченное время"].sum() for v in report["Ответственный"]}
    for key in rep_dict:
        report.loc[len(report)] = {'Ответственный': key, 'Проект': '', 'Задача': 'яяя',
                                   'Затраченное время': rep_dict[f'{key}'], 'Запланированное время': ''}
    report = report.sort_values(by=['Ответственный', 'Задача'])
    report.loc[(report["Задача"] == 'яяя'), 'Задача'] = "Итого"
    # report['Затраченное время'] = pd.to_datetime(report['Затраченное время'], unit='s').dt.strftime('%H:%M:%S')
    report['Затраченное время'] = report['Затраченное время'].apply(convert)
    report.to_excel(path, index=False)

