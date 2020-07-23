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
