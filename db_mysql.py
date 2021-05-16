import mysql.connector,socket,time
class mysql_db:

    def user_database(Host,User,Password,Database_SQL_name,Database_table):
        mydb = mysql.connector.connect(
        host=Host,
        user=User,
        passwd=Password,
        database=Database_SQL_name
        )
        mycursor = mydb.cursor()
        query = "SELECT * FROM "+Database_SQL_name+"."+Database_table
        mycursor.execute(query)
        data = mycursor.fetchall()
        dict = {}
        x = 0
        while x < len(data):
            username = data[x][0].lower()
            dict[username]={}
            dict[username]["password"]= data[x][1]
            dict[username]["membership"] = data[x][2]
            x+=1

        mycursor.close()
        mydb.close()
        ##return the dict variable where all the user infomation got extracted out from the MySQL database
        ## Sample of Dict outcome is:
        ### dict = {user1: {"password":"xyz","membership":"gold"}, user2: {"password":"xyz","membership":"silver"} }
        return dict

    def admin_database(Host,User,Password,Database_SQL_name,Database_table):
        mydb = mysql.connector.connect(
        host=Host,
        user=User,
        passwd=Password,
        database=Database_SQL_name
        )
        mycursor = mydb.cursor()
        query = "SELECT * FROM "+Database_SQL_name+"."+Database_table
        mycursor.execute(query)
        data = mycursor.fetchall()

        dict = {}
        dict["username"]=data[0][0].lower()
        dict["password"]= data[0][1]
        dict["API"] = data[0][2]
        dict["Database_host"] = data[0][3]
        dict["Database_username"] = data[0][4]
        dict["Database_password"] = data[0][5]
        dict["Database_SQL_name"] = data[0][6]
        dict["Database_Table"] = data[0][7]
        dict["Syslog_server"] = data[0][8]
        dict["Syslog_port"] = data[0][8]
        print(dict)
        mycursor.close()
        mydb.close()
        ##return the dict variable where all the user infomation got extracted out from the MySQL database
        ## Sample of Dict outcome is:
        ### dict = {user1: {"password":"xyz","membership":"gold"}, user2: {"password":"xyz","membership":"silver"} }
        return dict

    # Check if the Database is reachable
    def check_sql(Host,User,Password,Database_SQL_name):
        try:
            mydb = mysql.connector.connect(
              host=Host,
              user=User,
              password=Password,
              database=Database_SQL_name
            )
            if (mydb):
                mydb.close()
                return "passed"
        except:
            return "failed"

    # Check the Tables that part of the database
    def sql_tables(Host,User,Password,Database_SQL_name):
        list_tables= []
        mydb = mysql.connector.connect(
          host=Host,
          user=User,
          password=Password,
          database=Database_SQL_name
        )
        mycursor = mydb.cursor()
        query = f"USE {Database_SQL_name}"
        mycursor.execute(query)
        mycursor.execute("SHOW TABLES")
        myresult = mycursor.fetchall()
        # print(myresult)
        x = 0
        while x < len(myresult):
            list_tables.append(myresult[x][0])
            x +=1

        mycursor.close()
        mydb.close()
        return list_tables

    # Create a database table
    def create_sql_tables(dict):
        mydb = mysql.connector.connect(
        host=dict['Database_host'],
        user=dict['Database_username'],
        password=dict['Database_password'],
        database=dict['Database_SQL_name'])
        mycursor = mydb.cursor()
        query = f"CREATE TABLE {dict['Database_Table']} (username VARCHAR(45), password VARCHAR(45), API VARCHAR(45), Database_host VARCHAR(45), Database_username VARCHAR(45), Database_password VARCHAR(45), Database_SQL_name VARCHAR(45), Database_Table VARCHAR(45), Syslog_server VARCHAR(45), Syslog_port INT(45))"
        result = mycursor.execute(query)
        print(f"New table -> {dict['Database_Table']} has been created")
        mycursor.close()
        mydb.close()

    def create_sql_captive_tables(dict):
        mydb = mysql.connector.connect(
        host=dict['Database_host'],
        user=dict['Database_username'],
        password=dict['Database_password'],
        database=dict['Database_SQL_name'])
        mycursor = mydb.cursor()
        query = f'''CREATE TABLE Captive (name VARCHAR(45), membership VARCHAR(45), the_group VARCHAR(45))'''
        result = mycursor.execute(query)
        print(f"New table -> Captive has been created")
        mycursor.close()
        mydb.close()

    def sql_add_new_row(dict):
        mydb = mysql.connector.connect(
        host=dict['Database_host'],
        user=dict['Database_username'],
        password=dict['Database_password'],
        database=dict['Database_SQL_name'])
        mycursor = mydb.cursor()
        list_column= []
        for data in dict:
            list_column.append(data)
        x = 0
        while x < len(list_column):
            if x == 0:
                header_column = f"({list_column[x]}, "
                data_column = f"('{dict[list_column[x]]}', "
                x +=1
            if x == len(list_column)-1:
                header_column += f"{list_column[x]})"
                data_column += f"{dict[list_column[x]]})"
                x +=1
            else:
                header_column += f"{list_column[x]}, "
                data_column += f"'{dict[list_column[x]]}', "
                x +=1

        query = f'''INSERT INTO {dict['Database_Table']} {header_column} VALUES {data_column};'''
        print(query)
        result = mycursor.execute(query)
        mydb.commit()
        mycursor.close()
        mydb.close()

    def sql_get_list_users(dict):
        mydb = mysql.connector.connect(
        host=dict['Database_host'],
        user=dict['Database_username'],
        password=dict['Database_password'],
        database=dict['Database_SQL_name'])
        mycursor = mydb.cursor()
        list_users= []
        query = f"""SELECT username FROM {dict['Database_Table']}"""
        mycursor.execute(query)
        result = mycursor.fetchall()
        x = 0
        while x < len(result):
            list_users.append(result[x][0])
            x +=1
        print(list_users)
        mycursor.close()
        mydb.close()
        return list_users

    def sql_delete_user(dict,username):
        mydb = mysql.connector.connect(
        host=dict['Database_host'],
        user=dict['Database_username'],
        password=dict['Database_password'],
        database=dict['Database_SQL_name'])
        mycursor = mydb.cursor()
        list_users= []
        query = f"""DELETE FROM {dict['Database_Table']} WHERE username = '{username}' """
        mycursor.execute(query)
        mydb.commit()
        mycursor.close()
        mydb.close()
