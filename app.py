from fast_bitrix24 import Bitrix
from excel_processing import *
from flask import Flask, render_template, request, redirect
import dotenv
import os

app = Flask(__name__)
app.debug = True

env = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_path=env)
webhook = os.getenv('webhook')
load_path = os.getenv('load_path')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/forward/', methods=['POST'])
def bitrix():
    date_from = request.form['trip-f']
    date_to = request.form['trip-l']
    index = 0
    b = Bitrix(webhook)
    print(b)
    cmd = {}
    cmd_before = {}
    elapse = {}
    cmd_elapse = {}
    for i in range(20):
        cmd[f'task_{i}'] = f'tasks.task.list?order[id]=asc&filter[>CREATED_DATE]={date_from}&filter[<CREATED_DATE]={date_to}&start={index}'
        index += 50
    index = 0
    for i in range(20, 30):
        cmd_before[f'task_{i}'] = f'tasks.task.list?order[CREATED_DATE]=desc&filter[<CREATED_DATE]={date_from}&start={index}'
        index += 50
    cmd.update(cmd_before)
    tasks_batch = b.call_batch({
        'halt': 0,
        'cmd': cmd
    })
    for t_batch in tasks_batch:
        tasks_info = tasks_batch[t_batch]['tasks']
        for task in tasks_info:
            task_id = task['id']
            task_user_id = task['responsible']['id']
            project_name = ""
            try:
                project_name = task['group']['name']
            except:
                pass
            elapse[f"{task_id}_{task_user_id}"] = {
                'title': task['title'],
                'project': project_name,
                'user_id':  task['responsible']['id'],
                'user_name': task['responsible']['name'],
                'plan_time': task['durationPlan'],
                'elapse_time': 0
            }
            cmd_elapse[f"{task_id}_{task['responsible']['id']}"] = f"task.elapseditem.getlist?task_id={task_id}&order[ID]=ASC&filter[USER_ID]={task_user_id}"
        tasks_el_batch = b.call_batch({
            'halt': 0,
            'cmd': cmd_elapse
        })
        cmd_elapse = {}
        for task_el_id in tasks_el_batch:
            task_sec = 0
            for el_time in tasks_el_batch[task_el_id]:
                date_stop = el_time['DATE_STOP'].split('T')[0]
                date_start = el_time['DATE_START'].split('T')[0]
                if date_to >= date_stop and date_from >= date_start:
                    task_sec += int(el_time['SECONDS'])
            elapse[task_el_id]['elapse_time'] = task_sec

            add_to_report(elapse[task_el_id]['user_name'], elapse[task_el_id]['project'], elapse[task_el_id]['title'], elapse[task_el_id]['elapse_time'], elapse[task_el_id]['plan_time'])
    save_report()
    folder_path = 'reports'
    save_path = f"{folder_path}/report_{date_from}_{date_to}.xlsx"
    upload_file(load_path, save_path, False)
    return redirect('https://disk.yandex.ru/d/21xSRNmfdR-kVA/')


if __name__ == '__main__':
    app.run()
