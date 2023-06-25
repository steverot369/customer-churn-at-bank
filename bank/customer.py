from flask import *
from database import *
from datetime import datetime
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
    return render_template('customerhome.html',transaction=transaction)



@customer.route('/customerviewtransaction')
def customerviewtransaction():
    # data={}
    return render_template('customerviewtransaction.html')




