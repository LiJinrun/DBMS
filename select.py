import pandas as pd
import re
from permission import check_permission

def select(user, sql, dbname, return_pd=0, print_table=1):
    sql_words = sql.split()
    # select sno,cno from student,sc where student.sno=sc.sno   		     # 连接查询
    if '.' in sql_words[-1] and '=' in sql_words[-1]:
        check_permission(user, sql_words[1], 'select')
        select_cols = sql_words[1].split(',')
        sheet_name1, sheet_name2 = sql_words[3].split(',')
        merge_col = sql_words[-1].split('=')[-1].split('.')[-1]  # merge_col就是判断值相等的列
        table1 = pd.read_excel('data/' + dbname + '.xlsx', sheet_name=sheet_name1, dtype=str)
        table2 = pd.read_excel('data/' + dbname + '.xlsx', sheet_name=sheet_name2, dtype=str)
        if select_cols == ['*']:
            select_pd = pd.merge(table1, table2, on=merge_col)
        else:
            select_pd = pd.merge(table1, table2, on=merge_col)[select_cols]
    # select * from student where sno between 1 and 4
    elif 'between' in sql:
        select_cols = sql_words[1].split(',')
        sheet_name = sql_words[3]
        table = pd.read_excel('data/' + dbname + '.xlsx', sheet_name=sheet_name, dtype=str)
        col, start, end = sql_words[-5], sql_words[-3], sql_words[-1]
        if select_cols == ['*']:
            select_pd = table[(table[col] >= start) & (table[col] <= end)]
        else:
            select_pd = table[(table[col] >= start) & (table[col] <= end)][select_cols]
    # select * from student order by sno desc # ORDER BY
    elif 'order by' in sql:
        if sql_words[-1] == 'desc':  # 降序
            ascending = False
        else:
            ascending = True
        order_by_col = sql_words[6]
        select_cols = sql_words[1].split(',')
        sheet_name = sql_words[3]
        table = pd.read_excel('data/' + dbname + '.xlsx', sheet_name=sheet_name, dtype=str)
        if select_cols == ['*']:
            select_pd = table.sort_values(order_by_col, ascending=ascending)
        else:
            select_pd = table.sort_values(order_by_col, ascending=ascending)[select_cols]
    # select * from student where sno=1 and sname=zhangsan
    elif 'and' in sql:
        select_cols = sql_words[1].split(',')
        sheet_name = sql_words[3]
        table = pd.read_excel('data/' + dbname + '.xlsx', sheet_name=sheet_name, dtype=str)
        col1, val1 = sql_words[5].split('=')
        col2, val2 = sql_words[7].split('=')
        if select_cols == ['*']:
            select_pd = table[(table[col1] == val1) & (table[col2] == val2)]
        else:
            select_pd = table[(table[col1] == val1) & (table[col2] == val2)][select_cols]
    # select * from student where sno=1 or sno=2
    elif 'or' in sql:
        select_cols = sql_words[1].split(',')
        sheet_name = sql_words[3]
        table = pd.read_excel('data/' + dbname + '.xlsx', sheet_name=sheet_name, dtype=str)
        col1, val1 = sql_words[5].split('=')
        col2, val2 = sql_words[7].split('=')
        if select_cols == ['*']:
            select_pd = table[(table[col1] == val1) | (table[col2] == val2)]
        else:
            select_pd = table[(table[col1] == val1) | (table[col2] == val2)][select_cols]
    # select * from student where sname like zhang%
    elif 'like' in sql:
        col = sql_words[-3]
        values = sql_words[-1][:-1]  # zhang
        regex = re.compile("^" + values + ".*")
        sheet_name = sql_words[3]
        table = pd.read_excel('data/' + dbname + '.xlsx', sheet_name=sheet_name, dtype=str)
        select_index = []
        for i, s in enumerate(table[col]):
            if bool(regex.match(s)):
                select_index.append(i)
        select_pd = table.iloc[select_index]
    # sql = 'select * from sc where cno=1 except select * from sc where cno=2' 集合查询
    elif 'union' in sql or 'intersect' in sql or 'except' in sql:
        key = 'union' if 'union' in sql else 'intersect' if 'intersect' in sql else 'except'
        key_index = sql_words.index(key)
        sql_words1 = sql_words[:key_index]
        sql_words2 = sql_words[key_index + 1:]
        # 把上一个条件里的代码copy两遍即可，最后再连接到一起
        select_cols = sql_words1[1].split(',')
        sheet_name = sql_words1[3]
        table = pd.read_excel('data/' + dbname + '.xlsx', sheet_name=sheet_name, dtype=str)
        limit_col, limit_val = sql_words1[-1].split('=')
        table = table[table[limit_col] == limit_val]
        if select_cols == ['*']:
            select_pd1 = table
        else:
            select_pd1 = table[select_cols]
        ###################
        select_cols = sql_words2[1].split(',')
        sheet_name = sql_words2[3]
        table = pd.read_excel('data/' + dbname + '.xlsx', sheet_name=sheet_name, dtype=str)
        limit_col, limit_val = sql_words2[-1].split('=')
        table = table[table[limit_col] == limit_val]
        if select_cols == ['*']:
            select_pd2 = table
        else:
            select_pd2 = table[select_cols]
        ###################
        # 并集
        if key == 'union':
            select_pd = pd.merge(select_pd1, select_pd2, on=select_pd1.columns.tolist(), how='outer')
        # 交集
        elif key == 'intersect':
            select_pd = pd.merge(select_pd1, select_pd2, on=select_pd1.columns.tolist())
        # 差集
        else:
            select_pd = pd.concat([select_pd1, select_pd2]).drop_duplicates()
            select_pd = pd.concat([select_pd1, select_pd2]).drop_duplicates(keep=False)
    # select sno,count(cno) from sc group by sno having count(cno)>3
    #elif re.match('.*group by.*having count.*', sql):
    elif re.match('.*group by.*having.*', sql):
        sheet_name = sql_words[3]
        group_by_col = sql_words[6]
        count_col = re.findall('\(.*\)', sql_words[-1])[0].strip('()')
        count_bound = int(re.findall('\d', sql_words[-1])[0])
        table = pd.read_excel('data/'+dbname+'.xlsx', sheet_name=sheet_name, dtype=str)
        if 'count' in sql:
            group_by_table = table.groupby(group_by_col).count()
        elif 'sum' in sql:
            group_by_table = table.groupby(group_by_col).sum()
        elif 'avg' in sql:
            group_by_table = table.groupby(group_by_col).mean()
        elif 'max' in sql:
            group_by_table = table.groupby(group_by_col).max()
        elif 'min' in sql:
            group_by_table = table.groupby(group_by_col).min()
        group_by_table.columns = ['count(%s)' % count_col]
        select_pd = group_by_table[group_by_table['count(%s)' % count_col] > count_bound].reset_index()
    # 嵌套查询 select sno,sname from student where sno in(select sno from sc)
    elif re.match('select.*in\(select.*', sql):
        sheet_name = sql_words[3]
        table = pd.read_excel('data/' + dbname + '.xlsx', sheet_name=sheet_name, dtype=str)
        nest_sql = re.findall('\(.*\)',sql)[0].strip('()')
        values = select(user, nest_sql, dbname, return_pd=0, print_table=0)
        values = [value[0] for value in values]
        col = sql_words[5]
        select_cols = sql_words[1].split(',')
        if select_cols == ['*']:
            select_pd = table[table[col].isin(values)]
        else:
            select_pd = table[table[col].isin(values)][select_cols]
    # select sno,sname from student
    elif len(sql_words) == 4:
        """
        select * from sc
        select sno from student
        """
        select_cols = sql_words[1].split(',')
        sheet_name = sql_words[3]
        table = pd.read_excel('data/'+dbname+'.xlsx', sheet_name=sheet_name, dtype=str)
        if select_cols == ['*']:
            select_pd = table
        else:
            select_pd = table[select_cols]
    # select * from student where sno=1
    elif len(sql_words) == 6:
        select_cols = sql_words[1].split(',')
        sheet_name = sql_words[3]
        table = pd.read_excel('data/' + dbname + '.xlsx', sheet_name=sheet_name, dtype=str)
        limit_col, limit_val = sql_words[-1].split('=')
        table = table[table[limit_col] == limit_val]
        if select_cols == ['*']:
            select_pd = table
        else:
            select_pd = table[select_cols]
    if print_table == 1:
        print(select_pd)
    if return_pd == 1:
        return select_pd
    else:
        return select_pd.values.tolist()

