import glob
import pandas as pd
import seaborn as sns

sns.set()


def read_reports() -> pd.DataFrame:
    report_files = glob.glob('./results/*.txt')

    data = []

    for i in report_files:
        rows = i.split('/')[-1].replace('.txt', '').split('_')
        task = rows.pop(len(rows) - 1)
        model = '_'.join(rows)
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

        data.append(item)
    df = pd.DataFrame(data).sort_values(['task', 'model'])
    return df


if __name__ == '__main__':
    df = read_reports()
    print(df.to_markdown())
    # ax = sns.barplot(x="model", y="Requests per second", hue="task",
    #                  data=df[df['task'] == 'predict'])
    # ax.get_figure().savefig("predict.png")
    #
    # ax = sns.barplot(x="model", y="Requests per second", hue="task",
    #                  data=df[df['task'] == 'tokenize'])
    # ax.get_figure().savefig("tokenize.png")
