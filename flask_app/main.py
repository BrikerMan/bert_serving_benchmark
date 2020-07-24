import os
import numpy as np
from flask import Flask, request
import toolkit
import requests
from typing import Tuple

app = Flask(__name__)

if os.environ.get('TF_SERVING') == 'True':
    model, tokenizer = toolkit.load_bert(toolkit.download_bert_if_needs(), with_model=False)
else:
    model, tokenizer = toolkit.load_bert(toolkit.download_bert_if_needs())

token_ids, segment_ids = tokenizer.encode(u'Setup flask api')
x1, x2 = np.array([token_ids]), np.array([segment_ids])
if model:
    res = model.predict([x1, x2])
    print('\n' + '=' * 80)
    print(f'Setup model finished, predict result shape: {res.shape}')
    print('=' * 80 + '\n')


@app.route('/hello_world')
def index():
    return {"Hello": "World"}


def tokenize_sentence(sentence: str) -> Tuple[np.ndarray, np.ndarray]:
    token_ids, segment_ids = tokenizer.encode(sentence)
    x1, x2 = np.array([token_ids]), np.array([segment_ids])
    return x1, x2


@app.route("/tokenize")
def tokenize():
    sentence = request.args['sentence']
    x1, x2 = tokenize_sentence(sentence)
    return {
        'x1': x1.tolist(),
        'x2': x2.tolist(),
    }


@app.route('/parse')
def parse():
    sentence = request.args['sentence']
    x1, x2 = tokenize_sentence(sentence)
    if model:
        res = model.predict([x1, x2]).tolist()
    else:
        tensor = [{
            "Input-Token": i1.tolist(),
            "Input-Segment": i2.tolist()
        } for i1, i2 in zip(x1, x2)]
        r = requests.post("http://tf_serving:8501/v1/models/bert:predict", json={"instances": tensor})
        res = r.json()['predictions']

    return {
        "sentence": sentence,
        "token_ids": x1.tolist(),
        "prediction": res
    }


if __name__ == "__main__":
    app.run(port=5050)
