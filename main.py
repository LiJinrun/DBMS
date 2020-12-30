from create_database import create_db
from create_table import create_table
from create_view import *
from index import *
from insert import insert
from permission import set_permission, del_permission, check_permission
from check import check_user
from delete import delete
from select import select
from update import update
from help import help


using_dbname = ''
db_path = 'data/'
user = ''
change_index = False

def welcome():
    """
    欢迎界面/字符画
    :return:
    """
    print("""
          ##############################################

                      _____  ____  __  __  _____ 
                     |  __ \|  _ \|  \/  |/ ____|
                     | |  | | |_) | \  / | (___  
                     | |  | |  _ <| |\/| |\___ \ 
                     | |__| | |_) | |  | |____) |
                     |_____/|____/|_|  |_|_____/ 

                    -> exit/quit:退出 help:语法帮助 <-

          ##############################################
          """)


def login():
    global user
    print("Please Login:")
    username = input("username: ")
    password = input("password: ")
    #username = password = 'root'
    if check_user(username, password):
        print("Login Success! Welcome {}!".format(username))
        user = username
    else:
        print("User not exist or password is wrong! Please try again.")
        login()


def get_command():
    """
    从控制台获取命令
    :return: None
    """
    command = input("{}>>> ".format(user)) if not using_dbname else input("{}[{}]> ".format(user, using_dbname))
    return command.strip()


def use_db(dbname):
    global using_dbname
    using_dbname = dbname
    print("Database changed.")


def query(sql):
    global change_index
    sql_word = sql.replace("'", '').split(" ")
    if len(sql_word) < 2:
        print("[!]命令输入错误，请检查!")
        return
    operate = sql_word[0].lower()
    if operate == 'use':
        try:
            use_db(sql_word[2])
        except:
            print("[!]权限不足")
    elif operate == 'create':
        check_permission(user, sql_word[1], operate)
        if sql_word[1] == 'database':
            create_db(sql_word[2])
        elif sql_word[1] == 'table':
            create_table(sql, using_dbname)
        elif sql_word[1] == 'view':  # creat view test1 as select * from user
            create_view(sql, using_dbname)
        elif sql_word[1] == 'index':
            change_index = True
            create_index(sql, using_dbname)
        else:
            print("[!]只能创建database、table、view、index，请检查输入的命令.")
    elif operate == 'select':
        select(user, sql, using_dbname)
    elif operate == 'grant':
        set_permission(user, sql)
    elif operate == 'revoke':
        del_permission(sql)
    elif operate == 'insert':
        check_permission(user, using_dbname, 'insert')
        insert(sql, using_dbname, change_index=change_index)
    elif operate == 'update':
        check_permission(user, using_dbname, 'update')
        update(sql, using_dbname)
    elif operate == 'delete':
        check_permission(user, using_dbname, 'delete')
        delete(sql, using_dbname)
    elif operate == 'help':
        help(sql, using_dbname)
    else:
        print("[!]Syntax Error.")


def run():
    global user
    welcome()
    login()
    while True:
        command = get_command()
        if command == 'quit' or command == 'exit':
            if user != 'root':
                print('用户{}退出，当前为root'.format(user))
                user = 'root'
            else:
                print("谢谢使用~~")
                exit(0)
        elif command == 'setuser':
            if user == 'root':
                login()
            else:
                print('用户权限不足，请输入quit/exit退出当前用户，回到root以获得最高权限')
        else:
            query(command)


if __name__ == '__main__':
    run()
