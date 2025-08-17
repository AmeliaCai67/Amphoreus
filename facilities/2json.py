import os
import json
import re

def parse_txt_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.rstrip('\n') for line in f.readlines()]
    content = '\n'.join(lines)
    # 提取路径和原动力（允许在同一行）
    path_match = re.search(r'路径：([^\n。]*)', content)
    motive_match = re.search(r'原动力：([^\n。]*)', content)
    # 注释：后面所有内容
    comment_match = re.search(r'注释：([\s\S]*)', content)
    data = {
        '路径': path_match.group(1).strip() if path_match else '',
        '原动力': motive_match.group(1).strip() if motive_match else '',
        '注释': comment_match.group(1).strip() if comment_match else ''
    }
    return data

def main():
    base_dir = 'entity_settings'
    result = {}
    for filename in os.listdir(base_dir):
        if filename.endswith('.txt'):
            filepath = os.path.join(base_dir, filename)
            key = os.path.splitext(filename)[0]
            result[key] = parse_txt_file(filepath)
    # 输出为 json 文件
    with open('entity_settings.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main()