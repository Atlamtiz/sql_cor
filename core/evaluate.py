import sqlite3
from concurrent.futures import ThreadPoolExecutor, TimeoutError, as_completed


def execute_sql(sql, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as e:
        return "Error: unexcutable"  # -1
    finally:
        conn.close()


def execute_sql_with_timeout(sql, db_path, timeout=10):
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(execute_sql, sql, db_path)
        try:
            result = future.result(timeout=timeout)
        except TimeoutError:
            result = "Error: timeout"  # -2
    return result


def ex_evaluation(pre_sql_path, gold_sql_path, db_path):
    # 读入文件
    with open(pre_sql_path, 'r') as f:
        pre_sql_list = [s.strip() for s in f.readlines()]

    with open(gold_sql_path, 'r') as f:
        lines = f.readlines()
    gold_sql_list = [s.split('\t---- db_id ----\t')[0].strip() for s in lines]
    db_place_list = [s.split('\t---- db_id ----\t')[1].strip() for s in lines]

    # 结果列表初始化
    res_list = [-1] * len(pre_sql_list)

    # 执行 SQL 的任务
    with ThreadPoolExecutor() as executor:
        futures = []
        for index, sql in enumerate(pre_sql_list):
            db_path_4_sql = f'{db_path}/{db_place_list[index]}/{db_place_list[index]}.sqlite'
            future = executor.submit(execute_sql_with_timeout, sql, db_path_4_sql)
            futures.append((index, future, db_path_4_sql))

        # 处理并行任务的结果
        for index, future, db_path_4_sql in futures:
            try:
                pre_output = future.result()
                if pre_output == "Error: timeout":
                    res_list[index] = -2
                elif pre_output == "Error: unexcutable":
                    res_list[index] = -1
                else:
                    # 执行 gold_sql
                    gold_output = execute_sql_with_timeout(gold_sql_list[index], db_path_4_sql)

                    # 比较执行结果
                    if set(gold_output) == set(pre_output):
                        res_list[index] = 1
                    else:
                        res_list[index] = 0
            except Exception as e:
                res_list[index] = -1  # 捕获其他异常情况

    return res_list
