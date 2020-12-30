import pandas as pd
import re
from index import modify_index
from check import check_Constraint


def update(sql, dbname, change_index=False):
    '''
        update student set sname=ljr where sno=1
        update student set sname=sno_and_sname where sno=1 and sname=zhangsan
        update student set sname=sno_is1or2 where sno=1 or sno=2
        update student set sname=sno_[1,2] where sno between 1 and 4
        update student set sname=sno_is1or2 where sno in (1,2)
        update student set sname=lisan where sname like zhao%          # 所有姓zhang的
    '''

    sql_words = sql.split()
    table_name = sql_words[1]
    table = pd.read_excel('data/' + dbname + '.xlsx', sheet_name=table_name, dtype=str)
    cols = table.columns
    write = pd.ExcelWriter(r'data/' + dbname + '.xlsx', mode="a", engine="openpyxl")
    wb = write.book
    wb.remove(wb[table_name])
    update_col, update_val = sql_words[3].split('=')
    where_sql = sql_words[5:]
    if len(where_sql) == 1:  # 只有一个约束
        col, val = where_sql[0].split('=')
        update_index = table[table[col] == val].index.tolist()
    else:  # 有关键字 and or 等等
        if where_sql[1] == 'and':
            col1, val1 = where_sql[0].split('=')
            col2, val2 = where_sql[2].split('=')
            update_index = table[(table[col1] == val1) & (table[col2] == val2)].index.tolist()
        elif where_sql[1] == 'or':
            col1, val1 = where_sql[0].split('=')
            col2, val2 = where_sql[2].split('=')
            update_index = table[(table[col1] == val1) | (table[col2] == val2)].index.tolist()
        elif where_sql[1] == 'between':  # 提取区间内的index
            col = where_sql[0]
            start, end = where_sql[2], where_sql[4]
            update_index = table[(table[col] >= start) & (table[col] <= end)].index.tolist()
        elif where_sql[1] == 'in':
            col = where_sql[0]
            values = where_sql[2].strip('()').split(',')
            update_index = table[table[col].isin(values)].index.tolist()
        elif where_sql[1] == 'like':
            col = where_sql[0]
            values = where_sql[2][:-1]  # zhang
            regex = re.compile("^" + values + ".*")
            update_index = []
            for i, s in enumerate(table[col]):
                if bool(regex.match(s)):
                    update_index.append(i)

    table.loc[update_index, update_col] = update_val
    check_Constraint(dbname, table, table_name)  # 检查非空、唯一、数据类型等完整约束
    table.to_excel(write, sheet_name=table_name, index=False)
    try:
        write.save()
        print('表' + table_name + '修改了%d个元组' % len(update_index))
        print('修改后的表', table_name, '如下')
        print(pd.read_excel('data/' + dbname + '.xlsx', sheet_name=table_name, dtype=str))
        # 更新索引

    except:
        print('数据库正在被其他进程使用，无法修改，请关闭后再修改')
    if change_index:
        modify_index(dbname, table_name, cols)