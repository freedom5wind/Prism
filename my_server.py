from flask import Flask
from flask import request
import json

from my_responser import responser

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def my_server():
	if request.method == 'POST':
		# json_string = request.form['json_string']
		# json_object = json.loads(json_string)
		# return responser(json_object)
		return responser(request.form)
