from flask import *
from database import *
import demjson
import uuid
from datetime import datetime

api = Blueprint('api',__name__)

@api.before_request
def beep():
	import winsound
	winsound.Beep(2500,100)


@api.route('/login',methods=['get','post'])
def login():
	data={}
	# data.update(request.args)
	username = request.args['uname']
	password = request.args['pass']
	q = "select * from login where uname='%s' and password='%s'" % (username,password)
	res = select(q)
	if(len(res) > 0):
		data['status']  = 'success'
		data['data'] = res
	else:
		data['status']	= 'failed'
	return  demjson.encode(data)