from flask import Flask
from flask.ext.cors import CORS
from flask import request
import json

from my_responser import responser

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET', 'POST'])
def my_server():
	if request.method == 'POST':

		# get the request dictionary from request.form
		string =  ''
		for i in request.form.keys():
			string += str(i)

		# deal with the exception
		try:
			obj = json.loads(string)
		except JSONDecodeError:
			return "Error:bad request syntax."

		return responser(obj)
	else:
		return "Error:please request data by 'POST'"
