import re
from PySide6.QtCore import QFile, QTextStream
from loguru import logger
import json

def load_json(qt_resource_path : str) -> dict:
    json_file = QFile(qt_resource_path)
    if not json_file.open(QFile.OpenModeFlag.ReadOnly | QFile.OpenModeFlag.Text):
        logger.error(f"Cannot open file {qt_resource_path} for reading.")
        return {}
    stream = QTextStream(json_file)
    json_data = stream.readAll()
    json_file.close()
    
    try:
        return json.loads(json_data)
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from file {qt_resource_path}.")

def extract_update_date(text):
    # 使用正则表达式匹配“更新于”后面的日期
    # \s* 表示任意数量的空白字符（包括空格、制表符、换行符等）
    # \d{4}-\d{2}-\d{2} 表示 YYYY-MM-DD 格式的日期
    # \s*\d{2}:\d{2} 表示 HH:MM 格式的时分
    match = re.search(r'更新于\s*(\d{4}-\d{2}-\d{2}\s*\d{2}:\d{2})', text)

    if match:
        # 提取匹配的日期和时间
        update_date = match.group(1).strip()
        return update_date
    else:
        return text


# remove the trailing whitespace
def sanitize_text(text: str, remove_all: bool = True) -> str:
    if remove_all:
        return re.sub(r'\s+', '', text.strip())
    else:
        return text.strip()


def extract_and_convert_score(text: str):
    # 定义映射关系
    score_mapping = {
        'sml-str5': 0.5,
        'sml-str10': 1.0,
        'sml-str15': 1.5,
        'sml-str20': 2.0,
        'sml-str25': 2.5,
        'sml-str30': 3.0,
        'sml-str35': 3.5,
        'sml-str40': 4.0,
        'sml-str45': 4.5,
        'sml-str50': 5.0
    }

    # 正则表达式模式，用于匹配 `sml-str*` 或 `sml-strs*`
    pattern = r'\bsml-str[s]?\d+\b'

    # 查找第一个匹配的子字符串
    match = re.search(pattern, text)

    if match:
        semantic_text = match.group(0)
        # 将匹配的子字符串转换为对应的分数
        if semantic_text in score_mapping:
            return score_mapping[semantic_text]
        else:
            return -1
    else:
        return -1
