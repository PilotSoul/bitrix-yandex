from fast_bitrix24 import Bitrix
from excel_processing import *
from flask import Flask, render_template
from datetime import datetime



app = Flask(__name__)
app.debug = True

webhook = "https://truecode.bitrix24.ru/rest/599/du721ie4n0jjvbc2/"
tasks_path = 'task.item.list.json'
full_task_path = 'tasks.task.get'
elapse_time_path = 'task.elapseditem.getlist'


@app.route('/')
def index():
    # return "Hello"
    return render_template('index.html')


@app.route('/forward/', methods=['POST'])
def bitrix():
    b = Bitrix(webhook)
    tasks = b.get_all(tasks_path)
    for task in tasks:
        task_id = task['ID']
        full_name, task_name, ids, project_name = find_task_info(full_task_path, task, b)
        tasks_time = find_elapse_time(elapse_time_path, task_id, b)
        for name in tasks_time:
            rep = add_to_report(full_name, task_name, project_name, name, tasks_time[name])
    save_report(rep)
    now = datetime.now()
    t = now.strftime("%d-%m-%Y_%H-%M")
    p = 'test_folder'
    load_path = "/Users/PilotSoul/Desktop/bitrix_yandex/report.xlsx"
    save_path = f"test_folder/report_{str(t)}.xlsx"
    upload_file(load_path, save_path, False)

    return 'Ok'


if __name__ == '__main__':
    app.run()
