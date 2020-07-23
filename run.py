import os
import time
import json
import psutil
import urllib.request
import pathlib
import argparse
import asyncio
from asyncio.subprocess import PIPE, STDOUT

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--method', type=str, nargs='+',
                    help='runner methos: {fastapi, flask, all}',
                    default=['all'])
parser.add_argument('--debug', action='store_true')


def setup_env_variables(name: str = 'fastapi', tf_serving: bool = False, debug: bool = False):
    if tf_serving:
        os.environ['TF_SERVING'] = 'True'
        print(f'----- Start run {name} with tf-serving -----')
    else:
        print(f'----- Start run {name} -----')

    if name == 'fastapi':
        os.environ['WORKER_CLASS'] = "uvicorn.workers.UvicornWorker"
        os.environ['API_MODULE'] = "fastapi_app.main"
    else:
        os.environ['WORKER_CLASS'] = "gevent"
        os.environ['API_MODULE'] = "flask_app.main"


def run_container_and_ab(tf_serving: bool, debug: bool = False):
    os.system("docker-compose -f docker/docker-compose.yml down")
    start_command = "docker-compose -f docker/docker-compose.yml up --build"
    if not debug:
        start_command += ' -d'
    # Only run api, without tf_serving
    if not tf_serving:
        start_command += ' api'

    print('---------- Start Docker with command -----------')
    print(start_command)
    print('-------------------------------------------------')
    os.system(start_command)

    start_finished = False
    try_times = 0
    while not start_finished:
        try:
            with urllib.request.urlopen('http://127.0.0.1:5050/parse?sentence=1234') as response:
                if response.status == 200:
                    start_finished = True
                    time.sleep(10)
        except:
            pass
        print(f"{try_times} | Still starting, wait 3s ...")
        time.sleep(3)
        try_times += 1

async def get_cpu_state(method):
    while True:
        if os.path.exists('./results/performance.json'):
            with open('./results/performance.json', 'r') as f:
                content = json.loads(f.read())
        else:
            content = {}

        if method not in content:
            content[method] = []
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().used / 1024 / 1024
        content[method].append({
            'index': len(content[method]),
            'cpu': cpu,
            'ram': ram
        })
        with open('./results/performance.json', 'w') as f:
            f.write(json.dumps(content))

        await asyncio.sleep(1)
        print(f"RAM: {ram}")
        print(f"CPU: {cpu}")

async def performance_report(name: str = 'fastapi', tf_serving: bool = False, debug: bool = False):
    query = urllib.parse.quote('今天天气不错呀')
    tasks = {
        'predict': f'http://127.0.0.1:5050/parse?sentence={query}',
        'tokenize': f'http://127.0.0.1:5050/parse?tokenize={query}',
    }

    for task_name, task_url in tasks.items():
        cmd = f"ab -n 500 -c 10 {task_url}"
        p = await asyncio.create_subprocess_shell(cmd,
            stdin=PIPE, stdout=PIPE, stderr=STDOUT)
        result_byte, _ = (await p.communicate())
        result = result_byte.decode()
        with open(f"./results/{name}{'_tf' if tf_serving else ''}_{task_name}.txt", 'w') as f:
            f.write(result)
        print(f'--------- {task_name} Performance ----------')
        print(result)

async def start_test(name: str = 'fastapi', tf_serving: bool = False, debug: bool = False):
    setup_env_variables(name=name, tf_serving=tf_serving, debug=debug)
    run_container_and_ab(tf_serving=tf_serving, debug=debug)

    pathlib.Path('./results').mkdir(exist_ok=True)


    cpu_record_task = asyncio.create_task(get_cpu_state(name))
    ab_test_task = asyncio.create_task(performance_report(name, tf_serving, debug))

    # Wait until ab finished, then cancel the cpu recording
    await ab_test_task
    cpu_record_task.cancel()

    os.system("docker-compose -f docker/docker-compose.yml down")


if __name__ == "__main__":
    args = parser.parse_args()
    all_methods = ['fastapi', 'flask', 'fastapi_tf', 'flask_tf']
    t_methods = []

    if args.method == ['all']:
        t_methods = all_methods
    else:
        for m in args.method:
            t_methods.append(m)

    for m in t_methods:
        rows = m.split('_')
        asyncio.run(start_test(rows[0], tf_serving=rows[-1] == 'tf', debug=args.debug))
