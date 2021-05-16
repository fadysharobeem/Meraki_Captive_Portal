## In meraki dashboard you will need to whitelist the host of your captive portal AND *.googleapis.com

import mysql.connector,pprint,requests,os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from syslogclient import SyslogC
from db_mysql import mysql_db
from meraki_data import meraki_users

app = Flask(__name__)
app.config['SECRET_KEY']  = os.urandom(128)
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Placeholder for first time login
dict = {"username":"admin","password":"admin","API":"","Database_password":""}

# Run a Meraki call to capture the APs which the API key has access to
meraki_users.Start(dict['API'])

## check_captive_user_cred function is used to check the username and password of the user against MySQL database
def check_captive_user_cred(username,password):
    # get the list of tables configured to check if Captive is part of it
    db_tables = mysql_db.sql_tables(dict['Database_host'],dict['Database_username'],dict['Database_password'],dict['Database_SQL_name'])
    # Create a Captive table if its not in the list of tables are configured
    if "Captive" not in db_tables:
        print("XXXXXXXXXX Database is not configured XXXXXXXXXX")
        mysql_db.create_sql_captive_tables(dict)

    # Get the user details from the database
    result_dict = mysql_db.user_database(dict['Database_host'],dict['Database_username'],dict['Database_password'],dict['Database_SQL_name'],"Captive")

    if username in result_dict.keys():
        if password == str(result_dict[username]["password"]):
            print("User is successfully authenticated")
            return "passed",result_dict[username]["membership"]
        else:
            print("Password is wrong")
            return "failed",None
    else:
        print("Username can't be found")
        return "failed",None
# Check_cred is a function to verify the provided Admin user credentials against the data stored in dict
def Check_cred(username,password):
    if username == dict['username'].lower():
        if password == dict['password']:
            print("pass")
            return "pass"
        else:
            print("fail")
            return "fail"
    else:
        return "fail"
# Construct the Syslog message before sendin the alert to the server
def constructSyslog(username,clientMAC,clientIP,nodeMAC,state):
    message = f'''Splash_Page_Events Username="{username}" Client_MAC="{clientMAC}" Client_IP="{clientIP}" Node_MAC="{nodeMAC} state="{state}"'''
    return message

def checking_DB_tables():
    db_status = "NOT working"
    # check_sql is to verify if the sql database and credentials are working or not
    check_db = mysql_db.check_sql(dict['Database_host'],dict['Database_username'],dict['Database_password'],dict['Database_SQL_name'])

    if check_db == "passed":
        print(" The database details is correct")
        db_status ="working"

        # Check db tables once the database is reachable and check if the table is provided by user is part of the current list of tables
        db_tables = mysql_db.sql_tables(dict['Database_host'],dict['Database_username'],dict['Database_password'],dict['Database_SQL_name'])
        if dict['Database_Table'] in db_tables:
            print("The table is already configured")
        else:
            print("XXXXXXX The table is not configured XXXXXXX")
            # Creatig the Table in case it wasn't already configured
            mysql_db.create_sql_tables(dict)

        # Check if the users are not configured already if not then add that user
        list_users= mysql_db.sql_get_list_users(dict)
        z = 0
        while z <len(list_users):
            # Delete all users in the table to allow only single user
            mysql_db.sql_delete_user(dict,list_users[z])
            z +=1
        mysql_db.sql_add_new_row(dict)

    else:
        print("Something wrong with the details provided for the database")
        db_status ="NOT working"
    return db_status

##############################################
# this section for Captive Portal users
##############################################
@app.route("/")
def home():
    # print(request)
    session["client_ip"]= request.args.get('client_ip')
    session["client_mac"] = request.args.get('client_mac')
    session["grant_url"] = request.args.get('base_grant_url')
    session["Node_mac"] = request.args.get('node_mac')
    session["user_continue_url"] = request.args.get('user_continue_url')

    print(f"Client IP is: {session['client_ip']} && Client MAC is: {session['client_mac']} && URL is: {session['grant_url']}")
    return render_template("Captive-Portal.html")

@app.route('/good')
def good():
    if not session["grant_url"] == None:
        print("-------- "+ session["grant_url"])
        redirect_url = session["grant_url"]+"?continue="+session["user_continue_url"]
        meraki_users.verify(dict["API"],session['client_mac'],session['username'],session['Node_mac'],session['membership'])
    else:
        redirect_url = "https://meraki.cisco.com"
    # Consturct and send message to Syslog server
    sysMessage = constructSyslog(session["username"],session['client_mac'],session['client_ip'],session['Node_mac'],"Succeed")
    try:
        SyslogC.SendSysLog(sysMessage,dict)
    except:
        print("Issue with Syslog")

    return redirect(redirect_url, code=302)

@app.route('/retry')
def retry():
    return render_template("Captive-Portal.html")

@app.route('/bad')
def bad():
    # Construct and send message to Syslog server
    sysMessage = constructSyslog(session["username"],session['client_mac'],session['client_ip'],session['Node_mac'],"Failed")
    try:
        SyslogC.SendSysLog(sysMessage,dict)
    except:
        print("Issue with Syslog")
    return render_template("Failed.html")

@app.route('/verify', methods=["POST"])
def verify():
    session["username"] = request.form["name"].lower()
    session["password"] = request.form["membership"]
    ## Try to check the user credentials and if it fails, it will redirect the user to the Admin page to check the database
    try:
        session['result'],session["membership"] = check_captive_user_cred(session["username"],session["password"])
    except:
        print("Check if the database is configured")
        return redirect(url_for('Admin'))

    if session['result'] == "passed":
        return redirect(url_for('good'))
    else:
        return redirect(url_for('bad'))

##############################################
# this section for Admin
##############################################
@app.route('/Admin')
def Admin():
    return render_template("Admin.html")

@app.route('/check', methods=['POST'])
def check():
    session["username"] = request.form['username']
    session["password"] = request.form['password']
    print(f'useranme -- {session["username"]} && password -- {session["password"]}')
    result = Check_cred(session["username"].lower(),session["password"] )
    if result == "pass":
        return render_template("Admin-logged.html", Admin_Name=session["username"].upper(),data=dict)
    else:
        return render_template("Failed-Admin.html")

@app.route('/save', methods=["POST"])
def save():
    api= request.form['api']
    if api != '':
        dict['API'] = api

    else:
        pass
    # api_status is a variable to check if Meraki API is correct
    api_status = meraki_users.check_meraki_api(dict['API'])
    print(f"------{api_status}")
    if api_status == "working":
        meraki_users.Start(dict['API'])
    password= request.form['password']
    if password != '':
        dict['password'] = password
    DB_pass= request.form['DB_pass']
    if DB_pass != '':
        dict['Database_password'] = DB_pass

    dict['username']= request.form['username']
    dict['Database_host']= request.form['DB_IP']
    dict['Database_username']= request.form['DBUsername']
    dict['Database_SQL_name']= request.form['DB_sys']
    dict['Database_Table']= request.form['DB_table']
    dict['Syslog_server']= request.form['syslog_ip']
    if request.form['syslog_port'] == "":
        dict['Syslog_port']=514
    else:
        dict['Syslog_port']= request.form['syslog_port']
    # Calling checking_DB_tables to find if its reachable and create the table if not configured
    db_status = checking_DB_tables()

    return render_template("Admin-check.html",Admin_Name=dict["username"].upper(),db_status=db_status,api_status=api_status)

@app.route('/retry_admin')
def retry_admin():
    return render_template("Admin.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000, debug=True)
