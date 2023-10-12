from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import datetime
import MySQLdb.cursors
import re


datee = datetime.date.today()

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Arvind@123'
app.config['MYSQL_DB'] = 'banksystem'
app.config['permanent_session_lifetime']=datetime.timedelta(minutes=1)
mysql = MySQL(app)

app.secret_key = 'My key'


@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'LoginID' in request.form and 'Password' in request.form:
        loginid = request.form['LoginID']
        password = request.form['Password']
        cursor = mysql.connection.cursor()
        cursor.execute('select * from Accounts where account_no in (select account_no from account_login_system where login_id = %s and Login_Password = %s)', (loginid, password,))
        account = cursor.fetchone()
        if account: 
            account_no=account[0]
            if account[1]=="verified": 
                session['LoggedIn'] = True
                session.permanent=True
                session['Account_no'] = account_no
                session['password']=password
                return redirect(url_for('profile'))
            elif account[1]=='pending':
                msg='your account is not verified !'
            elif account[1]=='blocked':
                msg='your account has been blocked !'
            else:
                msg="unknown error occured contact to bank manager "+account
                
            
        else:
            msg = 'Incorrect ID/password!'
    return render_template('log.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('LoggedIn', None)
    session.pop('Account_no', None)
    return redirect(url_for('login'))


@app.route('/profile')
def profile():
    if 'LoggedIn' in session:
        cursor = mysql.connection.cursor()
        cursor.execute('select * from Accounts where Account_no = %s', (session['Account_no'],))
        acc = cursor.fetchone()
        return render_template('profile.html', acc=acc)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'Account_name' in request.form and 'Phone_no' in request.form and 'Address' in request.form and 'DOB' in request.form and 'Aadhaar_no' in request.form and 'Voter_ID' in request.form and 'Email' in request.form and 'Password' in request.form:
        account_name = request.form['Account_name']
        phone_no = request.form['Phone_no']
        address = request.form['Address']
        dob = request.form['DOB']
        login_id=request.form['login']
        aadhaar = request.form['Aadhaar_no']
        voter_id = request.form['Voter_ID']
        email = request.form['Email']
        password = request.form['Password']
        account_type=request.form['account_type']
        pancard_no=request.form['pancard_no']
        cursor = mysql.connection.cursor()
        cursor.execute('select * from Accounts where Voter_ID = %s or aadhaar_no = %s or Email = %s', (voter_id, aadhaar, email,))
        account = cursor.fetchone()
        if account:
            msg = 'Account with same details exists!'
            return render_template('register.html', msg=msg)
        if not account_name or not phone_no or not address or not dob or not aadhaar or not voter_id or not email or not password:
            msg = 'Please fill the entire form!'
            return render_template('register.html', msg=msg)
        if len(phone_no) != 10:
            msg = 'Please enter a 10-digit phone number!'
            return render_template('register.html', msg=msg)
        if len(aadhaar) != 12:
            msg = 'Please enter correct Aadhaar number!'
            return render_template('register.html', msg=msg)
        else:
            cursor.execute('insert into Accounts values(default,"pending",%s, 1500, 5, NULL, %s, %s, %s, %s, %s, %s,%s,%s)', (account_name, phone_no, address, dob, aadhaar,voter_id if voter_id else None, email,account_type,pancard_no if pancard_no else None,))
            cursor.execute('insert into Account_login_system values(%s,%s,(select account_no from accounts where aadhaar_no=%s))', (login_id,password,aadhaar,))
            mysql.connection.commit()
            cursor.close()
            msg = 'Registered request send successfully'
            return render_template('register.html', msg=msg)
    return render_template('register.html', msg=msg)


@app.route('/withdraw', methods=['GET', 'POST'])
def withdraw():
    if 'LoggedIn' in session:
        msg = ''
        if request.method == 'POST' and 'Amount' in request.form:
            amount = request.form['Amount']
            user_password=request.form['password']
            amount = int(amount)
            account_no = session['Account_no']
            password=session['password']
            if user_password==password:
                cursor = mysql.connection.cursor()
                z=str(datetime.datetime.now())
                cursor.execute('select * from Accounts where Account_no = %s', (account_no,))
                acc = cursor.fetchone()
                if acc[3] > amount:
                    final_amount = acc[3] - amount
                    cursor.execute('start transaction')
                    cursor.execute('set autocommit=0')
                    cursor.execute('UPDATE Accounts SET Balance = %s WHERE Account_no = %s', (final_amount, account_no,))
                    cursor.execute('Select * from Accounts where Account_no =%s ', (account_no,))
                    a1 = cursor.fetchone()[3]   # balance of account who's account is de
                    if(a1==final_amount):
                        cursor.execute('insert into Transaction_History values("successful",%s,NULL,%s,default,"widraw",%s)',(amount,z,account_no,))
                        mysql.connection.commit()
                        msg = 'Transaction successful'
                    else:
                        cursor.execute('insert into Transaction_History values("successful",%s,NULL,%s,default,"widraw",%s)',(amount,z,account_no,))
                        mysql.connection.rollback()
                        msg = 'Transaction unsucessaful'
                    cursor.close()
                else:
                    msg = 'Insufficient balance!'
            else:
                msg='Incorrect password'
        return render_template('withdraw.html', msg=msg)
    return redirect(url_for('login'))


@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if 'LoggedIn' in session:
        msg = ''
        if request.method == 'POST' and 'Amount' in request.form:
            amount = request.form['Amount']
            amount = int(amount)
            if amount<500:
                msg='Too low ammount deposite minimum 500 '
            elif amount>1000000:
                msg='you can deposite maximum 10 lakh rupee'
            else:
                z=str(datetime.datetime.now())
                account_no = session['Account_no']
                cursor = mysql.connection.cursor()
                cursor.execute('insert into Transaction_History values("pending",%s,NULL,%s,default,"deposite",%s)',(amount,z,account_no,))
                mysql.connection.commit()
                cursor.close()
                msg = 'Deposite request send successfully'
        return render_template('deposit.html', msg=msg)
    return redirect(url_for('login'))


@app.route('/maketransaction', methods=['GET', 'POST'])
def maketransaction():
    if 'LoggedIn' in session:
        msg = ''
        if request.method == 'POST' and 'Amount' in request.form and 'ToAccount_ID' in request.form:
            amount = int(request.form['Amount'])
            toaccount_id = int(request.form['ToAccount_ID'])
            account_no = session['Account_no']
            cursor = mysql.connection.cursor()
            cursor.execute('Select * from Accounts where Account_no =%s ', (account_no,))
            a1 = cursor.fetchone()
            cursor.execute('Select * from Accounts where Account_no =%s ', (toaccount_id,))
            b1 = cursor.fetchone()
            if a1 and b1:
                if a1[0]==b1[0]:
                    msg = 'please enter different account no'
                    return render_template('transaction.html', msg=msg)  
                elif b1[1]=="verified":
                    x = a1[3]
                    y = b1[3]
                    if x >= amount:
                        x = x - amount
                        y = y + amount
                        z = str(datetime.datetime.now())
                        cursor.execute('start transaction')
                        cursor.execute('set autocommit=0')
                        cursor.execute('update Accounts set Balance=%s where Account_no=%s', (y, toaccount_id,))
                        cursor.execute('update Accounts set Balance=%s where Account_no=%s', (x, account_no,))
                        cursor.execute('Select * from Accounts where Account_no =%s ', (account_no,))
                        a2 = cursor.fetchone()[3]   # balance of account who's account is debited
                        cursor.execute('Select * from Accounts where Account_no =%s ', (toaccount_id,))
                        b2 = cursor.fetchone()[3]  # balance of account no who's account is creadited
                        if(x==a2 and y==b2):
                            cursor.execute('insert into Transaction_History values(%s,%s,%s,%s,default,%s,%s)',("verified",amount, toaccount_id, z,"transfer from "+str(account_no)+" to "+str(toaccount_id) ,account_no,))
                            mysql.connection.commit()
                            msg = 'transaction successfully'
                        else:
                            cursor.execute('rollback')
                            cursor.execute('insert into Transaction_History values(%s,%s,%s,%s,default,%s,%s)',("fail",amount, toaccount_id, z,"transfer from "+str(account_no)+" to "+str(toaccount_id) ,account_no,))
                            mysql.connection.commit()
                            msg='transction unsuccessful'
                        cursor.close()
                        return render_template('transaction.html', msg=msg)
                    else:
                        msg = 'insufficient amount '
                        return render_template('transaction.html', msg=msg)
                else:
                    msg = 'account not varified'
                    return render_template('transaction.html', msg=msg)
            else:
                msg = "enter correct account no.s "

        return render_template('transaction.html', msg=msg)
    return redirect(url_for('login'))


@app.route('/loan', methods=['GET', 'POST'])  #appliying for loan
def loan():
    msg = ''
    if 'LoggedIn' in session:
        account_no = session['Account_no']
        if request.method == 'POST':
            z=str(datetime.datetime.now())
            amount=request.form['amount']
            period=request.form['period']
            cursor = mysql.connection.cursor()
            cursor.execute('insert into loan values(12,%s,default,%s,"pending",%s,%s,NULL,NULL)', (amount,account_no,period,z,))
            mysql.connection.commit()
            cursor.close()
            msg="loan request send successfully "
            return render_template('loan.html',msg=msg)
        return render_template('loan.html')
    return redirect(url_for('login'))


@app.route('/loandetails',methods=['GET','POST']) #londetails
def loandetails():
        if 'LoggedIn' in session:
            cursor = mysql.connection.cursor()
            cursor.execute('select Loan_id,loan_status,period,request_date,loan_pass_on,Interest,Amount,amount_passed from loan where account_no = %s', (session['Account_no'],))
            msg = cursor.fetchall()
            return render_template('loandetails.html',msg=msg)
        return render_template('loandetails.html')


@app.route('/transaction_history', methods=['GET', 'POST'])  #list of accounts
def transaction_history():
    msg = ''
    if 'LoggedIn' in session:
        account_no = session['Account_no']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * from transaction_history WHERE account_no=%s or toAccount_ID=%s', (account_no,account_no,))
        account = cursor.fetchall()
        return render_template('transaction_history.html', msg=account)
    return redirect(url_for('login'))


@app.route('/adminlogin', methods=['GET', 'POST'])    #admin log in
def adminlogin():
    msg = ''
    if request.method == 'POST' and 'LoginID' in request.form and 'Password' in request.form:
        loginid = request.form['LoginID']
        password = request.form['Password']
        cursor = mysql.connection.cursor()
        cursor.execute('select * from Admin_login_system where Login_ID = %s and Login_password = %s', (loginid, password,))
        account = cursor.fetchone()
        if account:
            session['Admin_LoggedIn'] = True
            session['Admin_ID'] = account[2]
            return redirect(url_for('adminhome'))
        else:
            msg = 'Incorrect ID/password!'
    return render_template('admin_log.html', msg=msg)


@app.route('/adminhome')    # admin log home page
def adminhome():
    if 'Admin_LoggedIn' in session:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM Admin WHERE Admin_ID = %s', (session['Admin_ID'],))
        acc = cursor.fetchone()
        return render_template('admin_home.html', acc=acc)
    return redirect(url_for('adminlogin'))


@app.route('/adminlogout')
def adminlogout():
    session.pop('Admin_LoggedIn', None)
    session.pop('Admin_ID', None)
    return redirect(url_for('adminlogin'))


@app.route('/query1', methods=['GET', 'POST']) #view details of customer
def query1():
    msg = ''
    if 'Admin_LoggedIn' in session:
        admin_id= session['Admin_ID']
        if request.method == 'POST' and 'Account_no' in request.form:
            account_no = request.form['Account_no']
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * from Accounts WHERE Account_no = %s and admin_id=%s', (account_no,admin_id,))
            account = cursor.fetchall()
            if account:
                return render_template('query1.html', msg=account)
            else:
                msg = 'Account does not exist'
                return render_template('query1.html', msg1=msg)
        return render_template('query1.html', msg1=msg)
    return redirect(url_for('adminlogin'))


@app.route('/query2', methods=['GET', 'POST'])  # blocking an account
def query2():
    msg = ''
    if 'Admin_LoggedIn' in session:
        admin_id= session['Admin_ID']
        if request.method == 'POST' and 'Account_no' in request.form:
            account_no = request.form['Account_no']
            cursor = mysql.connection.cursor()
            cursor.execute('SELECT * from Accounts WHERE Account_no = %s and admin_id=%s', (account_no,admin_id,))
            account = cursor.fetchone()
            if account:
                cursor.execute('update accounts set account_status="blocked" where account_no=%s',(account_no,))
                mysql.connection.commit()
                cursor.close()
                msg="account blocked successfully"
                return render_template('query2.html', msg=msg)
            else:
                msg = 'Account does not exist'
                return render_template('query2.html', msg=msg)
        return render_template('query2.html', msg=msg)
    return redirect(url_for('adminlogin'))


@app.route('/query3', methods=['GET', 'POST'])  #list of accounts
def query3():
    msg = ''
    if 'Admin_LoggedIn' in session:
        admin_id= session['Admin_ID']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * from Accounts WHERE admin_id=%s', (admin_id,))
        account = cursor.fetchall()
        return render_template('query3.html', msg=account)
    return redirect(url_for('adminlogin'))


@app.route('/query4', methods=['GET', 'POST']) #varifying loan status
def query4():
    if 'Admin_LoggedIn' in session:
        admin_id= session['Admin_ID']
        cursor = mysql.connection.cursor()
        date=str(datetime.datetime.now())
        if request.method == 'POST':
            loan_id=request.form['loan_id']
            selectValue = request.form.get('select1')
            val=str(selectValue)
            if val=="Approve":
                amount=int(request.form['amount'])
                if amount>0:
                    cursor.execute('UPDATE loan set loan_status="verified" where loan_id=%s',(loan_id,))
                    cursor.execute('UPDATE loan set amount_passed=%s where loan_id=%s',(amount,loan_id,))
                    cursor.execute('UPDATE loan set loan_pass_on=%s where loan_id=%s',(date,loan_id,))
                    cursor.execute('update accounts set balance=balance+%s where account_no=(select account_no from loan where loan_id=%s)',(amount,loan_id,))
                    mysql.connection.commit()  
            elif val=="Reject":
                cursor.execute('UPDATE loan set loan_status="rejected" where loan_id=%s',(loan_id,))
                mysql.connection.commit() 
        cursor.execute('SELECT * from loan WHERE loan_status="pending" and account_no in (select account_no from accounts where admin_id=%s)',(admin_id,))
        msg = cursor.fetchall()
        cursor.close()
        return render_template('query4.html', msg=msg)
    return redirect(url_for('adminlogin'))


@app.route('/query5', methods=['GET', 'POST'])   #for varifying deposite process
def query5():
    msg=""
    if 'Admin_LoggedIn' in session:
        admin_id = session['Admin_ID']
        cursor = mysql.connection.cursor()
        if request.method == 'POST':
            transaction_id=request.form['transaction_id']
            selectValue = request.form.get('select1')
            val=str(selectValue)
            cursor.execute('UPDATE transaction_history set Transaction_status =%s where transaction_id=%s',(val,transaction_id,))
            cursor.execute('select * from transaction_history where transaction_id=%s',(transaction_id,))
            info=cursor.fetchone()
            account_no=info[6]
            amount=int(info[1])
            if(val=='Approve'):
                cursor.execute('update accounts set balance=balance+%s where account_no=%s',(amount,account_no,))
            mysql.connection.commit() 
        cursor.execute('SELECT * from transaction_history WHERE Transaction_status = "pending" and account_no in (select account_no from accounts where admin_id=%s)',(admin_id,))
        msg = cursor.fetchall()
        cursor.close()
        return render_template('query5.html',msg=msg)
    return redirect(url_for('adminlogin'))
 

@app.route('/query6', methods=['GET', 'POST'])    #for variying account no 
def query6():
    msg=""
    if 'Admin_LoggedIn' in session:
        cursor = mysql.connection.cursor()
        if request.method == 'POST':
            admin_id= session['Admin_ID']
            account_no=request.form['account_no']
            selectValue = request.form.get('select1')
            val=str(selectValue)
            cursor.execute('UPDATE accounts set Account_status =%s where Account_no=%s',(val,account_no,))
            cursor.execute('UPDATE accounts set Admin_ID=%s where Account_no=%s',(admin_id,account_no,))
            cursor.execute('UPDATE Admin set Total_user=Total_user+1 where Admin_ID=%s',(admin_id,))
            mysql.connection.commit() 
        cursor.execute('SELECT * from accounts WHERE Account_status ="pending"')
        msg = cursor.fetchall()
        cursor.close()
        return render_template('query6.html',msg=msg)
    return redirect(url_for('adminlogin'))


if __name__ == '__main__':
    app.run(debug=True)
