from flask import *
from database import *
import uuid
import os
from datetime import datetime
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
    cursor.execute("SELECT MONTH(transaction_date), SUM(transaction_amount) FROM transactions GROUP BY MONTH(transaction_date)")
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


    # ===============feedbacks
    cursor.execute("select message,date from feedback order by date LIMIT 3")
    feedback_messages = cursor.fetchall()
 
    cursor = db.cursor()
    query = "SELECT COUNT(*) FROM feedback WHERE DATE(date) = CURDATE()"
    # latest message
    # query="SELECT COUNT(*) FROM feedback WHERE date = (SELECT MAX(date) FROM feedback)"
    cursor.execute(query)
    count = cursor.fetchone()[0]
    print("max date=",query)
    if 'count_removed' in session:
        session.pop('count_removed')  # Remove the 'count_removed' flag from session
    
    return render_template('adminhome.html', labels=labels, values=values,total_amount=total_amount,name=name,feedback_messages=feedback_messages,count=count)


@admin.route('/adminviewfeedback')
def adminviewfeedback():
    cursor = db.cursor()
    # cursor.execute("SELECT message,date FROM feedback")
    query = "SELECT message,date FROM feedback WHERE DATE(date) = CURDATE()"
    cursor.execute(query)
    messages = cursor.fetchall()

    # cursor.execute("select message,date from feedback order by date DESC LIMIT 6")
    # messages = cursor.fetchall()
    return render_template('adminviewfeedback.html',messages=messages)

@admin.route('/adminsendmessage')
def adminsendmessage():
    
    return render_template('adminsendmessage.html')

@admin.route('/adminaddemployee', methods=['post', 'get'])
def adminaddemployee():
    cursor = db.cursor()
    cursor.execute("SELECT branch_name FROM branch")
    branch_names = [row[0] for row in cursor.fetchall()]
    if 'add' in request.form:
        fname = request.form['fname']
        lname = request.form['lname']
        age = request.form['age']
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
        username = request.form['username']
        password = request.form['password']
        recipient_email = request.form['email']
        cursor.execute("select branch_id from branch  where branch_name='%s'"%(branch))
        branch_id=cursor.fetchone()[0]

	    

        sender_email = "mltalerts.mlt.co.in@gmail.com"
        subject = "registration"
        message = f"Welcome, {fname} {lname}! Thank you for registering with us."
        
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
        
        
        q = "INSERT INTO login VALUES(null,'%s', '%s', '%s')" % (username, password, employee_type)
        id=insert(q)
        q = "INSERT INTO employee VALUES(null,'%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s', '%s', '%s', '%s','%s ','%s','active')" % (id, branch_id,fname, lname, age,img,status,gender,branch,employee_type,address,zipcode,place,district, phone, email)
        insert(q)
       
        # Execute the employee query here
        flash("Registration successful...")

    
        return redirect(url_for('admin.adminaddemployee'))
    
    return render_template('adminaddemployee.html',branch_names=branch_names)

        
@admin.route('/adminaddbranch',methods=['post','get'])
def adminaddbranch():
    if 'add' in request.form:
        bname = request.form['bname']
        location = request.form['location']
        phoneno = request.form['phone']
        ifsccode = request.form['ifsccode']

        q = "INSERT INTO branch VALUES(null,'%s', '%s', '%s','%s')" % (bname, location, phoneno,ifsccode)
        insert(q)
        # Execute the employee query here
        flash("Registration successful...")
        return redirect(url_for('admin.adminaddbranch'))
    return render_template('adminaddbranch.html')

@admin.route('/adminmanagehome',methods=['post','get'])
def adminmanagehome():
	return render_template('adminmanagehome.html')


@admin.route('/adminmanagemployee',methods=['post','get'])
def adminmanagemployee():

    cursor = db.cursor()
    cursor.execute("SELECT * FROM employee order by employe_id desc LIMIT 10")
    employees = cursor.fetchall()

    cursor.execute("select uname from login where login_type='admin';")
    name = cursor.fetchone()[0]
    cursor = db.cursor()
    cursor.execute("SELECT branch_name FROM branch")
    branch_names = [row[0] for row in cursor.fetchall()]
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
    