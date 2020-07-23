# Bert Serving Benchmark

This repo is a bechmark for different serving BERT methods.

Requirements:

- docker
- docker-compose
- python3

## Run

Just run, ab test results will be saved to `results` folder.

```shell
python3 run.py   # run all models

python3 run.py -m flask     # run flask and serve model inside flask
python3 run.py -m flask_tf  # run flask with tf_serving

python3 run.py -m fastapi     # run fastapi and serve model inside fastapi
python3 run.py -m fastapi_tf  # run fastapi with tf_serving
```


## Result

```
ab -n 1000 -c 50 http://host:port/task
```

| task     | model      |   Failed request |   Complete requests |   Requests per second |   Time per request |
|:---------|:-----------|-----------------:|--------------------:|----------------------:|-------------------:|
| predict  | fastapi    |                0 |                1000 |                 12.83 |           3896.94  |
| predict  | fastapi_tf |                0 |                1000 |                 20.77 |           2406.94  |
| predict  | flask      |                0 |                 nan |                nan    |            nan     |
| predict  | flask_tf   |                0 |                1000 |                 21.53 |           2322.59  |
| tokenize | fastapi    |                0 |                1000 |               1084.46 |             46.106 |
| tokenize | fastapi_tf |                0 |                1000 |               1143.56 |             43.723 |
| tokenize | flask      |                0 |                1000 |                672.36 |             74.365 |
| tokenize | flask_tf   |                0 |                1000 |                684.84 |             73.009 |

```
ab -n 1000 -c 20 http://host:port/task
```

|    | task     | model      |   Failed request |   Complete requests |   Requests per second |   Time per request |
|---:|:---------|:-----------|-----------------:|--------------------:|----------------------:|-------------------:|
|  2 | predict  | fastapi    |                0 |                1000 |                 13.04 |           1533.71  |
|  0 | predict  | fastapi_tf |                0 |                1000 |                 21.14 |            945.925 |
|  6 | predict  | flask      |                0 |                 nan |                nan    |            nan     |
|  1 | predict  | flask_tf   |                0 |                1000 |                 19.09 |           1047.71  |
|  4 | tokenize | fastapi    |                0 |                1000 |                813.16 |             24.595 |
|  5 | tokenize | fastapi_tf |                0 |                1000 |                932.96 |             21.437 |
|  7 | tokenize | flask      |                0 |                1000 |                596.36 |             33.537 |
|  3 | tokenize | flask_tf   |                0 |                1000 |                613.6  |             32.594 |

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
