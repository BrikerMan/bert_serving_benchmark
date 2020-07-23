import os
from typing import Optional
from fastapi import FastAPI
import numpy as np
import toolkit

os.environ['TF_KERAS']='1'

from bert4keras.models import build_transformer_model
from bert4keras.tokenizers import Tokenizer

app = FastAPI()

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

@app.get("/")
async def hello_world():
    return {"Hello": "World"}


@app.get("/parse")
def parse(sentence: str):
    # encode
    token_ids, segment_ids = tokenizer.encode(sentence)
    x1, x2 = np.array([token_ids]), np.array([segment_ids])
    res = model.predict([x1, x2])
    return {
        "sentence": sentence,
        "token_ids": token_ids,
        "prediction": res.tolist()
        }

if __name__ == "__main__":
    print('\n ===== predicting =====\n')
