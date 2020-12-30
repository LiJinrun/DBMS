import os
import pandas as pd

db_path = 'data/'

'''
输入“help database”命令，输出所有数据表、视图和索引的信息，同时显示其对象类型；

输入“help index 索引名”命令，输出索引的详细信息。
'''
def help(sql, dbname):
    '''
        help database mydb
        help table student
        help view scview
        help index
    '''
    sql_word = sql.split()
    if sql_word[1] == 'database':
        print('所有表的信息如下')
        print(pd.read_excel('data/table_information.xlsx', sheet_name=dbname, dtype=str))
        print('创建视图的命令如下')
        print(pd.read_excel('data/' + dbname + '.xlsx', sheet_name='viewname_sql', dtype=str))
        print('索引的信息如下')
        print('无信息，因为还未创建索引')
    elif sql_word[1] == 'table':
        table_name = sql_word[2]
        print(pd.read_excel('data/' + dbname + '.xlsx', sheet_name=table_name, dtype=str))
        table = pd.read_excel('data/table_information.xlsx', sheet_name=dbname, dtype=str)
        print(table[table['table'] == table_name])
    elif sql_word[1] == 'view':
        view_name = 'view_'+sql_word[2]
        view_sql = pd.read_excel('data/'+dbname+'.xlsx', sheet_name='viewname_sql')
        print(view_sql[view_sql['viewname'] == view_name]['sql'].values[0])
