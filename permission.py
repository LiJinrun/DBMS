import pandas as pd
import re


# grant use on mydb for admin
def set_permission(from_user, sql):
    '''
    grant create on database to ljr
    grant select on table student to ljr
    grant all privileges on table student to ljr
    grant update(sno) on table student to ljr
    grant insert on table sc to ljr with grant option
    切换到ljr用户后检查执行grant insert on table sc to zhangsan可以检查是否具有转授权功能
    '''
    table_privilege = pd.read_excel('data/privilege.xlsx', dtype=str)
    sql_words = sql.split()
    item = {'from_user': [from_user]}  # 要插入一条权限记录
    ############################################################################################
    to_user = sql_words[sql_words.index('to') + 1]  # 目标用户 ljr
    item['to_user'] = [to_user]
    ############################################################################################
    object = sql_words[sql_words.index('on') + 1]  # 操作的对象类型（数据库级别，表级别，还是属性列级别？）
    if object == 'database':  # 说明是对数据库级别的权限
        item['object_name'] = ['database']
    elif object == 'table':  # 说明不是数据库级别的权限，但具体是表还是属性列还不清楚，暂且认为是表
        table_name = sql_words[sql_words.index('table') + 1]
        item['object_name'] = ['table:' + table_name]  # table: 表明是表级别的
    ############################################################################################
    action = sql_words[1]  # 赋予的操作
    if len(re.findall('\(.*\)', action)) > 0:  # 说明是属性列级别的权限
        col = re.findall('\(.*\)', action)[0].strip('()')
        item['object_name'] = ['column:{}.{}'.format(table_name, col)]  # 例如column:student.sno 表示是对属性列级别的
        action = re.findall('.*\(', action)[0].strip('(')
        item['action'] = [action]
    else:  # 说明不是属性列级别的权限，直接把相应的操作存下来即可，有可能是all，有可能是具体到select等
        item['action'] = [action]
    ############################################################################################
    if 'with grant option' in sql:  # 判断被赋予权限的用户是否有权限将被赋予的操作转授权
        item['sublicense'] = ['1']
    else:
        item['sublicense'] = ['0']
    ############################################################################################
    # 要记录的一条权限已经全部组织完成，接下来判断当前用户是否有权限执行本次操作
    if from_user == 'root':  # root完全没问题
        pass
    else:
        # 查询该用户是否有转授权的权利
        table_privilege = pd.read_excel('data/privilege.xlsx', dtype=str)  # 打开存放权限的表
        table_current_user = table_privilege[table_privilege['to_user'] == from_user]  # 找到被授权用户为当前用户的记录
        # 注意考虑user可以转授权对sc的选择，但不可以转授权对student的插入这种情况，所以必须严格匹配
        if table_current_user[
            (table_current_user['action'] == item['action'][0]) &
            (table_current_user['object_name'] == item['object_name'][0])
        ]['sublicense'].values[0] != '1':
            print('该用户无法转授权，请仔细检查授权表')
            return
    table_privilege = table_privilege.append(pd.DataFrame(item))
    table_privilege.to_excel('data/privilege.xlsx', index=False)


# revoke select on test_tb for testuser
def del_permission(sql):
    '''
    revoke create on database from ljr
    revoke update(sno) on table student from ljr
    revoke insert on table sc from public           # public是指收回所有用户对sc的查询权限
    revoke insert on table sc from ljr cascade      # cascade是指将ljr转授权的所有权限收回
    '''
    table_privilege = pd.read_excel('data/privilege.xlsx', dtype=str)
    sql_words = sql.split()
    item = {'from_user': ['root']}
    ############################################################################################
    from_user = sql_words[sql_words.index('from') + 1]  # 目标用户 ljr
    item['to_user'] = [from_user]
    ############################################################################################
    object = sql_words[sql_words.index('on') + 1]  # 操作的对象类型（数据库级别，表级别，还是属性列级别？）
    if object == 'database':  # 说明是对数据库级别的权限
        item['object_name'] = ['database']
    elif object == 'table':  # 说明不是数据库级别的权限，但具体是表还是属性列还不清楚，暂且认为是表
        table_name = sql_words[sql_words.index('table') + 1]
        item['object_name'] = ['table:' + table_name]  # table: 表明是表级别的
    ############################################################################################
    action = sql_words[1]  # 收回的操作
    if len(re.findall('\(.*\)', action)) > 0:  # 说明是属性列级别的权限
        col = re.findall('\(.*\)', action)[0].strip('()')
        item['object_name'] = ['column:{}.{}'.format(table_name, col)]  # 例如column:student.sno 表示是对属性列级别的
        action = re.findall('.*\(', action)[0].strip('(')
        item['action'] = [action]
    else:  # 说明不是属性列级别的权限，直接把相应的操作存下来即可，有可能是all，有可能是具体到select等
        item['action'] = [action]
    item['sublicense'] = '0'  # 默认赋为0，后续会修改
    ############################################################################################
    if from_user == 'public':
        item = table_privilege[(table_privilege['object_name'] == item['object_name'][0]) & (
                    table_privilege['action'] == item['action'][0])]
    ############################################################################################
    if sql_words[-1] == 'cascade':
        item = table_privilege[(table_privilege['object_name'] == item['object_name'][0]) & (
                    table_privilege['action'] == item['action'][0])]
        item = item[(item['to_user'] == from_user) & (item['sublicense'] == '1') | (item['from_user'] == from_user) & (
                    item['sublicense'] == '0')]
    item = pd.DataFrame(item)
    table_privilege = pd.concat([table_privilege, item]).drop_duplicates(keep=False)
    table_privilege.to_excel('data/privilege.xlsx', index=False)


def check_permission(user, object_name, action):
    if user == 'root':
        return
    else:
        privilege = pd.read_excel('data/privilege.xlsx', dtype=str)
        check_rows = privilege[(privilege['to_user'] == user) &
                               (privilege['object_name'] == object_name) &
                               (privilege['action'] == action)]
        if len(check_rows) == 0:  # 说明找不到相关的权限记录
            print('无权限，请检查')

