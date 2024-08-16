import re
import json


def tag_sample(sql_ori_content):
    pattern = r'-------------------------(.*?) sample_num'
    index_list = re.findall(pattern, sql_ori_content, re.DOTALL)
    index_list = [int(s) for s in index_list]

    tag = 0
    for index_index, index_sample in enumerate(index_list):
        if index_index == index_sample:
            continue
        else:
            tag = index_index
            break

    if tag == 0:
        return ("All samples are correct")
    else:
        return (f"Error: 第{tag}个样本开始，有错误（缺少 or 重复）")


def tag_sql(sql_ori_content):
    sql_ori_content += '-------------------------'
    sample_pattern = r'sample_num(.*?)-------------------------'
    sql_pattern = r'```sql(.*?)```'

    sample_list = re.findall(sample_pattern, sql_ori_content, re.DOTALL)
    sql_match_list = []

    for sample_index, sample_content in enumerate(sample_list):
        sql_list = re.findall(sql_pattern, sample_content, re.DOTALL)
        if len(sql_list) == 1:
            sql_match_list.append(sql_list[0].strip())
        else:
            sql_match_list.append(f"Error: 第 {sample_index + 1} 个样本有 {len(sql_list)} 个SQL。")

    return sql_match_list


def sql_match(sql_gen_ori_path):
    try:
        # 尝试使用 utf-8 编码读取文件
        with open(sql_gen_ori_path, 'r', encoding='utf-8') as f:
            sql_ori_content = f.read()
    except UnicodeDecodeError as e:
        # 处理可能的编码错误
        print(f"Error reading file {sql_gen_ori_path}: {e}")
        return

    tag_sample_res = tag_sample(sql_ori_content)
    if tag_sample_res != "All samples are correct":
        return tag_sample_res

    sql_list = tag_sql(sql_ori_content)
    return [s.replace('\n', ' ').replace('\t', ' ').strip() for s in sql_list]


import json

def prompt_construction(dataset):
    instance_path = f'./dataset/data_instance/{dataset}_all_instance.json'
    schema_path = f'./dataset/schema_prompt/{dataset}_tables.json'

    with open(instance_path, 'r', encoding='utf-8') as f:
        instance_list = json.load(f)

    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_list = json.load(f)

    prompt_list = []

    if dataset == 'spider':
        for instance in instance_list:
            for schema in schema_list:
                if instance['db_id'] == schema['db_id']:
                    schema_prompt = schema['prompt']
                    prompt_tmp = f"""{schema_prompt}
Give me the SQL query: "{instance['question']}"
No need explanation.
Please output the a brief SQL in the following format:
```sql
...
```"""
                    prompt_list.append(prompt_tmp)  # 将 prompt_tmp 添加到 prompt_list 中

    elif dataset == 'bird':
        for instance in instance_list:
            for schema in schema_list:
                if instance['db_id'] == schema['db_id']:
                    schema_prompt = schema['prompt']
                    prompt_tmp = f"""{schema_prompt}
Give me the SQL query: "{instance['question']}"
Here is a helpful evidence: "{instance['evidence']}"
No need explanation.
Please output the a brief SQL in the following format:
```sql
...
```"""
                    prompt_list.append(prompt_tmp)  # 将 prompt_tmp 添加到 prompt_list 中

    return prompt_list
