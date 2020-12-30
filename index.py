import pandas as pd
import os


def create_index(sql, dbname, operate='create'):
    # dbname = 'mydb'
    # sql = 'create index idxsname on student(sname)'
    sql_words = sql.split()
    left = sql_words[-1].index('(')
    table_name = sql_words[-1][:left]
    column = sql_words[-1][left + 1:-1]

    if not os.path.exists('data/index/' + dbname):
        os.makedirs('data/index/' + dbname)

    write = pd.ExcelWriter(r'data/index/' + dbname + '/' + table_name + '.xlsx', mode='a', engine="openpyxl")
    wb = write.book
    try:
        if operate != 'create':
            wb.remove(wb[column])
        table = pd.read_excel('data/' + dbname + '.xlsx', sheet_name=table_name, dtype=str)
        data = table[column]
        index = dict()
        for i, item in enumerate(data):
            index[str(item)] = ''
        for i, item in enumerate(data):
            item = str(item)
            index[item] += '1'
            for j in index:
                if j != item:
                    index[j] += '0'
        key = list(index.keys())
        bit = list(index.values())
        index_table = pd.DataFrame({'key': key, 'bit': bit})

        index_table.to_excel(write, sheet_name=column, index=False)
        write.save()
        if operate == 'create':
            print('索引创建成功')
    except:
        pass


def modify_index(dbname, table_name, cols):
    for col in cols:
        sql = '*** *** *** on {}({})'.format(table_name, col)
        create_index(sql, dbname, 'update')
