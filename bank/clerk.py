from flask import *
from database import *
import uuid
import demjson
import datetime
import smtplib
# import schedule
# import time
from dateutil.relativedelta import relativedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
app.secret_key = 'your_secret_key' 
admin=Blueprint('admin',__name__)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="bank"
)
clerk=Blueprint('clerk',__name__)

@clerk.route('/clerkhome')
def clerkhome():
    cursor = db.cursor()
    cursor.execute("select employe_fname,employee_lname,email from employee where loginid='%s'"%(session['logid']))
    name = cursor.fetchall()
    cursor.execute("SELECT branch_name FROM branch")
    branch_names = [row[0] for row in cursor.fetchall()]
    print(branch_names)
    return render_template('clerkhome.html',name=name)
    

@clerk.route('/clerkmanagehome')
def clerkmanagehome():
    return render_template('clerkmanagehome.html')
    

@clerk.route('/clerkadduser', methods=['post', 'get'])
def clerkadduser():
    cursor = db.cursor()
    # cursor.execute("SELECT e.branch,e.employe_fname from employee e,branch b where e.branch_id=b.branch_id and e.branch_id=(select branch_id from employee where employe_id='%s'%(session['logid'])) and employee='clerk'")
    cursor.execute("SELECT branch from employee where employe_id='%s'" % session['clid'])
    # cursor.execute("SELECT e.branch, e.employe_fname FROM employee e, branch b WHERE e.branch_id = b.branch_id AND e.branch_id = (SELECT branch_id FROM employee WHERE employe_id = '{}') AND employe_id='{}'".format(session['clid'], session['logid']))

    branch_names = [row[0] for row in cursor.fetchall()]
    print(branch_names)
    if 'add' in request.form:
        fname = request.form['fname']
        lname = request.form['lname']
        dob = request.form['dob']
        i=request.files['image']
        img="uploads/"+str(uuid.uuid4())+i.filename
        i.save('bank/static/'+img)
        status = request.form['status']
        gender = request.form['gender']
        phone = request.form['phone']
        email = request.form['email']
        branch = request.form['branch']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        zipcode = request.form['zipcode']
        country = request.form['country']
        education = request.form['education']
        msalary = request.form['msalary']

        idproof = request.form['idproof']
        idnumber = request.form['idnumber']
        idupload = request.files['image1']
        img1="uploads/"+str(uuid.uuid4())+idupload.filename
        idupload.save('bank/static/'+img1)
        join_date = datetime.datetime.now().date()  # Get current date
        recipient_email = request.form['email']
        sender_email = "mltalerts.mlt.co.in@gmail.com"
        subject = "registration"
        message = f"Welcome, {fname} {lname}! Thank you for registering with us. \n your temporary username: {email} and password : {phone} \n you can change it after sime time!!"
        
        
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        
        
        msg.attach(MIMEText(message, "plain"))
        
       
        smtp_host = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = "mltalerts.mlt.co.in@gmail.com"
        smtp_password = "kjerrrtwgllsaqdp"
        
        
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            
            server.starttls()
        
            
            server.login(smtp_username, smtp_password)
        
            
            server.sendmail(sender_email, recipient_email, msg.as_string())
        
            
            server.quit()
        cursor.execute("select branch_id from branch  where branch_name='%s'"%(branch))
        branch_id=cursor.fetchone()[0]
        
        q = "INSERT INTO login VALUES(null,'%s', '%s', 'customer')" % (email, phone)
        id=insert(q)
        q = "INSERT INTO customers VALUES(null,'%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s', '%s', '%s', '%s','%s','%s','%s','%s','%s','%s','%s','%s','1')" % (id, branch_id,fname, lname, dob,img,status,gender,phone,email,branch,address,city,state,zipcode,country,education,msalary,idproof,idnumber,img1,join_date)
        insert(q)
       
        
        flash("Registration successful...")

    
        return redirect(url_for('clerk.clerkadduser'))
    return render_template('clerkadduser.html',branch_names=branch_names)



@clerk.route('/clerksavingsaccount',methods=['post', 'get'])
def clerksavingsaccount():
    cursor = db.cursor()
    cursor.execute("select fname,lname from customers where branch_id=(select branch_id from employee where employe_id='%s')"%(session['clid']))
    fname=cursor.fetchall()
    print(fname)
    cursor.execute("select ifsc_code from branch where branch_id=(select branch_id from employee where employe_id='%s')"%(session['clid']))
    branch_id=cursor.fetchone()[0]
    cursor.fetchall()
    cursor.execute("select branch_id from branch where branch_id=(select branch_id from employee where employe_id='%s')"%(session['clid']))
    bid=cursor.fetchone()[0]
    print("branch id =======",branch_id)
    if 'add' in request.form:
        name = request.form['name']
        accno = request.form['accno']
        ifsccode = request.form['ifsccode']
        balance='0'
        acc_started_date = datetime.datetime.now().date()
        name_parts = name.split(" ")
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        query = "SELECT cid FROM customers WHERE fname = %s AND lname = %s"
        cursor.execute(query, (first_name, last_name))
        cid = cursor.fetchone()[0]
        q = "INSERT INTO savingsacc (customer_id, branch_id, acc_no, ifsccode, balance,acc_started_date,pin_no,acc_status) VALUES (%s, %s, %s, %s, %s, %s,'1', 'active')"
        values = (cid, bid, accno, ifsccode, balance, acc_started_date)
        cursor.execute(q, values)
                # Generate random cheque number
        cursor.execute("select savings_id from savingsacc where acc_no='%s'"%(accno))
        acc_id=cursor.fetchone()[0]
        
        cheque_no = str(random.randint(1000000000, 9999999999))
        
        # Insert cheque details into Cheque table
        cheque_query = "INSERT INTO cheque (customer_id,savings_id,cheque_no,issued_date, status) VALUES (%s,%s, %s,%s, 'active')"
        cheque_values = (cid, acc_id,cheque_no,acc_started_date)
        cursor.execute(cheque_query, cheque_values)
        
        # Generate random debit card details
        debit_card_no = str(random.randint(1000000000000000, 9999999999999999))
        cv = str(random.randint(100, 999))
        expiry_date = (datetime.datetime.now() + datetime.timedelta(days=365 * 20)).date()
        
        # Insert debit card details into Debit Card table
        debit_card_query = "INSERT INTO debitcard (customer_id,savings_id,debit_no,cv,expiry_date, status) VALUES (%s, %s,%s, %s, %s,'active')"
        debit_card_values = (cid,acc_id,debit_card_no, cv, expiry_date)
        cursor.execute(debit_card_query, debit_card_values)
        cursor.execute("SELECT count FROM bankproducts WHERE customer_id = %s", (cid,))
        existing_record = cursor.fetchone()
        if existing_record:  
            count = existing_record[0] + 2
            cursor.fetchall()
            cursor.execute("UPDATE bankproducts SET count = %s WHERE customer_id = %s", (count, cid))
        else:
            cursor.execute("INSERT INTO bankproducts (customer_id, count) VALUES (%s, %s)", (cid, 2))   
        flash("Registration successful...")
        return redirect(url_for('clerk.clerksavingsaccount'))

    return render_template('clerksavingsaccount.html',fname=fname,branch_id=branch_id)





@clerk.route('/clerkdepositaccount',methods=['get','post'])
def clerkdepositaccount():
    cursor = db.cursor()
    cursor.execute("select fname,lname from customers where branch_id=(select branch_id from employee where employe_id='%s')"%(session['clid']))
    fname=cursor.fetchall()
    print(fname)
    cursor.fetchall()
    cursor.execute("select branch_id from branch where branch_id=(select branch_id from employee where employe_id='%s')"%(session['clid']))
    bid=cursor.fetchone()[0]
    cursor.execute("select ifsc_code from branch where branch_id=(select branch_id from employee where employe_id='%s')"%(session['clid']))
    branch_id=cursor.fetchone()[0]
    cursor.execute("select c.fname,c.lname,s.acc_no from savingsacc s,customers c where c.cid=s.customer_id and c.branch_id=(select branch_id from employee where employe_id='%s')" % (session['clid']))
    accno = cursor.fetchall()
    if 'add' in request.form:
        name = request.form['name']

        depositamt = request.form['depositAmount']
        newaccno = request.form['accno']
        ifsccode = request.form['ifsccode']
        interestEarned = request.form['interestEarned']
        tenure = request.form['tenure']
        depositType = request.form['depositType']
        maturityDate = request.form['interestRate']
        maturityDate = request.form['maturityDate']
        toaccno = request.form['addaccno']
        interestRate = request.form['interestRate']
        
        print(toaccno)
        name_parts = name.split(" ")
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        query = "SELECT cid FROM customers WHERE fname = %s AND lname = %s"
        cursor.execute(query, (first_name, last_name))
        cid = cursor.fetchone()[0]
        date = datetime.datetime.now().date()
        formatted_date = date.strftime("%d-%m-%y")
        fixeddeposit = "INSERT INTO depositacc (customer_id, acc_no, ifsccode, deposit_amt, tenure, deposit_date, deposit_type, maturity_date, interest_rate, interest_amt, interest_earn,acc_to, last_transaction_date,acc_type, acc_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,'0',%s,%s, 'deposit', 'active')"
        fixeddeposit_values = (cid, newaccno, ifsccode, depositamt, tenure, formatted_date, depositType, maturityDate, interestRate,interestEarned,toaccno,formatted_date)
        cursor.execute(fixeddeposit, fixeddeposit_values)

        flash("Registration successful...")
        return redirect(url_for('clerk.clerkdepositaccount'))
        
        
    return render_template('clerkdepositaccount.html',fname=fname,branch_id=branch_id,accno=accno)








@clerk.route('/clerkloanaccount',methods=['post','get'])
def clerkloanaccount():
    cursor = db.cursor()
    cursor.execute("select fname,lname from customers where branch_id=(select branch_id from employee where employe_id='%s')"%(session['clid']))
    fname=cursor.fetchall()
    print(fname)
    cursor.fetchall()
    cursor.execute("select branch_id from branch where branch_id=(select branch_id from employee where employe_id='%s')"%(session['clid']))
    bid=cursor.fetchone()[0]
    cursor.execute("select ifsc_code from branch where branch_id=(select branch_id from employee where employe_id='%s')"%(session['clid']))
    branch_id=cursor.fetchone()[0]
    cursor.execute("select c.fname,c.lname,s.acc_no from savingsacc s,customers c where c.cid=s.customer_id and c.branch_id=(select branch_id from employee where employe_id='%s')" % (session['clid']))
    accno = cursor.fetchall()
    
    if 'add' in request.form:
        name = request.form['name']

        
        newaccno = request.form['accno']
        ifsccode = request.form['ifsccode']
        toaccno = request.form['addaccno']
        loanType=request.form['loanType']
        loanAmount = request.form['loanAmount']
        
        tenure = request.form['tenure']
        maturityDate = request.form['interestRate']
        emiPayment=request.form['emiPayment']
        interestPayableDate=request.form['interestPayableDate']
        maturityDate = request.form['maturityDate']
   
        interestRate = request.form['interestRate']
        name_parts = name.split(" ")
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        query = "SELECT cid FROM customers WHERE fname = %s AND lname = %s"
        cursor.execute(query, (first_name, last_name))
        cid = cursor.fetchone()[0]
        date = datetime.datetime.now().date()
        formatted_date = date.strftime("%d-%m-%y")
        remaining_loanAmount='0'
        fixeddeposit = "INSERT INTO loanacc (customer_id,branch_id,acc_no,ifsccode,loan_type,acc_payable,maturity_date,tenure,interest_rate,interst_amt,issued_amount,remaing_amount,date_issued,date_interest,acc_type,acc_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s,%s, %s, %s,%s,%s,'loanaccount', 'active')"
        fixeddeposit_values = (cid,bid, newaccno, ifsccode,loanType,toaccno,maturityDate,tenure,interestRate,emiPayment, loanAmount,loanAmount,formatted_date,interestPayableDate)
        cursor.execute(fixeddeposit, fixeddeposit_values)
        flash("Registration successful...")
        return redirect(url_for('clerk.clerkdepositaccount'))
    return render_template('clerkloanaccount.html',fname=fname,branch_id=branch_id,accno=accno)



@clerk.route('/clerkloancash',methods=['post','get'])
def clerkloancash():
    cursor = db.cursor()
    cursor.execute("select employe_fname, employee_lname, email from employee where loginid='%s'" % (session['logid']))
    name = cursor.fetchall()
    cursor.execute("select c.fname,c.lname,s.acc_no from loanacc s,customers c where c.cid=s.customer_id and s.branch_id=(select branch_id from employee where employe_id='%s') and s.acc_type='loanaccount'" % (session['clid']))
    accno = cursor.fetchall()
    accountDetails = []  # Initialize accountDetails with a default value
    if 'add' in request.form:
        accno = request.form['accno']
        # cursor.execute("SELECT s.acc_no,s.ifsccode,s.balance,c.fname,c.lname from customers c,savingsacc s where c.cid=s.customer_id and s.acc_no = %s", (accno,))
        cursor.execute("SELECT s.acc_no,s.ifsccode,c.fname,c.lname,s.issued_amount,s.remaing_amount,s.interst_amt,s.interest_rate from customers c,loanacc s where c.cid=s.customer_id and s.acc_no =%s",(accno,))
        accountDetails = cursor.fetchall()
        cursor.execute("select c.fname,c.lname,s.acc_no from loanacc s,customers c where c.cid=s.customer_id and s.branch_id=(select branch_id from employee where employe_id='%s') and s.acc_type='loanaccount'" % (session['clid']))
        accno = cursor.fetchall()

    if 'add1' in request.form:
        # Retrieve form data
        accno1 = request.form['accno1']
        loanEmi=request.form['emi']
        name = request.form['name']
        loanAmount = float(request.form['remaining'])
        interestRate = float(request.form['interestRate'])
        
        name_parts = name.split(" ")
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        query = "SELECT cid FROM customers WHERE fname = %s AND lname = %s"
        cursor.execute(query, (first_name, last_name))
        cid = cursor.fetchone()[0]
       
        # Calculate interest and EMI
        interestRate = interestRate / 100 / 12  # Convert to monthly interest rate
        monthlyinterest=loanAmount*interestRate
        principleAmount = float(loanEmi) - monthlyinterest

        outstandingBalance = loanAmount - principleAmount
        print(interestRate)
        print(monthlyinterest)

        print(principleAmount)
        print(outstandingBalance)

        cursor.execute("UPDATE loanacc SET remaing_amount = %s WHERE acc_no = %s",(outstandingBalance, accno1,))
        db.commit()  # Commit the changes to the database
        flash("emi paid successfully...")
        return redirect(url_for('clerk.clerkloancash'))
    return render_template('clerkloancash.html', name=name, accno=accno, accountDetails=accountDetails)




@clerk.route('/clerkmanagecustomers',methods=['post','get'])
def clerkmanagecustomers():

    cursor = db.cursor()
    cursor.execute("select employe_fname,employee_lname,email from employee where loginid='%s'"%(session['logid']))
    name = cursor.fetchall()
    cursor.execute("SELECT * FROM customers where branch_id=(select branch_id from employee where employe_id='%s')"%(session['clid']))
    employees = cursor.fetchall()
    
    return render_template('clerkmanagecustomers.html',employees=employees,name=name)


@clerk.route('/clerkviewaccdetails')
def clerkviewaccdetails():
    cursor = db.cursor()
    cursor.execute("select employe_fname,employee_lname,email from employee where loginid='%s'"%(session['logid']))
    name = cursor.fetchall()
    cursor.execute("SELECT c.fname,c.lname,c.phone,c.photo,s.acc_no,s.ifsccode,s.acc_no,s.balance,s.acc_started_date,s.acc_status FROM customers c,savingsacc s where c.cid=s.customer_id")
    employees = cursor.fetchall()
    print(employees)
    return render_template('clerkviewaccdetails.html',name=name,employees=employees)


@clerk.route('/clerkviewloanacc',methods=['post','get'])
def clerkviewloanacc():

    cursor = db.cursor()
    cursor.execute("select employe_fname,employee_lname,email from employee where loginid='%s'"%(session['logid']))
    name = cursor.fetchall()
    cursor.execute("SELECT c.fname,c.lname,l.acc_no,l.ifsccode,l.interst_amt,l.interest_rate,l.issued_amount,l.remaing_amount,l.acc_status,l.date_interest,l.loan_type FROM customers c,loanacc l where c.cid=l.customer_id and l.branch_id=(select branch_id from employee where employe_id='%s')"%(session['clid']))
    employees = cursor.fetchall()
    date = datetime.datetime.now().date()
    formatted_date = date.strftime("%d-%m-%y")
    return render_template('clerkviewloanacc.html',employees=employees,name=name,formatted_date=formatted_date)



@clerk.route('/clerkdepositcash',methods=['post','get'])
def clerkdepositcash():
    cursor = db.cursor()
    
    
    cursor.execute("select employe_fname, employee_lname, email from employee where loginid='%s'" % (session['logid']))
    name = cursor.fetchall()
    cursor.execute("SELECT c.fname, c.lname, c.phone, c.photo, s.acc_no, s.ifsccode, s.acc_no, s.balance, s.acc_started_date, s.acc_status FROM customers c, savingsacc s where c.cid=s.customer_id")
    employees = cursor.fetchall()
    print(employees)
    cursor.execute("select c.fname,c.lname,s.acc_no from savingsacc s,customers c where c.cid=s.customer_id and c.branch_id=(select branch_id from employee where employe_id='%s')" % (session['clid']))
    accno = cursor.fetchall()

    accountDetails = []  # Initialize accountDetails with a default value

    if 'add' in request.form:
        accno = request.form['accno']
        # cursor.execute("SELECT s.acc_no,s.ifsccode,s.balance,c.fname,c.lname from customers c,savingsacc s where c.cid=s.customer_id and s.acc_no = %s", (accno,))
        cursor.execute("SELECT s.acc_no,s.ifsccode,s.balance,c.fname,c.lname,ch.cheque_no from customers c,savingsacc s,cheque ch where c.cid=s.customer_id and s.savings_id=ch.savings_id and s.acc_no =%s",(accno,))
        accountDetails = cursor.fetchall()
        cursor.execute("select c.fname,c.lname,s.acc_no from savingsacc s,customers c where c.cid=s.customer_id and c.branch_id=(select branch_id from employee where employe_id='%s')" % (session['clid']))
        accno = cursor.fetchall()
    if 'add1' in request.form:
        deposit = int(request.form['amt'])
        accno = request.form['accno1']
        transaction_type=request.form['paymentMethod']
        withdrawal_amt=request.form['amounts']

        # note
        fivers = int(request.form['5'])
        tenrs = int(request.form['10'])
        twentyrs = int(request.form['20'])
        fiftyrs = int(request.form['50'])
        hundredrs = int(request.form['100'])
        twohundredrs = int(request.form['200'])
        fivehundredrs = int(request.form['500'])
        thousandrs = int(request.form['1000'])
            


        print('deposit',deposit)
        print('amt',accno)
        
        cursor.execute("select branch_id from branch where branch_id=(select branch_id from employee where employe_id='%s')"%(session['clid']))
        bid=cursor.fetchone()[0]
        date = datetime.datetime.now()
        trans_no = str(random.randint(1000000000000000, 9999999999999999))
        cursor.execute("select savings_id from savingsacc where acc_no='%s'"%(accno))
        savings_id=cursor.fetchone()[0]
        cursor.execute("select customer_id from savingsacc where acc_no='%s'"%(accno))
        cid=cursor.fetchone()[0]
        if deposit>=25000:
            flash('min depsit value is 25000')
            return redirect(url_for('clerk.clerkdepositcash'))
        else:
            cursor.execute("UPDATE savingsacc SET balance = balance + %s WHERE acc_no = %s",(deposit, accno))
            transaction = "INSERT INTO transaction (customer_id,acc_id,branch_id,t_no,t_type,amount, date_time) VALUES (%s, %s,%s, %s, 'cash depsoit',%s,%s)"
            transaction_values = (cid,savings_id,bid,trans_no,deposit,date)
            cursor.execute(transaction, transaction_values)
            
            cursor.execute(transaction, transaction_values)     
            if fivers > 0:
                transaction = "INSERT INTO notescount (branch_id,note_type,count) VALUES (%s, '5',%s)"
                transaction_values = (bid,fivers)
                cursor.execute(transaction, transaction_values)
            if tenrs > 0:
                transaction = "INSERT INTO notescount (branch_id,note_type,count) VALUES (%s, '10',%s)"
                transaction_values = (bid,tenrs)
                cursor.execute(transaction, transaction_values)
            if twentyrs > 0:
                transaction = "INSERT INTO notescount (branch_id,note_type,count) VALUES (%s, '20',%s)"
                transaction_values = (bid,twentyrs)
                cursor.execute(transaction, transaction_values)
            if fiftyrs > 0:
                transaction = "INSERT INTO notescount (branch_id,note_type,count) VALUES (%s, '50',%s)"
                transaction_values = (bid,fivers)
                cursor.execute(transaction, transaction_values)
            if hundredrs > 0:
                transaction = "INSERT INTO notescount (branch_id,note_type,count) VALUES (%s, '100',%s)"
                transaction_values = (bid,hundredrs)
                cursor.execute(transaction, transaction_values)
            if twohundredrs > 0:
                transaction = "INSERT INTO notescount (branch_id,note_type,count) VALUES (%s, '200',%s)"
                transaction_values = (bid,twohundredrs)
                cursor.execute(transaction, transaction_values)
            if fivehundredrs > 0:
                transaction = "INSERT INTO notescount (branch_id,note_type,count) VALUES (%s, '500',%s)"
                transaction_values = (bid,fivehundredrs)
                cursor.execute(transaction, transaction_values)
            if thousandrs > 0:
                transaction = "INSERT INTO notescount (branch_id,note_type,count) VALUES (%s, '1000',%s)"
                transaction_values = (bid,thousandrs)
                cursor.execute(transaction, transaction_values)
        flash("depsoited successfully...")
        return redirect(url_for('clerk.clerkdepositcash'))

    if 'add2' in request.form:
        deposit = request.form['amt']
        accno = request.form['accno1']
        
        withdrawal_amt=request.form['amounts']
        balance=request.form['balance']
        cursor.execute("select branch_id from branch where branch_id=(select branch_id from employee where employe_id='%s')"%(session['clid']))
        bid=cursor.fetchone()[0]
        date = datetime.datetime.now()
        trans_no = str(random.randint(1000000000000000, 9999999999999999))
        cursor.execute("select savings_id from savingsacc where acc_no='%s'"%(accno))
        savings_id=cursor.fetchone()[0]
        cursor.execute("select customer_id from savingsacc where acc_no='%s'"%(accno))
        cid=cursor.fetchone()[0]
        if withdrawal_amt>balance:
            flash('cant withdraw')
            return redirect(url_for('clerk.clerkdepositcash'))
        else:
            cursor.execute("UPDATE savingsacc SET balance = balance - %s WHERE acc_no = %s",(withdrawal_amt, accno))
            transaction = "INSERT INTO transaction (customer_id,acc_id,branch_id,t_no,t_type,amount, date_time) VALUES (%s, %s,%s, %s, 'cheque withdrawl',%s,%s)"
            transaction_values = (cid,savings_id,bid,trans_no,withdrawal_amt,date)
            cursor.execute(transaction, transaction_values)
        
        
        flash("withdraw successfully...")
        return redirect(url_for('clerk.clerkdepositcash'))
    return render_template('clerkdepositcash.html', name=name, employees=employees, accno=accno, accountDetails=accountDetails)




@clerk.route('/clerkcheckdeposit',methods=['post','get'])
def clerkcheckdeposit():
    cursor = db.cursor()
    
    
    cursor.execute("select employe_fname, employee_lname, email from employee where loginid='%s'" % (session['logid']))
    name = cursor.fetchall()
    cursor.execute("SELECT c.fname, c.lname, c.phone, c.photo, s.acc_no, s.ifsccode, s.acc_no, s.balance, s.acc_started_date, s.acc_status FROM customers c, savingsacc s where c.cid=s.customer_id")
    employees = cursor.fetchall()
    print(employees)
    cursor.execute("select c.fname,c.lname,s.acc_no from savingsacc s,customers c where c.cid=s.customer_id and c.branch_id=(select branch_id from employee where employe_id='%s')" % (session['clid']))
    accno = cursor.fetchall()

    accountDetails = []  # Initialize accountDetails with a default value

    if 'add' in request.form:
        accno = request.form['accno']
        cursor.execute("SELECT s.acc_no,s.ifsccode,s.balance,c.fname,c.lname from customers c,savingsacc s where c.cid=s.customer_id and s.acc_no = %s", (accno,))
        accountDetails = cursor.fetchall()
        cursor.execute("select c.fname,c.lname,s.acc_no from savingsacc s,customers c where c.cid=s.customer_id and c.branch_id=(select branch_id from employee where employe_id='%s')" % (session['clid']))
        accno = cursor.fetchall()
    if 'add1' in request.form:
        deposit = request.form['amt']
        accno = request.form['accno1']

        # note
        fivers = int(request.form['5'])
        tenrs = int(request.form['10'])
        twentyrs = int(request.form['20'])
        fiftyrs = int(request.form['50'])
        hundredrs = int(request.form['100'])
        twohundredrs = int(request.form['200'])
        fivehundredrs = int(request.form['500'])
        thousandrs = int(request.form['1000'])
            


        print('deposit',deposit)
        print('amt',accno)
        
        cursor.execute("select branch_id from branch where branch_id=(select branch_id from employee where employe_id='%s')"%(session['clid']))
        bid=cursor.fetchone()[0]
        date = datetime.datetime.now()
        trans_no = str(random.randint(1000000000000000, 9999999999999999))
        cursor.execute("select savings_id from savingsacc where acc_no='%s'"%(accno))
        savings_id=cursor.fetchone()[0]
        cursor.execute("select customer_id from savingsacc where acc_no='%s'"%(accno))
        cid=cursor.fetchone()[0]
        cursor.execute("UPDATE savingsacc SET balance = balance + %s WHERE acc_no = %s",(deposit, accno))
        transaction = "INSERT INTO transaction (customer_id,acc_id,branch_id,t_no,t_type,amount, date_time) VALUES (%s, %s,%s, %s, 'deposit',%s,%s)"
        transaction_values = (cid,savings_id,bid,trans_no,deposit,date)
        cursor.execute(transaction, transaction_values)
        # Insert into the table if count is not 0
        if fivers > 0:
            transaction = "INSERT INTO notescount (branch_id,note_type,count) VALUES (%s, '5',%s)"
            transaction_values = (bid,fivers)
            cursor.execute(transaction, transaction_values)
        if tenrs > 0:
            transaction = "INSERT INTO notescount (branch_id,note_type,count) VALUES (%s, '10',%s)"
            transaction_values = (bid,tenrs)
            cursor.execute(transaction, transaction_values)
        if twentyrs > 0:
            transaction = "INSERT INTO notescount (branch_id,note_type,count) VALUES (%s, '20',%s)"
            transaction_values = (bid,twentyrs)
            cursor.execute(transaction, transaction_values)
        if fiftyrs > 0:
            transaction = "INSERT INTO notescount (branch_id,note_type,count) VALUES (%s, '50',%s)"
            transaction_values = (bid,fivers)
            cursor.execute(transaction, transaction_values)
        if hundredrs > 0:
            transaction = "INSERT INTO notescount (branch_id,note_type,count) VALUES (%s, '100',%s)"
            transaction_values = (bid,hundredrs)
            cursor.execute(transaction, transaction_values)
        if twohundredrs > 0:
            transaction = "INSERT INTO notescount (branch_id,note_type,count) VALUES (%s, '200',%s)"
            transaction_values = (bid,twohundredrs)
            cursor.execute(transaction, transaction_values)
        if fivehundredrs > 0:
            transaction = "INSERT INTO notescount (branch_id,note_type,count) VALUES (%s, '500',%s)"
            transaction_values = (bid,fivehundredrs)
            cursor.execute(transaction, transaction_values)
        if thousandrs > 0:
            transaction = "INSERT INTO notescount (branch_id,note_type,count) VALUES (%s, '1000',%s)"
            transaction_values = (bid,thousandrs)
            cursor.execute(transaction, transaction_values)
        
        flash("depsoited successfully...")
        return redirect(url_for('clerk.clerkdepositcash'))
    return render_template('clerkdepositcash.html', name=name, employees=employees, accno=accno, accountDetails=accountDetails)