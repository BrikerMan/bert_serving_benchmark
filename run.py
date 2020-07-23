import os
import time
import urllib.request
import pathlib
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-m', '--method', type=str, nargs='+',
                    help='runner methos: {fastapi, flask, all}',
                    default=['all'])

def run_container_and_ab():
    os.system("docker-compose -f docker/base.yml down")
    os.system("docker-compose -f docker/base.yml up --build -d")
    print("Start waiting for docker images to start.")

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

def run(name: str = 'fastapi'):
    if name == 'fastapi':
        os.environ['WORKER_CLASS'] = "uvicorn.workers.UvicornWorker"
        os.environ['API_MODULE'] = "fastapi_app.main"
    else:
        os.environ['WORKER_CLASS'] = "gevent"
        os.environ['API_MODULE'] = "flask_app.main"
    run_container_and_ab()

    query = urllib.parse.quote('今天天气不错呀')
    result = os.popen(f"ab -n 500 -c 10 http://127.0.0.1:5050/parse?sentence={query}").read()
    pathlib.Path('./results').mkdir(exist_ok=True)
    with open (f'./results/{name}.txt', 'w') as f:
        f.write(result)
    print(result)
    os.system("docker-compose -f docker/base.yml down")



if __name__ == "__main__":
    args = parser.parse_args()
    all_methods = ['fastapi', 'flask']
    t_methods = []
    print(args.method)
    if args.method == ['all']:
        t_methods = all_methods
    else:
        for m in args.method:
            t_methods.append(m)

    for m in t_methods:
        run(m)
