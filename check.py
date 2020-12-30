import re
import pandas as pd
import numpy as np

def check_user(username, password):
    table = pd.read_excel("data/account.xlsx", sheet_name='user')
    try:
        pos = table[table['username'] == username].index.tolist()[0]
    except:
        return False
    right_pswd = table.iloc[pos]['password']
    if password == right_pswd:
        return True
    else:
        return False


# 检查约束
def check_Constraint(using_dbname, check_pd, tablename):  # insert={'sno':'1'}
    table = pd.read_excel("data/table_information.xlsx", sheet_name=using_dbname)
    insert_table = table[table['table'] == tablename]
    index = insert_table.index.tolist()
    for insert_col in check_pd:
        insert_values = check_pd[insert_col]
        for insert_value in insert_values:
            for i in index:
                column_name, typee, is_null, unique, pk, fk = table.iloc[i][1:]
                if is_null == 0:  # 不可以为空
                    if insert_value == '':
                        return False
                if unique == '1':  # 不能有重复的
                    if not check_unique(using_dbname, tablename, insert_col, insert_value):
                        return False
                if pk == '1':
                    if not check_unique(using_dbname, tablename, insert_col, insert_value) or insert_value == '':
                        return False
                elif not fk is np.NaN:  # 该属性列有外键约束
                    if not check_foreign_key_in_primary_key(using_dbname,fk,column_name,insert_value):
                        return False
                if '[' in typee:  # 说明有长度限制
                    typee, maxlen = re.findall(r'(\w*)\[(\d*)\]', typee)[0]  # int[10] => int,10
                else:  # 否则长度无所谓，默认不超过1000
                    maxlen = 1000
                if len(insert_value) > int(maxlen):
                    return False
                if typee == 'int':
                    if type(insert_value) != type(1):
                        return False
                if typee == 'float':
                    if type(insert_value) != type(1.0):
                        return False
                if typee == 'char':
                    if type(insert_value) != type('c'):
                        return False
    return True


def check_foreign_key_in_primary_key(db_name, foreign_key_name, column_name, check_value):
    data = pd.read_excel('data/' + db_name + '.xlsx', sheet_name=foreign_key_name, dtype=str)
    if check_value in data[column_name].tolist():
        return True
    else:
        return False

def check_unique(using_dbname, tablename, insert_col, insert_value):
    table = pd.read_excel("data/" + using_dbname + ".xlsx", sheet_name=tablename)
    if list(table[insert_col]).count(insert_value) > 0:
        return False
    else:
        return True
