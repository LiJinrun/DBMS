from select import select
import pandas as pd
import os


# create view scview as select * from sc
def create_view(sql, dbname):
    """
    create view scview as select * from sc # 创建视图，并在view.xlsx里存储
    create view studentview as select * from student
    create view test as select * from student
    """
    sql_words = sql.split()
    view_name = 'view_' + sql_words[2]
    db_path = 'data/' + dbname + '.xlsx'
    select_sql = ' '.join(sql_words[4:])

    write = pd.ExcelWriter(db_path, mode='a', engine='openpyxl')
    wb = write.book
    wb.remove(wb['viewname_sql'])

    view_sql = pd.read_excel(db_path, sheet_name='viewname_sql', dtype=str)

    if view_name not in view_sql['viewname']:
        view_sql = view_sql.append(pd.DataFrame([[view_name, sql]], columns=view_sql.columns))
        view_sql.to_excel(write, sheet_name='viewname_sql', index=False)

    table_select = select(select_sql, dbname, return_pd=1, print_table=1)
    table_select.to_excel(write, sheet_name=view_name, index=False)
    write.save()
