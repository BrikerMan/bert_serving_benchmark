import os
import numpy as np
from flask import Flask, request, jsonify
import toolkit
import logging
os.environ['TF_KERAS']='1'

from bert4keras.models import build_transformer_model
from bert4keras.tokenizers import Tokenizer

app = Flask(__name__)

bert = toolkit.download_bert_if_needs()
config_path = os.path.join(bert, 'bert_config.json')
checkpoint_path = os.path.join(bert, 'bert_model.ckpt')
dict_path = os.path.join(bert, 'vocab.txt')

tokenizer = Tokenizer(dict_path, do_lower_case=True)  # 建立分词器
model = build_transformer_model(config_path, checkpoint_path)

token_ids, segment_ids = tokenizer.encode(u'Setup flask api')
x1, x2 = np.array([token_ids]), np.array([segment_ids])
res = model.predict([x1, x2])
print('\n' + '='*80)
print(f'Setup model finished, predict result shape: {res.shape}')
print('='*80 + '\n')

@app.route('/')
def index():
    return {"Hello": "World"}


@app.route('/parse')
def parse():
    sentence = request.args
    token_ids, segment_ids = tokenizer.encode(sentence)
    x1, x2 = np.array([token_ids]), np.array([segment_ids])
    res = model.predict([x1, x2])
    return jsonify({
        "sentence": sentence,
        "token_ids": token_ids,
        "prediction": res.tolist()
        })


if __name__ == "__main__":
    app.run()
