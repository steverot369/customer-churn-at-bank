from flask import *
from database import *
public=Blueprint('public',__name__)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="bank"
)

@public.route('/',methods=['post','get'])
def publichome():
	return render_template('publichome.html')

@public.route('/login',methods=['post','get'])
def login():
	if 'submit' in request.form:
		username=request.form['username']
		passw=request.form['password']

		q="select * from login where uname='%s' and password='%s' and status='active'"%(username,passw)
		res=select(q)
		print(res)
		if res:
			session['logid']=res[0]['loginid']
			
			if res[0]['login_type']=="admin":
				flash('Welcome')
				return redirect(url_for("admin.adminhome"))
				
			elif res[0]['login_type']=="manager":
				
				q="select * from employee where loginid='%s'"%(session['logid'])
				res=select(q)
				
				session['mid']=res[0]['employe_id']
				flash('Welcome')
				return redirect(url_for("manager.managerhome"))
			elif res[0]['login_type']=="clerk":
				q="select * from employee where loginid='%s'"%(session['logid'])
				res=select(q)
				session['clid']=res[0]['employe_id']
				print(session['clid'])
				flash('Welcome')
				return redirect(url_for("clerk.clerkhome"))
			elif res[0]['login_type']=="customer":
				q="select * from customers where loginid='%s'"%(session['logid'])
				res=select(q)
				session['cust_id']=res[0]['cid']
				# print(session['cid'])
				flash('Welcome')
				
				return redirect(url_for("customer.customerhome"))
		
		else:
			flash('Invalid username or password !!!')
	return render_template('login.html')



@public.route('/forgotpassword',methods=['post','get'])
def forgotpassword():
	cursor=db.cursor()
	if 'add' in request.form:
		# phoneno=request.form['phoneno']
		username=request.form['phoneno']

		password=request.form['password']
		cursor.execute("select uname from login where uname='%s' and  status='active'"%(username))
		uname=cursor.fetchone()
		
		

		if uname is not None:
			cursor.execute("update login set password='%s' where uname='%s'"%(password,username))
			flash("updated successfully")
			return redirect(url_for("public.login"))
		else:
			flash("username does not exist or wrong username")
			return redirect(url_for("public.forgotpassword"))


		


	return render_template('forgotpassword.html')

