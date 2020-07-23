import os
import zipfile
import pathlib
from tensorflow.keras.utils import get_file


def download_bert_if_needs(parent_dir: str = None) -> str:
    if parent_dir is None:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.join(dir_path, 'data')
        pathlib.Path(parent_dir).mkdir(exist_ok=True, parents=True)
    bert_path = os.path.join(parent_dir, 'chinese_L-12_H-768_A-12')
    if not os.path.exists(bert_path):
        zip_file_path = get_file('chinese_L-12_H-768_A-12.zip',
                'https://storage.googleapis.com/bert_models/2018_11_03/chinese_L-12_H-768_A-12.zip',
                untar=False,
                cache_subdir='',
                cache_dir=parent_dir
        )
        unzipped_file = zipfile.ZipFile(zip_file_path, "r")
        unzipped_file.extractall(path=parent_dir)
    return bert_path
