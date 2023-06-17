from flask import *
from database import *
import uuid
import demjson

customer=Blueprint('customer',__name__)

@customer.route('/customerhome')
def customerhome():
    # data={}
    return render_template('customerhome.html')

