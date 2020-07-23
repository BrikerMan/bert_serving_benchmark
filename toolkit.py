import os
import zipfile
import pathlib

from tensorflow.keras import Model
from tensorflow.keras.utils import get_file
from typing import Optional, Tuple

os.environ['TF_KERAS']='1'

from bert4keras.models import build_transformer_model
from bert4keras.tokenizers import Tokenizer

def download_bert_if_needs(parent_dir: str = None) -> str:
    if parent_dir is None:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.join(dir_path, 'data')
    bert_path = os.path.join(parent_dir, 'chinese_L-12_H-768_A-12')
    if not os.path.exists(bert_path):
        pathlib.Path(bert_path).mkdir(exist_ok=True, parents=True)
        zip_file_path = get_file('chinese_L-12_H-768_A-12.zip',
                'https://storage.googleapis.com/bert_models/2018_11_03/chinese_L-12_H-768_A-12.zip',
                untar=False,
                cache_subdir='',
                cache_dir=parent_dir
        )
        unzipped_file = zipfile.ZipFile(zip_file_path, "r")
        unzipped_file.extractall(path=parent_dir)
    return bert_path


def load_bert(model_path: str, with_model=True) -> Tuple[Optional[Model], Tokenizer]:
    config_path = os.path.join(model_path, 'bert_config.json')
    checkpoint_path = os.path.join(model_path, 'bert_model.ckpt')
    dict_path = os.path.join(model_path, 'vocab.txt')

    tokenizer = Tokenizer(dict_path, do_lower_case=True)  # 建立分词器
    if with_model:
        model = build_transformer_model(config_path, checkpoint_path)
        model.run_eagerly = False
    else:
        model = None
    return model, tokenizer


def convert2saved_model(parent_dir: str = None):
    if parent_dir is None:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.join(dir_path, 'data')
    saved_model_path = os.path.join(parent_dir, 'bert_saved_model', '1')
    if not os.path.exists(saved_model_path):
        bert_path = download_bert_if_needs(parent_dir=parent_dir)
        model, _ = load_bert(bert_path)
        model.save(saved_model_path)

if __name__ == "__main__":
    convert2saved_model()
