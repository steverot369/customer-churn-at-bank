from flask import *
from database import *
from datetime import datetime
import random
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="bank"
)
customer=Blueprint('customer',__name__)

@customer.route('/customerhome')
def customerhome():
    # data={}
    cursor = db.cursor()
    cursor.execute("SELECT t_no,t_type,amount,date_time,customer_id from transaction where customer_id=(select cid from customers where cid='%s') LIMIT 8"%(session['cust_id']))
    transaction = cursor.fetchall()
    cursor.execute("select fname,lname,email from customers where loginid='%s'"%(session['logid']))
    name = cursor.fetchall()
    return render_template('customerhome.html',transaction=transaction,name=name)



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
        cursor.execute("select pin_no,balance,customer_id,branch_id,savings_id from savingsacc where acc_no='%s'"%(accno))
        mpipin=cursor.fetchone()
        balance=mpipin[1]
        cid=mpipin[2]
        branch_id=mpipin[3]
        savings_id=mpipin[4]
        amount_debited = int(balance) - int(amount)
        date = datetime.now()
        trans_no = str(random.randint(1000000000000000, 9999999999999999))

        print(mpipin[0])
        if mpipin[0] == '1':
            flash("set mpi pin...")
            return redirect(url_for('customer.customersetpin'))
        elif mpipin[0] == pin:
            cursor.execute("UPDATE savingsacc SET balance = balance + %s WHERE acc_no = %s",(amount, to_acc,))
            cursor.execute("UPDATE savingsacc SET balance = balance - %s WHERE acc_no = %s",(amount, accno,))
            transaction = "INSERT INTO o_transaction (acc_id, customer_id, branch_id, from_acc, to_acc, amount_credited, amount_debited, t_type, t_no, date) VALUES (%s, %s, %s, %s, %s, %s, %s, 'online', %s, %s)"
            transaction_values = (savings_id, cid, branch_id, accno, to_acc, amount, amount, trans_no, date)
            cursor.execute(transaction, transaction_values)
 
            transaction1 = "INSERT INTO transaction (customer_id,acc_id,branch_id,t_no,t_type,amount, date_time) VALUES (%s, %s,%s, %s, 'cash depsoit',%s,%s)"
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




@customer.route('/customerrequestcreditcard')
def customerrequestcreditcard():
    # data={}
    cursor=db.cursor()
    cursor.execute("select fname,lname,dob,gender,phone,email,city,state,zipcode,country,msalary,idnumber from customers where cid='%s'"%(session['cust_id']))
    customer=cursor.fetchall()
    card_name = request.args.get('card_name')
    return render_template('customerrequestcreditcard.html',customer=customer,card_name=card_name)

@customer.route('/differentcreditcard',methods=['post','get'])
def differentcreditcard():
   
    return render_template('differentcreditcard.html')


