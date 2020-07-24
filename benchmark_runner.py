# encoding: utf-8

# author: BrikerMan
# contact: eliyar917@gmail.com
# blog: https://eliyar.biz

# file: benchmark_runner.py
# time: 9:57 上午

import os
import urllib
import asyncio
import json
import psutil
import httpx
import pathlib
from asyncio.subprocess import PIPE, STDOUT


class BenchmarkRunner:
    def __init__(self,
                 number_of_requests: int = 1000,
                 number_of_concurrency: int = 50,
                 report_parent_folder: str = './reports',
                 debug: bool = False):
        self.number_of_requests = number_of_requests
        self.number_of_concurrency = number_of_concurrency

        self.report_path = os.path.join(report_parent_folder, f'ab_n_{number_of_requests}_c_{number_of_concurrency}')

        self.debug = False

        pathlib.Path(self.report_path).mkdir(exist_ok=True, parents=True)
        if debug:
            print('===== DEBUG MODE: Will stuck after container started =====')

    async def record_cpu_ram_state(self, method_name: str):
        """
        Record ram and cpu state to <report_path>/performance.json file
        :param method_name:
        :return:
        """
        performance_record = os.path.join(self.report_path, 'performance.json')
        if os.path.exists(performance_record):
            with open(performance_record, 'r') as f:
                content = json.loads(f.read())
        else:
            content = {}
        content[method_name] = []
        while True:
            if method_name not in content:
                content[method_name] = []
            cpu = sum(psutil.cpu_percent(percpu=True))
            ram = psutil.virtual_memory().used / 1024 / 1024
            content[method_name].append({
                'index': len(content[method_name]),
                'cpu': cpu,
                'ram': ram
            })
            with open(performance_record, 'w') as f:
                f.write(json.dumps(content, indent=2))

            await asyncio.sleep(1)
            if self.debug:
                print(f'RAM: {ram} CPU: {cpu}')

    def setup_env_variables(self, method_name: str = 'fastapi'):
        if method_name.endswith('tf_serving'):
            os.environ['TF_SERVING'] = 'True'
        else:
            os.environ['TF_SERVING'] = 'False'

        if method_name.startswith('fastapi'):
            os.environ['WORKER_CLASS'] = "uvicorn.workers.UvicornWorker"
            os.environ['API_MODULE'] = "fastapi_app.main"
        elif method_name.startswith('flask'):
            os.environ['WORKER_CLASS'] = "gevent"
            os.environ['API_MODULE'] = "flask_app.main"
        else:
            raise ValueError(f'Method: {method_name} not supported')

        print('------------- Setup Env Variables ---------------')
        print(f"TF_SERVING   : {os.environ['TF_SERVING']}")
        print(f"WORKER_CLASS : {os.environ['WORKER_CLASS']}")
        print(f"WORKER_COUNT : {os.environ.get('WORKER_COUNT', 4)}")
        print(f"API_MODULE   : {os.environ['API_MODULE']}")
        print('-------------------------------------------------')

    def start_docker_container(self, method_name: str):
        container_down_cmd = "docker-compose -f docker/docker-compose.yml down"
        container_up_cmd = "docker-compose -f docker/docker-compose.yml up --build"
        if not self.debug:
            container_up_cmd += ' -d'

        # Only run api, without tf_serving
        if not method_name.endswith('tf_serving'):
            container_up_cmd += ' api'

        print('---------- Start Docker with command -----------')
        print(f'$ {container_down_cmd}')
        print(f'$ {container_up_cmd}')
        print('-------------------------------------------------')
        os.system(container_down_cmd)
        os.system(container_up_cmd)

    async def wait_until_container_start(self):
        while True:
            try:
                async with httpx.AsyncClient() as client:
                    r = await client.get('http://127.0.0.1:5050/parse?sentence=1234545')
                    print(r.status_code)
                    if r.status_code == 200:
                        print(f"Request success, start ab after 10s")
                        await asyncio.sleep(10)
                        break
            except:
                pass
            print(f"Request failed, wait 3s ...")
            await asyncio.sleep(3)
        print('API test success, start benchmark')

    async def run_apache_ab_benchmark(self, method_name: str):
        query = urllib.parse.quote('今天天气不错呀')
        tasks = {
            'predict': f'http://127.0.0.1:5050/parse?sentence={query}',
            'tokenize': f'http://127.0.0.1:5050/parse?tokenize={query}',
        }

        for task_name, task_url in tasks.items():
            concurrency = self.number_of_concurrency
            requests = self.number_of_requests
            if task_name == 'tokenize':
                requests = requests * 10
                concurrency = concurrency * 2

            ab_cmd = f"ab -n {requests} -c {concurrency} {task_url}"
            print('---------- Start ab with command -----------')
            print(f'$ {ab_cmd}')
            print('--------------------------------------------')

            p = await asyncio.create_subprocess_shell(ab_cmd,
                                                      stdin=PIPE, stdout=PIPE, stderr=STDOUT)
            result_byte, _ = (await p.communicate())
            result = result_byte.decode()
            with open(os.path.join(self.report_path, f'{method_name}_{task_name}.txt'), 'w') as f:
                f.write(result)

            print(f'----- {task_name} Performance Report ------')
            print(result)

    async def run(self, method_name: str):
        print(f'======== Start test method {method_name} ========')

        ram_record_task = asyncio.create_task(self.record_cpu_ram_state(method_name=method_name))

        self.setup_env_variables(method_name=method_name)
        self.start_docker_container(method_name=method_name)
        await self.wait_until_container_start()
        await self.run_apache_ab_benchmark(method_name=method_name)

        ram_record_task.cancel()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--method', type=str, nargs='+',
                        help='runner methos: {fastapi, flask, all}',
                        default=['all'])
    parser.add_argument('-c', '--concurrency', type=int,
                        help='number of concurrency',
                        default=50)
    parser.add_argument('-n', '--n_requests', type=int,
                        help='number of requests',
                        default=1000)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    runner = BenchmarkRunner(number_of_requests=args.n_requests,
                             number_of_concurrency=args.concurrency,
                             debug=args.debug)

    all_methods = ['fastapi', 'flask', 'fastapi_tf', 'flask_tf']
    t_methods = []

    if args.method == ['all']:
        t_methods = all_methods
    else:
        for m in args.method:
            t_methods.append(m)

    for m in t_methods:
        asyncio.run(runner.run(m))
