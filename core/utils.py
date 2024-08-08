import re
import json

# 1. 保证 sample 顺序正确 
# 2. 如果无法匹配 ```sql ```,则让其为空，认为失败，或者标出来，认为无法正确生成vaild sql

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
    sql_pattern = r'`sql(.*?)```'

    #匹配所有样本
    sample_list = re.findall(sample_pattern, sql_ori_content, re.DOTALL)

    sql_match_list = []
    #每个样本中的SQL数量是否等于 1
    for sample_index, sample_content in enumerate(sample_list):
        sql_list = re.findall(sql_pattern, sample_content, re.DOTALL)
        if len(sql_list) == 1:
            sql_match_list.append(sql_list[:])
        else:
            sql_match_list.append(f"Error: 第 {sample_index+1} 个样本有 {len(sql_list)} 个SQL。")

    return sql_match_list



def sql_match(sql_gen_ori_path):
    with open(sql_gen_ori_path, 'r')as f:
        sql_ori_content = f.read()

    # 1. 判断样本（sample）数量正确，顺序正确；
    tag_sample_res = tag_sample(sql_ori_content)

    if tag_sample_res == "All samples are correct":
        sql_list = tag_sql(sql_ori_content)
        for index, sql in enumerate(sql_list):
            # 2. 每个sample中是否有且仅有一个 SQL
            if 'Error: ' in sql:
                print(sql)
                sql_list[index] = ['SELECT']
        return [s[0].replace('\n', ' ').replace('\t', ' ').strip() for s in sql_list]
    else:
        return tag_sample_res




# prompt 构建
# spider 和 bird 不同， bird 加 evidence

def prompt_construction(dataset):

    instance_path = f'./dataset/data_instance/{dataset}_all_instance.json'
    schema_path = f'./dataset/schema_prompt/{dataset}_tables.json'

    with open(instance_path, 'r')as f:
        instance_list = json.load(f)

    with open(schema_path, 'r')as f:
        schema_list = json.load(f)

    prompt_list = []
    
    if dataset == 'spider':
        for instance in instance_list:
            for schema in schema_list:
                if instance['db_id'] == schema['db_id']:
                    schema_prompt = schema['prompt']
                    prompt_tmp = f"""{schema_prompt}
Gave me the SQL query: "{instance['question']}"
No need explanation.
Please output the a brief SQL in the following format:
```sql
...
```"""
            prompt_list.append(prompt_tmp)
    
    elif dataset == 'bird':
        for instance in instance_list:
            for schema in schema_list:
                if instance['db_id'] == schema['db_id']:
                    schema_prompt = schema['prompt']
                    prompt_tmp = f"""{schema_prompt}
Gave me the SQL query: "{instance['question']}"
Here is a helpful evidence: "{instance['evidence']}"
No need explanation.
Please output the a brief SQL in the following format:
```sql
...
```"""
            prompt_list.append(prompt_tmp)
    
    return prompt_list

