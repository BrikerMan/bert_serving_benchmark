import glob
import pandas as pd
import seaborn as sns
import os
import json
import matplotlib.pyplot as plt

plt.rcParams['figure.dpi'] = 160

sns.set()


def read_reports(path: str) -> pd.DataFrame:
    report_files = glob.glob(f'{path}/*.txt')

    data = []

    for i in report_files:
        rows = i.split('/')[-1].replace('.txt', '').split('|')
        model, task = rows[0], rows[1]

        with open(i, 'r') as f:
            content = f.read().splitlines()
        item = {
            'task': task,
            'model': model,
            'Failed request': 0
        }

        for line in content:
            if line.startswith('Requests per second:'):
                count = line.replace('Requests per second:', '').strip()
                count = count.split('[#/sec]')[0]
                count = float(count)
                item['Requests per second'] = count

            if line.startswith('Time per request:') and not line.endswith('concurrent requests)'):
                count = line.replace('Time per request:', '').strip()
                count = count.split('[ms] (mean)')[0]
                count = float(count)
                item['Time per request'] = count

            if line.startswith('Failed requests:'):
                count = line.replace('Failed requests:', '').strip()
                count = int(count)
                item['Failed request'] = count

            if line.startswith('Complete requests:'):
                count = line.replace('Complete requests:', '').strip()
                count = int(count)
                item['Complete requests'] = count

            if line.startswith('Concurrency Level:'):
                count = line.replace('Concurrency Level:', '').strip()
                count = int(count)
                item['Concurrency'] = count

        data.append(item)
    df = pd.DataFrame(data).sort_values(['task', 'model'])
    return df


def plot_cpu_ram(path):
    record_path = os.path.join(path, 'performance.json')
    with open(record_path, 'r') as f:
        data = json.loads(f.read())

    new = []
    for method, items in data.items():
        for item in items:
            item['method'] = method
            new.append(item)

    df = pd.DataFrame(new)
    df['ram'] = df['ram'] / 1024
    df['second'] = df.pop('index')

    f, axes = plt.subplots(1, 2, figsize=(18, 8))

    sns.lineplot(x='second', y='ram', hue='method', data=df, ax=axes[0])
    sns.lineplot(x='second', y='cpu', hue='method', data=df, ax=axes[1])

    axes[0].set_title('RAM')
    axes[0].set_ylabel('Used RAM (GB)')
    axes[1].set_title('CPU')
    axes[1].set_title('4v CPU')

    f.savefig(os.path.join(path, 'ram_cpu_stats.png'))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--path', type=str,
                        help='report files path')
    args = parser.parse_args()

    df = read_reports(args.path)
    print(f'==== result of folder {args.path} ====')
    print(df.to_markdown(showindex="never"))
    plot_cpu_ram(args.path)
