from flask import *
from database import *
import uuid
import os
from datetime import datetime,timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app.secret_key = 'your_secret_key' 
admin=Blueprint('admin',__name__)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="bank"
)


@admin.route('/adminhome')
def adminhome():
    months = [
        'January', 'February', 'March', 'April',
        'May', 'June', 'July', 'August', 'September',
        'October', 'November', 'December'
    ]
    cursor = db.cursor()
    cursor.execute("SELECT MONTH(date_time), SUM(amount) FROM transaction GROUP BY MONTH(date_time)")
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



    
    cursor.execute("select sum(transaction_amount) from transactions")
    total_amount = cursor.fetchone()[0]
    cursor.execute("select uname from login where login_type='admin';")
    name = cursor.fetchone()[0]




    cursor.execute("""
        SELECT note_type, SUM(count) AS total_count
        FROM notescount
        GROUP BY note_type
        ORDER BY note_type DESC;
    """)

    # Fetch all rows from the result
    notes = cursor.fetchall()

    
   





    # ===============feedbacks
    cursor.execute("SELECT f.messages, f.date_time, c.photo,c.fname,c.lname FROM feedbacks f INNER JOIN customers c ON f.customer_id = c.cid ORDER BY f.date_time LIMIT 3")

    feedback_messages = cursor.fetchall()
 
    cursor = db.cursor()
    cursor.execute("SELECT l.acc_type,l.acc_no,l.date_issued,c.fname,c.lname FROM loanacc l,customers c where l.customer_id=c.cid UNION SELECT s.acc_type,s.acc_no,s.acc_started_date,c.fname,c.lname FROM savingsacc s,customers c where s.customer_id=c.cid UNION SELECT d.acc_type,d.acc_no,d.deposit_date,c.fname,c.lname FROM depositacc d,customers c where d.customer_id=c.cid and acc_status='active'")
    row_count=cursor.fetchall()
    account_count = cursor.rowcount
    cursor.execute("SELECT c.fname,c.lname,c.photo,tt.amount,tt.date_time,tt.t_type,tt.t_no FROM customers c,transaction tt where c.cid=tt.customer_id and tt.t_type='online' order by transaction_id desc LIMIT 4")
    online_transaction=cursor.fetchall()
    cursor.execute("SELECT c.fname,c.lname,tt.t_no,tt.t_type,tt.amount,tt.date_time FROM customers c,transaction tt where c.cid=tt.customer_id")
    transaction=cursor.fetchall()

    current_month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    current_month_end = current_month_start.replace(day=1, month=current_month_start.month + 1) - timedelta(days=1)

    current_month_query = "SELECT SUM(amount) FROM transaction WHERE date_time BETWEEN %s AND %s"
    cursor.execute(current_month_query, (current_month_start, current_month_end))
    current_month_result = cursor.fetchone()
    current_month_amount = current_month_result[0] if current_month_result[0] is not None else 0

    previous_month_query = "SELECT SUM(amount) FROM transaction WHERE date_time BETWEEN %s AND %s"
    cursor.execute(previous_month_query, (current_month_start - timedelta(days=30), current_month_start - timedelta(days=1)))
    previous_month_result = cursor.fetchone()
    previous_month_amount = previous_month_result[0] if previous_month_result[0] is not None else 0

    percentage_change = ((current_month_amount - previous_month_amount) / previous_month_amount) * 100 if previous_month_amount != 0 else 0
    percentage_change = min(percentage_change, 100)  # Limit the percentage change to 100
    percentage_change = round(percentage_change, 2)


    current_year = datetime.now().year
    previous_year = current_year - 1

    current_year_query = "SELECT COUNT(*) FROM customers WHERE YEAR(date) = %s"
    cursor.execute(current_year_query, (current_year,))
    current_year_result = cursor.fetchone()
    current_year_count = current_year_result[0] if current_year_result[0] is not None else 0

    previous_year_query = "SELECT COUNT(*) FROM customers WHERE YEAR(date) = %s"
    cursor.execute(previous_year_query, (previous_year,))
    previous_year_result = cursor.fetchone()
    previous_year_count = previous_year_result[0] if previous_year_result[0] is not None else 0

    customer_percentage_change = ((current_year_count - previous_year_count) / previous_year_count) * 100 if previous_year_count != 0 else 0
    customer_percentage_change = min(customer_percentage_change, 100)  # Limit the percentage change to 100
    customer_percentage_change = round(customer_percentage_change, 2)  # Round to two decimal places

   

    current_month_query1 = "SELECT COUNT(savings_id) FROM savingsacc WHERE acc_started_date BETWEEN %s AND %s"
    cursor.execute(current_month_query1, (current_month_start, current_month_end))
    current_month_result = cursor.fetchone()
    print("======current_month_result==========",current_month_result)
    current_month_balance = current_month_result[0] if current_month_result[0] is not None else 0

    previous_month_query1 = "SELECT COUNT(savings_id) FROM savingsacc WHERE acc_started_date BETWEEN %s AND %s"
    cursor.execute(previous_month_query1, (current_month_start - timedelta(days=30), current_month_start - timedelta(days=1)))
    previous_month_result = cursor.fetchone()
    print("=======previous_month_result=========",previous_month_result)
    previous_month_balance = previous_month_result[0] if previous_month_result[0] is not None else 0

    account_percentage_change = ((current_month_balance - previous_month_balance) / previous_month_balance) * 100 if previous_month_balance != 0 else 0
    account_percentage_change = round(account_percentage_change, 2)


    # for loan account
    current_month_query2 = "SELECT COUNT(loan_id) FROM loanacc WHERE date_issued BETWEEN %s AND %s"
    cursor.execute(current_month_query2, (current_month_start, current_month_end))
    current_month_result = cursor.fetchone()
    print("======current_month_result==========",current_month_result)
    current_month_balance1 = current_month_result[0] if current_month_result[0] is not None else 0

    previous_month_query2 = "SELECT COUNT(loan_id) FROM loanacc WHERE date_issued BETWEEN %s AND %s"
    cursor.execute(previous_month_query2, (current_month_start - timedelta(days=30), current_month_start - timedelta(days=1)))
    previous_month_result = cursor.fetchone()
    print("=======previous_month_result=========",previous_month_result)
    previous_month_balance1 = previous_month_result[0] if previous_month_result[0] is not None else 0

    loan_account_percentage_change = ((current_month_balance1 - previous_month_balance1) / previous_month_balance1) * 100 if previous_month_balance1 != 0 else 0
    loan_account_percentage_change = round(loan_account_percentage_change, 2)

    cursor.execute("select count(*) from customers where active='1'")
    customer_count=cursor.fetchone()[0]
    cursor.execute("select count(*) from employee where status='active'")
    employee_count=cursor.fetchone()[0]
    query = "SELECT COUNT(*) FROM complaints where reply='0'"
   
    cursor.execute(query)
    count = cursor.fetchone()[0]
    print("max date=",query)
    if 'count_removed' in session:
        session.pop('count_removed')  # Remove the 'count_removed' flag from session
    
    return render_template('adminhome.html', 
    labels=labels, values=values,total_amount=total_amount,name=name,feedback_messages=feedback_messages,count=count,online_transaction=online_transaction,notes=notes,
    transaction=transaction, current_month_amount=current_month_amount,
     previous_month_amount=previous_month_amount, percentage_change=percentage_change,
     current_year_count=current_year_count, previous_year_count=previous_year_count, customer_percentage_change=customer_percentage_change, 
     current_month_balance=current_month_balance, previous_month_balance=previous_month_balance, account_percentage_change=account_percentage_change,
     current_month_balance1=current_month_balance1, previous_month_balance1=previous_month_balance1, loan_account_percentage_change=loan_account_percentage_change,
     customer_count=customer_count,employee_count=employee_count,account_count=account_count)



@admin.route('/adminviewcomplaints', methods=['POST', 'GET'])
def adminviewcomplaints():
    
    cursor = db.cursor()
    query = "SELECT c.messages, c.date_time, cu.fname, cu.lname, cu.photo, c.reply, c.complaint_id FROM complaints c INNER JOIN customers cu ON c.customer_id = cu.cid WHERE c.reply = '0'"
    cursor.execute(query)
    messages = cursor.fetchall()
    cursor.execute("select count(*) from complaints where reply='0'")
    count=cursor.fetchone()[0]
    date=datetime.now()

    if "add" in request.form:
        id=request.form['complaint_id']
        reply = request.form['reply']
        print("reply===",reply)
        usertype='customer'
        cursor.execute("select customer_id,branch_id from complaints where complaint_id='%s'"%(id))
        customer_details=cursor.fetchone()
        cid=customer_details[0]
        bid=customer_details[1]
        cursor.execute("UPDATE complaints SET reply = %s WHERE complaint_id = %s", (reply, id))
        bank_messages = "INSERT INTO bank_messages (customer_id,branch_id,messages,user_type,message_type,date) VALUES (%s, %s, %s,%s,'bank',%s)"
        bank_messages_values = (cid,bid,reply,usertype,date)
        cursor.execute(bank_messages, bank_messages_values)

        flash("Send reply successfully")
        return redirect(url_for('admin.adminviewcomplaints'))
    
    
    return render_template('adminviewcomplaints.html', messages=messages,count=count)


@admin.route('/adminsendmessage',methods=['post','get'])
def adminsendmessage():
    cursor=db.cursor()
    cursor.execute("select branch_name from branch")
    branch_names = [row[0] for row in cursor.fetchall()]
    if 'add' in request.form:
        messages=request.form['messages']
        usertype=request.form['usertype']
        branchname=request.form['branch']
        date=datetime.now()
        cursor.execute("select branch_id from branch where branch_name='%s'"%(branchname))
        branch_id=cursor.fetchone()[0]
        bank_messages = "INSERT INTO bank_messages (customer_id,branch_id,messages,user_type,message_type,date) VALUES ('0', %s, %s,%s,'bank',%s)"
        bank_messages_values = (branch_id,messages,usertype,date)
        cursor.execute(bank_messages, bank_messages_values)
        flash("success message send")
        return redirect(url_for('admin.adminsendmessage'))


    
    return render_template('adminsendmessage.html',branch_names=branch_names)

@admin.route('/adminaddemployee', methods=['post', 'get'])
def adminaddemployee():
    cursor = db.cursor()
    cursor.execute("SELECT branch_name FROM branch")
    branch_names = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT email FROM customers UNION ALL SELECT email FROM employee")
    # cursor.execute("SELECT e.branch, e.employe_fname FROM employee e, branch b WHERE e.branch_id = b.branch_id AND e.branch_id = (SELECT branch_id FROM employee WHERE employe_id = '{}') AND employe_id='{}'".format(session['clid'], session['logid']))

    emails = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT phone from customers UNION ALL SELECT phone FROM employee")
    # cursor.execute("SELECT e.branch, e.employe_fname FROM employee e, branch b WHERE e.branch_id = b.branch_id AND e.branch_id = (SELECT branch_id FROM employee WHERE employe_id = '{}') AND employe_id='{}'".format(session['clid'], session['logid']))

    phoneno = [row[0] for row in cursor.fetchall()]
    if 'add' in request.form:
        fname = request.form['fname']
        lname = request.form['lname']
        dob = request.form['dob']
        i=request.files['image']
        img="uploads/"+str(uuid.uuid4())+i.filename
        i.save('bank/static/'+img)
        status = request.form['status']
        gender = request.form['gender']
        branch = request.form['branch']
        employee_type = request.form['employee_type']
        address = request.form['address']
        zipcode = request.form['zipcode']
        place = request.form['place']
        district = request.form['district']
        phone = request.form['phone']
        email = request.form['email']
        # username = request.form['username']
        # password = request.form['password']
        recipient_email = request.form['email']
        cursor.execute("select branch_id from branch  where branch_name='%s'"%(branch))
        branch_id=cursor.fetchone()[0]

	    

        sender_email = "mltalerts.mlt.co.in@gmail.com"
        subject = "registration"
        message = f"Welcome, {fname} {lname}! Thank you for registering with us.\n your temporary username: {email} and password : {phone} \n you can change it after sime time!!"
        
        # Create a MIME message
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        
        # Attach the message body
        msg.attach(MIMEText(message, "plain"))
        
        # SMTP server configuration
        smtp_host = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = "mltalerts.mlt.co.in@gmail.com"
        smtp_password = "kjerrrtwgllsaqdp"
        
        # Create an SMTP session
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            # Start TLS encryption for security
            server.starttls()
        
            # Login to the SMTP server
            server.login(smtp_username, smtp_password)
        
            # Send the email
            server.sendmail(sender_email, recipient_email, msg.as_string())
        
            # Close the SMTP session
            server.quit()
        
        
        q = "INSERT INTO login VALUES(null,'%s', '%s', '%s','no','active')" % (email, phone, employee_type)
        id=insert(q)
        q = "INSERT INTO employee VALUES(null,'%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s', '%s', '%s', '%s','%s ','%s','active')" % (id, branch_id,fname, lname, dob,img,status,gender,branch,employee_type,address,zipcode,place,district, phone, email)
        insert(q)
        cursor.execute("select * from branch")
        branch=cursor.fetchall()
        # Execute the employee query here
        flash("Registration successful...")

    
        return redirect(url_for('admin.adminaddemployee'))
    
    return render_template('adminaddemployee.html',branch_names=branch_names, phoneno= phoneno,emails=emails)

@admin.route('/adminaddbranch', methods=['post', 'get'])
def adminaddbranch():
   
    if 'add' in request.form:
        bname = request.form['bname']
        location = request.form['location']
        phoneno = request.form['phone']
        ifsccode = request.form['ifsccode']
        q = "INSERT INTO branch VALUES (null, '%s', '%s', '%s', '%s')" % (bname, location, phoneno, ifsccode)
        insert(q)
        flash("Registration successful...")
        return redirect(url_for('admin.adminaddbranch'))

    return render_template('adminaddbranch.html')



@admin.route('/adminviewbranch', methods=['post', 'get'])
def adminviewbranch():
    cursor = db.cursor()
   
    cursor.execute("SELECT * FROM branch")
    branch = cursor.fetchall()
    if 'add' in request.form:
        branch_id = request.form['bid']

        bname = request.form['bname']
        location = request.form['blocation']
        phoneno = request.form['bphone']
        cursor.execute("update branch set branch_name='%s',branch_location='%s',phoneno='%s' where branch_id='%s'"%(bname,location,phoneno,branch_id))
        flash('branch details updated successfully !')
        return redirect(url_for('admin.adminviewbranch'))
    if "action" in request.args:
        action=request.args['action']
       
        id=request.args['delete_id']
    else:
        action="none"

        
    if action=="reject":
       
        
        cursor.execute("update branch set status='reject' where loginid='%s'"%(id))
        
        flash('Rejected successfully !')
        return redirect(url_for('admin.adminviewbranch'))

    return render_template('adminviewbranch.html', branch=branch)



@admin.route('/adminmanagehome',methods=['post','get'])
def adminmanagehome():
	return render_template('adminmanagehome.html')





@admin.route('/adminmanagemployee',methods=['post','get'])
def adminmanagemployee():

    cursor = db.cursor()
    cursor.execute("SELECT * FROM employee where status='active' order by employe_id desc LIMIT 10")
    employees = cursor.fetchall()

    cursor.execute("select uname from login where login_type='admin';")
    name = cursor.fetchone()[0]
    cursor = db.cursor()
    cursor.execute("SELECT branch_name FROM branch")
    branch_names = [row[0] for row in cursor.fetchall()]
    if "action" in request.args:
        action=request.args['action']
       
        id=request.args['delete_id']
    else:
        action="none"

        
    if action=="reject":
       
        cursor.execute("update employee set status='reject' where loginid='%s'"%(id))
        cursor.execute("update login set status='reject' where loginid='%s'"%(id))
        
        flash('Rejected successfully !')
        return redirect(url_for('admin.adminmanagemployee'))
    return render_template('adminmanagemployee.html',employees=employees,name=name,branch_names=branch_names)


@admin.route('/viewdetails',methods=['post','get'])
def viewdetails():
    name1 = request.args.get('name1')
    name2 = request.args.get('name2')
    age = request.args.get('age')
    image = request.args.get('image')
    maritalStatus = request.args.get('maritalStatus')
    gender = request.args.get('gender')
    branch = request.args.get('branch')
    employeeType = request.args.get('employeeType')
    address = request.args.get('address')
    place = request.args.get('place')
    district = request.args.get('district')
    phone = request.args.get('phone')
    email = request.args.get('email')
    cursor = db.cursor()

    cursor.execute("select uname from login where login_type='admin';")
    name3 = cursor.fetchone()[0]
    return render_template('viewdetails.html', name1=name1, name2=name2,name3=name3,age=age, image=image, maritalStatus=maritalStatus, gender=gender, branch=branch, employeeType=employeeType, address=address, place=place, district=district, phone=phone, email=email)


@admin.route('/publichome')
def publichome():
    session.clear()
    flash("Successfully logout...")
    return redirect(url_for('public.publichome'))




@admin.route('/adminviewcustomer',methods=['post','get'])
def adminviewcustomer():

    cursor = db.cursor()
    cursor.execute("SELECT * FROM customers order by cid desc LIMIT 10")
    employees = cursor.fetchall()

    cursor.execute("select uname from login where login_type='admin';")
    name = cursor.fetchone()[0]
    cursor = db.cursor()
    cursor.execute("SELECT branch_name FROM branch")
    branch_names = [row[0] for row in cursor.fetchall()]
    return render_template('adminviewcustomer.html',employees=employees,name=name,branch_names=branch_names)



@admin.route('/adminviewtransaction',methods=['post','get'])
def adminviewtransaction():

    cursor = db.cursor()
    cursor.execute("select employe_fname,employee_lname,email from employee where loginid='%s'"%(session['logid']))
    name12 = cursor.fetchall()
    cursor.execute("SELECT t.t_no,t.t_type,t.amount,t.date_time,c.fname,c.lname,s.acc_no from transaction t,customers c,savingsacc s where t.customer_id=c.cid AND t.customer_id=s.customer_id")
    employees = cursor.fetchall()
    date = datetime.now().date()
    formatted_date = datetime.strftime(date,"%d-%m-%y")
    return render_template('adminviewtransaction.html',employees=employees,name12=name12,formatted_date=formatted_date)


@admin.route('/adminviewacc')
def adminviewacc():
    cursor = db.cursor()
    
    cursor.execute("""
    SELECT l.acc_type, l.acc_no, l.date_issued, c.fname, c.lname, c.photo, c.email, c.phone, l.acc_status, l.ifsccode, loan_id
    FROM loanacc l, customers c
    WHERE l.customer_id = c.cid AND l.acc_status = 'active'
    UNION
    SELECT s.acc_type, s.acc_no, s.acc_started_date, c.fname, c.lname, c.photo, c.email, c.phone, s.acc_status, s.ifsccode, s.savings_id
    FROM savingsacc s, customers c
    WHERE s.customer_id = c.cid AND s.acc_status = 'active'
    UNION
    SELECT d.acc_type, d.acc_no, d.deposit_date, c.fname, c.lname, c.photo, c.email, c.phone, d.acc_status, d.ifsccode, d.deposit_id
    FROM depositacc d, customers c
    WHERE d.customer_id = c.cid AND d.acc_status = 'active' 
    """)

    employees = cursor.fetchall()
    print(employees)
    return render_template('adminviewacc.html',employees=employees)



@admin.route('/analytics', methods=['POST', 'GET'])
def analytics():
    
    cursor = db.cursor()
    query = "SELECT c.messages, c.date_time, cu.fname, cu.lname, cu.photo, c.reply, c.complaint_id FROM complaints c INNER JOIN customers cu ON c.customer_id = cu.cid WHERE c.reply = '0'"
    cursor.execute(query)
    messages = cursor.fetchall()
    cursor.execute("select count(*) from complaints where reply='0'")
    count=cursor.fetchone()[0]
    date=datetime.now()

    
      
    
    
    return render_template('analytics.html')
    