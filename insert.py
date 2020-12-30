import pandas as pd
import re
from select import select
from check import check_Constraint
from index import modify_index

db_path = 'data/'


def insert(sql, dbname, change_index=False):
    """
    insert into sc(sno,cno) values(2,NULL)  # 单个插入
    insert into sc(sno,cno) values(1,2),(3,4),(5,6),(7,8)
    insert into student(sno,sname) values(4,liuneng),(5,zhaosi)
    insert into sc(sno) select sno from student  # 带子查询插入
    """
    sql_words = sql.split()
    left, right = sql_words[2].find('('), sql_words[2].find(')')
    table_name = sql_words[2][:left]
    table = pd.read_excel('data/' + dbname + '.xlsx', sheet_name=table_name, dtype=str)
    cols = sql_words[2][left + 1:right].split(',')
    if sql_words[3] != 'select':
        p = re.compile(r'[(](.*?)[)]', re.S)
        insert_values = [value.split(',') for value in re.findall(p, sql_words[3])]
        insert_pd = pd.DataFrame(insert_values, columns=table.columns)
        # insert_values =  [['4', 'liuneng'], ['5', 'zhaosi']]
    else:
        select_sql = ' '.join(sql_words[3:])  # select sno from student
        insert_values = select(select_sql, dbname, print_table=0)
        col_val = dict(zip(table.columns, zip(*insert_values)))
        insert_pd = pd.DataFrame(col_val, columns=table.columns)
    # # （唯一和非空）检查
    # print(insert_pd)
    # s = insert_pd.notna().all()
    # null_col = s[s.values == False].index
    # s = insert_pd.nunique().drop(labels=null_col)
    # notunique_col = s[s.values < len(insert_pd)].index
    # check_db = pd.read_excel('data/table_information.xlsx', sheet_name=dbname, dtype=str)
    # check_table = check_db[check_db['table'] == table_name]
    # indexs = check_table['column_name'].isin(null_col)
    # if len(null_col) and check_table[indexs]['null'].values[0] == '0':
    #     print('不允许出现空值')
    #     return
    # indexs = check_table['column_name'].isin(notunique_col)
    # if len(notunique_col) and '1' in check_table[indexs]['unique'].values:
    #     print('不允许出现重复值')
    #     return

    # 保存
    write = pd.ExcelWriter(r'data/' + dbname + '.xlsx', mode="a", engine="openpyxl")
    wb = write.book
    wb.remove(wb[table_name])
    table = table.append(insert_pd, ignore_index=True)
    check_Constraint(dbname, table, table_name)  # 检查非空、唯一、数据类型等完整性约束
    table.to_excel(write, sheet_name=table_name, index=False)
    try:
        write.save()
        print('表' + table_name + '添加了%d个元组' % len(insert_pd))
        # 更新索引

    except:
        print('数据库正在被其他进程使用，无法修改，请关闭后再修改')
    if change_index:
        modify_index(dbname, table_name, cols)
