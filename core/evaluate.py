import sqlite3
from concurrent.futures import ThreadPoolExecutor, TimeoutError

def execute_sql(sql, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        return "Error: unexcutable"   # -1
    finally:
        conn.close()

#  无法执行: -1; 超时: -2; 结果错误: 0; 结果正确： 1.
def execute_sql_with_timeout(sql, db_path, timeout=10):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(execute_sql, sql, db_path)
        try:
            result = future.result(timeout=timeout)
        except TimeoutError:
            result = "Error: timeout" # -2
    return result

# pre_sql_path: '/results/sql_gen_clean/llama3_70b_spider_clean.txt'
# gold_sql_path: '/dataset/data_instance/spider_all_gold.txt'
# db_path: '/dataset/spider/database'
def ex_evaluation(pre_sql_path, gold_sql_path, db_path):
    # 读入文件
    with open(pre_sql_path, 'r') as f:
        pre_sql_list = [s.strip() for s in f.readlines()]

    with open(gold_sql_path, 'r')as f:
        lines = f.readlines()
    gold_sql_list = [s.split('\t---- db_id ----\t')[0].strip() for s in lines]
    db_place_list = [s.split('\t---- db_id ----\t')[1].strip() for s in lines]
    
    # 执行 sql
    res_list = []
    for index, _ in enumerate(pre_sql_list):
        db_path_4_sql = f'{db_path}/{db_place_list[index]}/{db_place_list[index]}.sqlite'
        # 执行 pre_sql
        pre_output = execute_sql_with_timeout(pre_sql_list[index], db_path_4_sql)
        if pre_output == "Error: timeout":
            res_list.append(-2)
        elif pre_output == "Error: unexcutable":
            res_list.append(-1)
        else:
            #执行 gold_sql
            gold_output = execute_sql_with_timeout(gold_sql_list[index], db_path_4_sql)
            # print(f'----pre_-----{pre_output}')
            # print(f'----pre_-----{gold_output}')
            # 比较执行结果 ？这个是不是有点太严格了？
            if set(gold_output) == set(pre_output):
                res_list.append(1)
            else:
                res_list.append(0)

    return res_list


# Next -> 并行执行