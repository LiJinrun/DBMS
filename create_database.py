import pandas as pd
import os
from permission import check_permission

def create_db(dbname):  # 创建数据库，其实就是创建一个xlsx文件
    create_tb_in_tb_info(dbname)  # 创建table_information.xlsx
    db_path = 'data/' + dbname + '.xlsx'
    columns = ['database', 'select', 'insert', 'delete', 'update', 'use']
    first_line = [dbname, 'root', 'root', 'root', 'root', 'root']
    permission = pd.DataFrame([first_line], columns=columns)
    permission.to_excel(db_path, sheet_name='permission', index=False)

    write = pd.ExcelWriter(db_path, mode='a', engine='openpyxl')
    view_sql = pd.DataFrame(columns=['viewname', 'sql'])
    view_sql.to_excel(write, sheet_name='viewname_sql', index=False)
    write.save()
    print(u"数据库创建操作执行成功")


def create_tb_in_tb_info(dbname):  # 在table_infomation中创建数据库对应的表, 每一个数据库对应一个sheet
    table = pd.DataFrame(columns=['table', 'column_name', 'type', 'null', 'unique', 'primary_key', 'foreign_key'])
    if os.path.exists('data/table_information.xlsx'):
        write = pd.ExcelWriter('data/table_information.xlsx', mode="a", engine="openpyxl")
        table.to_excel(write, sheet_name=dbname, index=False)
        write.save()
    else:
        table.to_excel('data/table_information.xlsx', sheet_name=dbname, index=False)
