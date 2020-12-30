import re
import pandas as pd


# create table tbname (id int PK null,user char[10] )
# 创建一个表
def create_table(sql, dbname):
    sql_words = sql.split()
    db_path = 'data/' + dbname + '.xlsx'
    columns_list = re.findall('\((.*)\)', sql)[0].split(',')
    sheet_name = sql_words[2]
    try:  # 说明已经存在
        pd.read_excel(db_path, sheet_name=sheet_name, dtype=str)
        print('数据表已存在，请重新输入')
    except:
        # 写入table_information.xlsx
        table = pd.read_excel('data/table_information.xlsx', sheet_name=dbname, dtype=str)
        write = pd.ExcelWriter('data/table_information.xlsx', mode="a", engine="openpyxl")
        wb = write.book
        wb.remove(wb[dbname])
        length = len(columns_list)  # 表的属性的个数
        i = 0
        columns_names = []
        # 将字段的属性写到table_information库中
        while True:
            if i == length:
                break
            lis = {}
            column = columns_list[i].split()
            #create table sc (sno char[9], cno char[4] not null, foreign key(sno) references student(sno))
            if 'references' in column:  # 说明里面是foreign key(sno) references student(sno)
                j = column.index('references') + 1
                foreign_key = re.findall('\((.*)\)', column[j])[0]  # sno
                reference_table_name = re.findall('(.*)\(', column[j])[0]  # student
                length -= 1
                i -= 1
                index = table[(table['table'] == sheet_name) & (table['column_name'] == foreign_key)].index
                table.loc[index, 'foreign_key'] = reference_table_name
                break
            else:
                lis['table'] = sheet_name
                lis['column_name'] = column[0]
                lis['type'] = column[1]
                columns_names.append(column[0])
            for key in column[2:]:
                if key == 'null':  # 可以为空的
                    lis['null'] = '1'
                elif key == 'not':  # 非空的not null
                    lis['null'] = '0'
                elif key == 'unique':  # 独一无二的
                    lis['unique'] = '1'
                elif key == 'primary':  # 主键
                    lis['primary_key'] = '1'
                break
            table = table.append(lis, ignore_index=True)
            i += 1
        table = table.fillna('NULL')
        table.to_excel(write, sheet_name=dbname, index=False)
        write.save()
        # 写入dbname.xlsx
        write = pd.ExcelWriter('data/'+dbname+'.xlsx', mode='a', engine='openpyxl')
        pd.DataFrame(columns=columns_names).to_excel(write, sheet_name=sheet_name, index=False)
        write.save()
        print(u"数据表创建完成。")
