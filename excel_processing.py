import pandas as pd
import requests


report = pd.DataFrame(columns=['Проект', 'Задача', 'Ответственный', 'Исполнитель', 'Затраченное время', 'Итого'])
URL = 'https://cloud-api.yandex.net/v1/disk/resources'
TOKEN = 'y0_AgAEA7qkROuxAAhwEQAAAADPzLZNnWfdrZCyRrOw7_ss_7j6CQU7Tbs'
headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {TOKEN}'}


def upload_file(loadfile, savefile, replace=False):
    global URL
    """Загрузка файла.
    savefile: Путь к файлу на Диске
    loadfile: Путь к загружаемому файлу
    replace: true or false Замена файла на Диске"""
    res = requests.get(f'{URL}/upload?path={savefile}&overwrite={replace}', headers=headers).json()
    print(res)
    with open(loadfile, 'rb') as f:
        try:
            requests.put(res['href'], files={'file': f})
        except KeyError:
            print(res)


def create_folder(path):
    global URL
    requests.put(f'{URL}?path={path}', headers=headers)


def add_to_report(full_name, task_name, project_name, acc_name, el_time):
    # path = "report.xlsx"
    report.loc[len(report)] = {'Проект': project_name, 'Задача': task_name,
                               'Ответственный': full_name, 'Исполнитель': acc_name, 'Затраченное время': int(el_time)}
    report["Итого"] = [report.loc[report["Исполнитель"] == v, "Затраченное время"].sum() for v in report["Исполнитель"]]
    # report.to_excel(path)
    return report


def save_report(rep):
    path = "report.xlsx"
    rep.to_excel(path)


def check_ids(acc_id, b):
    acc = b.get_all('user.get',
                    params={
                        "ID": int(acc_id),
                    })
    acc_name = f"{acc[0]['LAST_NAME']} {acc[0]['NAME']}"
    return acc_name


def find_task_info(task_path, task, b):
    full_task = b.get_all(
        task_path,
        params={
            "taskId": task['ID'],
        })
    # print(full_task)
    full_name = f"{task['RESPONSIBLE_LAST_NAME']} {task['RESPONSIBLE_NAME']}"
    task_name = f"{task['TITLE']}"
    group = full_task['task']['group']
    ids = full_task['task']['accomplices']
    project_name = "Empty"
    if group:
        project_name = group['name']
    return full_name, task_name, ids, project_name


def find_elapse_time(elapse_time_path, task_id, b):
    users_time = {}
    elapsed_items = b.get_all(elapse_time_path,
                              params={
                                  "ID": int(task_id),
                              })
    for item in elapsed_items:
        minutes = 0
        name = check_ids(item['USER_ID'], b)
        if name in users_time:
            minutes = int(users_time[name]) + int(item['MINUTES'])
            users_time[name] = minutes
        else:
            users_time[name] = item['MINUTES']
    return users_time

