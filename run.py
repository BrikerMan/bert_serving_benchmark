import os
import time
import urllib.request
import pathlib
import argparse

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


def run(name: str = 'fastapi', tf_serving: bool = False, debug: bool = False):
    setup_env_variables(name=name, tf_serving=tf_serving, debug=debug)
    run_container_and_ab(tf_serving=tf_serving, debug=debug)

    pathlib.Path('./results').mkdir(exist_ok=True)
    query = urllib.parse.quote('今天天气不错呀')

    tasks = {
        'predict': f'http://127.0.0.1:5050/parse?sentence={query}',
        'tokenize': f'http://127.0.0.1:5050/parse?tokenize={query}',
    }

    for task_name, task_url in tasks.items():
        result = os.popen(f"ab -n 500 -c 10 {task_url}").read()
        with open(f"./results/{name}{'_tf' if tf_serving else ''}_{task_name}.txt", 'w') as f:
            f.write(result)
        print(f'--------- {task_name} Performance ----------')
        print(result)

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
        run(rows[0], tf_serving=rows[-1] == 'tf', debug=args.debug)
