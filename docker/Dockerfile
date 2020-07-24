# Version: 1.0
# Name: Python3.6

# FROM brikerman/ubuntu20.04_python3:3.8-cn
FROM brikerman/ubuntu18.04_python3:3.8-cn

ENV PYTHONPATH=/code/ \
    PYTHONIOENCODING=utf-8 \
    API_RUN_ENV=docker \
    # 环境名称
    API_ENV=dev  \
    API_PORT=5005 \
    TERM=xterm-256color

WORKDIR /code
COPY ./requirements.container.txt /code/requirements.txt
RUN pip3 install -r /code/requirements.txt --no-cache-dir

COPY . /code/

CMD gunicorn -c gun.py -k ${WORKER_CLASS} ${API_MODULE}:app
