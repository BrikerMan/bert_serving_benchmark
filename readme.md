# Bert Serving Benchmark

This repo is a bechmark for different serving BERT methods.

Requirements:

- docker
- docker-compose
- python3

## Run

Just run, ab test results will be saved to `reports` folder.

```shell
python3 benchmark_runner.py   # run all models

python3 benchmark_runner.py -m flask     # run flask and serve model inside flask
python3 benchmark_runner.py -m flask_tf  # run flask with tf_serving

python3 benchmark_runner.py -m fastapi     # run fastapi and serve model inside fastapi
python3 benchmark_runner.py -m fastapi_tf  # run fastapi with tf_serving
```


## Result

On GCP `n1-standard-4 (4 vCPU, 15 GB memory)` instance with Ubuntu 20.04 LTS Minimal OS.

```
export WORKER_COUNT=8
```

```
ab -n 2000 -c 100 http://host:port/predict
ab -n 20000 -c 200 http://host:port/tokenize
```

|    | task     | model      |   Failed request |   Concurrency |   Complete requests |   Requests per second |   Time per request |
|---:|:---------|:-----------|-----------------:|--------------:|--------------------:|----------------------:|-------------------:|
|  2 | predict  | fastapi    |                0 |           100 |                2000 |                 15.58 |           6418.62  |
|  5 | predict  | fastapi_tf |                0 |           100 |                2000 |                 15.55 |           6430.08  |
|  3 | predict  | flask      |             1789 |           100 |                2000 |                 55.59 |           1798.88  |
|  7 | predict  | flask_tf   |                0 |           nan |                 nan |                nan    |            nan     |
|  0 | tokenize | fastapi    |                0 |           200 |               20000 |               4165.32 |             48.016 |
|  4 | tokenize | fastapi_tf |                0 |           200 |               20000 |               4065.69 |             49.192 |
|  1 | tokenize | flask      |                0 |           200 |               20000 |               1426.87 |            140.167 |
|  6 | tokenize | flask_tf   |                0 |           200 |               20000 |               1509.65 |            132.481 |

```
ab -n 1000 -c 50 http://host:port/predict
ab -n 10000 -c 100 http://host:port/tokenize
```

|    | task     | model      |   Failed request |   Concurrency |   Complete requests |   Requests per second |   Time per request |
|---:|:---------|:-----------|-----------------:|--------------:|--------------------:|----------------------:|-------------------:|
|  2 | predict  | fastapi    |                0 |            50 |                1000 |                 14.28 |           3500.48  |
|  5 | predict  | fastapi_tf |                0 |            50 |                1000 |                 14.41 |           3469.32  |
|  3 | predict  | flask      |                0 |           nan |                 nan |                nan    |            nan     |
|  7 | predict  | flask_tf   |                0 |           nan |                 nan |                nan    |            nan     |
|  0 | tokenize | fastapi    |                0 |           100 |               10000 |               4043.94 |             24.728 |
|  4 | tokenize | fastapi_tf |                0 |           100 |               10000 |               4046.14 |             24.715 |
|  1 | tokenize | flask      |                0 |           100 |               10000 |               1324.8  |             75.483 |
|  6 | tokenize | flask_tf   |                0 |           100 |               10000 |               1504.53 |             66.466 |

```
ab -n 500 -c 10 http://host:port/task
```

|    | task     | model      |   Failed request |   Complete requests |   Requests per second |   Time per request |
|---:|:---------|:-----------|-----------------:|--------------------:|----------------------:|-------------------:|
|  2 | predict  | fastapi    |                0 |                 500 |                 11.3  |            884.981 |
|  0 | predict  | fastapi_tf |                0 |                 500 |                 18.64 |            536.612 |
|  6 | predict  | flask      |              420 |                 500 |                 36.86 |            271.309 |
|  1 | predict  | flask_tf   |                0 |                 500 |                 22.54 |            443.634 |
|  4 | tokenize | fastapi    |                0 |                 500 |                604.02 |             16.556 |
|  5 | tokenize | fastapi_tf |                0 |                 500 |                793.32 |             12.605 |
|  7 | tokenize | flask      |                0 |                 500 |                551.98 |             18.116 |
|  3 | tokenize | flask_tf   |                0 |                 500 |                511.06 |             19.567 |
