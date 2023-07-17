from flask import Flask
from public import public
from admin import admin
from manager import manager
from clerk import clerk
from customer import customer
from scheduler import scheduler
from update_interest_earn import update_interest_earn




app=Flask(__name__)

app.secret_key="secretkey"


# @app.route('/interstcal')
# def interstcal():
#     # Manually trigger the job
#     update_interest_earn()
#     return "Interest calculation started"
app.register_blueprint(public)

app.register_blueprint(admin,url_prefix='/admin')
app.register_blueprint(manager,url_prefix='/manager')
app.register_blueprint(clerk,url_prefix='/clerk')
app.register_blueprint(customer,url_prefix='/customer')


app.run(debug=True,host="0.0.0.0",port=5021)

