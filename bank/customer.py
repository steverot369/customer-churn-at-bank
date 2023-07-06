import uuid
from flask import *
from database import *
from datetime import datetime,timedelta
import random
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="bank"
)
customer=Blueprint('customer',__name__)

@customer.route('/customerhome',methods=['post', 'get'])
def customerhome():
    # data={}
    cursor = db.cursor()
    months = [
        'January', 'February', 'March', 'April',
        'May', 'June', 'July', 'August', 'September',
        'October', 'November', 'December'
    ]
    cursor = db.cursor()
    cursor.execute("SELECT MONTH(date_time), SUM(amount) FROM transaction where customer_id='%s' GROUP BY MONTH(date_time)"%(session['cust_id']))
    data = cursor.fetchall()
    labels = []
    values = []
    for month in months:
        month_num = datetime.strptime(month, '%B').month
        found = False
        for row in data:
            if row[0] == month_num:
                labels.append(month)
                values.append(row[1])
                found = True
                break
        if not found:
            labels.append(month)
            values.append(0)
   
    cursor.execute("SELECT t_no,t_type,amount,date_time,customer_id from transaction where customer_id=(select cid from customers where cid='%s') LIMIT 8"%(session['cust_id']))
    transaction = cursor.fetchall()
    cursor.execute("select fname,lname,email from customers where loginid='%s'"%(session['logid']))
    name = cursor.fetchall()
    cursor.execute("select cid,branch_id from customers where cid='%s'"%(session['cust_id']))
    customer=cursor.fetchone()
    cid=customer[0]
    bid=customer[1]
    date = datetime.now()
    cursor.execute("select balance,acc_no,ifsccode from savingsacc where customer_id='%s'"%(session['cust_id']))
    customer_details=cursor.fetchall()
    cursor.execute("select count from bankproducts where customer_id='%s'"%(session['cust_id']))
    count=cursor.fetchone()[0]
    cursor.execute("SELECT from_acc, to_acc, amount,t_type, date FROM o_transaction WHERE customer_id = '%s' LIMIT 4" % (session['cust_id']))

    transaction_details=cursor.fetchall()

   
    logged_in_user_id=int(session['cust_id'])
    print("login_id=====",logged_in_user_id)

    
    cursor.execute("SELECT customer_id, reciever_id,amount,date,name,photo,from_name,from_photo FROM o_transaction where customer_id=%s or reciever_id=%s ORDER BY date DESC LIMIT 5"%(logged_in_user_id,logged_in_user_id))
    details = cursor.fetchall()
    current_datetime = datetime.now()

# Extract the date portion from the current date and time
    current_date = current_datetime.date()
    cursor.execute("SELECT customer_id, reciever_id, amount, date, name, photo, from_name, from_photo FROM o_transaction WHERE (customer_id = %s OR reciever_id = %s) AND DATE(date) = %s ORDER BY date DESC LIMIT 3", (logged_in_user_id, logged_in_user_id, current_date))

    details1 = cursor.fetchall()
   

   
    if 'add' in request.form:
        messages=request.form['messages']
# Calculate the minimum allowed submission time (1 hour ago from the current time)
        min_allowed_time =  date - timedelta(hours=1)

        # Query the database to check the last submission time
        cursor.execute("SELECT MAX(date_time) FROM feedbacks WHERE customer_id = %s", (cid,))
        last_submission_time = cursor.fetchone()[0]

        # If the last submission time is None or earlier than the minimum allowed time, allow the submission
        if last_submission_time is None or last_submission_time < min_allowed_time:
            # Insert the feedback into the database
            feedback = "INSERT INTO feedbacks (customer_id, branch_id, messages, date_time) VALUES (%s, %s, %s, %s)"
            feedback_values = (cid, bid, messages, date)
            cursor.execute(feedback, feedback_values)
            flash('success')
        else:
            print('send after 1 hoursuccess')
   
    if 'add1' in request.form:
        messages=request.form['comments']

        min_allowed_time =  date - timedelta(hours=1)

     
        cursor.execute("SELECT MAX(date_time) FROM complaints WHERE customer_id = %s", (cid,))
        last_submission_time = cursor.fetchone()[0]

      
        if last_submission_time is None or last_submission_time < min_allowed_time:
           
            complaint = "INSERT INTO complaints (customer_id, branch_id, messages,reply ,date_time) VALUES (%s, %s, %s,'0', %s)"
            complaint_values = (cid, bid, messages, date)
            cursor.execute(complaint, complaint_values)
            flash('success')
        else:
            print('send after 1 hoursuccess')
    return render_template('customerhome.html',transaction=transaction,name=name,customer_details=customer_details,count=count,labels=labels, values=values,transaction_details=transaction_details,details=details,details1=details1,logged_in_user_id=logged_in_user_id)



@customer.route('/customerviewtransaction')
def customerviewtransaction():
    # data={}
    cursor = db.cursor()

    cursor.execute("SELECT t_no,t_type,amount,date_time,customer_id from transaction where customer_id=(select cid from customers where cid='%s')"%(session['cust_id']))
    transaction = cursor.fetchall()
    return render_template('customerviewtransaction.html',transaction=transaction)


@customer.route('/customerviewaccount')
def customerviewaccount():
    # data={}
    cursor = db.cursor()
    cursor.execute("SELECT acc_no,balance,acc_started_date from savingsacc where customer_id=(select cid from customers where cid='%s')"%(session['cust_id']))
    accounts = cursor.fetchall()
    return render_template('customerviewaccount.html',accounts=accounts)


@customer.route('/customertransferfund',methods=['post', 'get'])
def customertransferfund():
    # data={}
    cursor = db.cursor()

    cursor.execute("SELECT acc_no,balance,ifsccode from savingsacc where customer_id=(select cid from customers where cid='%s')"%(session['cust_id']))
    acc_no = cursor.fetchall()
    if 'add' in request.form:
        accno=request.form['accno']
        # from_acc = request.form['acc']
        to_acc = request.form['acc1']
        amount=request.form['amount']
        pin=request.form['mpipin']
        print("pin == ",pin)
        print("amount= ",amount)
        print("our account",acc_no)
        cursor.execute("select c.cid,c.fname,c.lname,c.photo from savingsacc s,customers c  where s.customer_id=c.cid and acc_no='%s'"%(to_acc))
        customer_details=cursor.fetchone()
        receiver_id=customer_details[0]
        fname=customer_details[1]
        lname=customer_details[2]
        full_name = fname + ' ' + lname
        photo=customer_details[3]


        cursor.execute("select c.cid,c.fname,c.lname,c.photo from savingsacc s,customers c  where s.customer_id=c.cid and acc_no=%s",(accno,))
        customer_details1=cursor.fetchone()
        # receiver_id=customer_details1[0]
        fname1=customer_details1[1]
        lname1=customer_details1[2]
        full_name1 = fname1 + ' ' + lname1
        photo1=customer_details1[3]


       


        print("receiver_id================",receiver_id)
        cursor.execute("select pin_no,balance,customer_id,branch_id,savings_id from savingsacc where acc_no='%s'"%(accno))
        mpipin=cursor.fetchone()
        balance=mpipin[1]
        cid=mpipin[2]
        branch_id=mpipin[3]
        savings_id=mpipin[4]
        
        date = datetime.now()
        trans_no = str(random.randint(1000000000000000, 9999999999999999))
        messages=f"a new transaction has done by you from acc {full_name} to {full_name1}"
        print(mpipin[0])
        if mpipin[0] == '1':
            flash("set mpi pin...")
            return redirect(url_for('customer.customersetpin'))
        elif mpipin[0] == pin:
            cursor.execute("UPDATE savingsacc SET balance = balance + %s WHERE acc_no = %s",(amount, to_acc,))
            cursor.execute("UPDATE savingsacc SET balance = balance - %s WHERE acc_no = %s",(amount, accno,))
            transaction = "INSERT INTO o_transaction (acc_id, customer_id,reciever_id, branch_id, from_acc, to_acc,name,photo,from_name,from_photo,amount,t_type, t_no, date) VALUES (%s, %s, %s,%s, %s,%s, %s,%s,%s, %s, %s, 'online', %s, %s)"
            transaction_values = (savings_id, cid,receiver_id, branch_id, accno, to_acc,full_name,photo,full_name1,photo1, amount,trans_no, date)
            cursor.execute(transaction, transaction_values)
            messages = "INSERT INTO bank_messages (customer_id,branch_id,messages,date) VALUES (%s, %s, %s)"
            messages_values = (cid,branch_id,messages,date)
            cursor.execute(messages, messages_values)
 
            transaction1 = "INSERT INTO transaction (customer_id,acc_id,branch_id,t_no,t_type,amount, date_time) VALUES (%s, %s,%s, %s, 'online',%s,%s)"
            transaction_values1 = (cid,savings_id,branch_id,trans_no,amount,date)
            cursor.execute(transaction1, transaction_values1) 

            flash("success...")
            return redirect(url_for('customer.customertransferfund'))
        
        else:
            flash("wrong pin")
            return redirect(url_for('customer.customertransferfund'))
        
    return render_template('customertransferfund.html',acc_no=acc_no)


@customer.route('/customersetpin',methods=['post', 'get'])
def customersetpin():
    # data={}
    cursor = db.cursor()
    cursor.execute("SELECT acc_no from savingsacc where customer_id=(select cid from customers where cid='%s')"%(session['cust_id']))
    acc_no = cursor.fetchall()
    if 'add' in request.form:
        acc_no=request.form['accno']
        confirmpin = request.form['confirmpin']
        cursor.execute("UPDATE savingsacc SET pin_no = %s WHERE acc_no = %s",(confirmpin, acc_no,))
        flash("successful Set Pin...")
        return redirect(url_for('customer.customersetpin'))
    return render_template('customersetpin.html',acc_no=acc_no)


@customer.route('/customerpayloan')
def customerpayloan():
    # data={}
    return render_template('customerpayloan.html')


@customer.route('/customerviewloanpayments')
def customerviewloanpayments():
    # data={}
    cursor=db.cursor()
    cursor.execute("select acc_no,ifsccode,loan_type,maturity_date,interest_rate,interst_amt,issued_amount,remaing_amount,date_interest from loanacc where customer_id=(select cid from customers where cid='%s')"%(session['cust_id']))
    loan=cursor.fetchall()
    return render_template('customerviewloanpayments.html',loan=loan)




@customer.route('/customerrequestcreditcard',methods=['post','get'])
def customerrequestcreditcard():
    # data={}
    cursor=db.cursor()
    cursor.execute("select fname,lname,dob,gender,phone,email,city,state,zipcode,country,msalary,idnumber,address from customers where cid='%s'"%(session['cust_id']))
    customer=cursor.fetchall()
    card_name = request.args.get('card_name')
    salary = request.args.get('salary')
    if 'add' in request.form:
        # card_name=request.form['cardname']
        jobname = request.form['j_name']
        company_name = request.form['c_name']
        company_location = request.form['c_location']
        m_salary = request.form['msalary']

        i1=request.files['file1']
        img1="uploads/"+str(uuid.uuid4())+i1.filename
        i1.save('bank/static/'+img1)

        i2=request.files['file2']
        img2="uploads/"+str(uuid.uuid4())+i2.filename
        i2.save('bank/static/'+img2)

        i3=request.files['file3']
        img3="uploads/"+str(uuid.uuid4())+i3.filename
        i3.save('bank/static/'+img3)

        request_date = datetime.now().date()  # Get current date
       
        cursor.execute("select cid from customers where cid='%s'"%(session['cust_id']))
        cid=cursor.fetchone()[0]
        cursor.execute("select branch_id from customers where cid='%s'"%(session['cust_id']))
        bid=cursor.fetchone()[0]
        credit_card = "INSERT INTO o_credit_card_request(customer_id,branch_id,card_name,job_type,c_name,c_location,m_salary,file1,file2,file3,date,status) VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s, %s,%s,'pending')"
        credit_card_values = (cid, bid, card_name, jobname,company_name, company_location, m_salary, img1, img2,img3,request_date)
        cursor.execute(credit_card, credit_card_values)

        
        flash("request successful...")

    
        return redirect(url_for('customer.customerrequestcreditcard'))
    
    return render_template('customerrequestcreditcard.html',customer=customer,card_name=card_name,salary=salary)

@customer.route('/differentcreditcard',methods=['post','get'])
def differentcreditcard():
    cursor=db.cursor()
    cursor.execute("select msalary from customers where cid='%s'"%(session['cust_id']))
    salary=cursor.fetchall()
    print(salary)
    return render_template('differentcreditcard.html',salary=salary)



@customer.route('/customersendfeedback')
def customersendfeedback():
    # data={}
 
    return render_template('customersendfeedback.html')




@customer.route('/customersendcomplaint')
def customersendcomplaint():
    # data={}
    cursor=db.cursor()
    cursor.execute("select cid,branch_id from customers where cid='%s'"%(session['cust_id']))
    customer=cursor.fetchone()
    cid=customer[0]
    bid=customer[1]
    current_datetime = datetime.now().date()
    formatted_datetime =datetime.strftime(current_datetime,"%d-%m-%y %H:%M:%S")

    if 'add' in request.form:
        messages=request.form['messages']
        complaint="insert into feedbacks(customer_id,branch_id,nessage,reply,date_time) values(%s,%s,%s,'0',%s)"
        complaint_values=(cid,bid,messages,formatted_datetime)
        cursor.execute(complaint,complaint_values)
    return render_template('customersendcomplaint.html')




@customer.route('/customerprofile', methods=['POST', 'GET'])
def customerprofile():
    cursor = db.cursor()
    cursor.execute("SELECT * FROM customers WHERE cid = %s" % (session['cust_id']))
    details = cursor.fetchall()
    cursor.execute("SELECT password FROM login WHERE loginid = %s" % (session['logid']))
    password = cursor.fetchone()[0]
    print(details)

    if request.method == 'POST':
        if 'add' in request.form:
            image = request.files['file']
            if image:
                img = "uploads/" + str(uuid.uuid4()) + image.filename
                image.save('bank/static/' + img)
                cursor.execute("UPDATE customers SET photo = %s WHERE loginid = %s", (img, session['logid']))
                flash("Photo updated successfully")
            else:
                flash("No photo selected")
            return redirect(url_for('customer.customerprofile'))
    if request.method == 'POST':
        if 'add1' in request.form:
            
            newpassword=request.form['confirmpassword']
            if newpassword:
                cursor.execute("UPDATE login SET password = '%s' where loginid='%s'"%(newpassword,session['logid']))
                flash("password updated sucessfully")
                return redirect(url_for('public.login'))
            else:
                flash("No password selected")
            return redirect(url_for('customer.customerprofile'))

    return render_template('customerprofile.html',details=details,password=password)




@customer.route('/customerpaysloan', methods=['POST', 'GET'])
def customerpaysloan():
    
    return render_template('customerpaysloan.html')