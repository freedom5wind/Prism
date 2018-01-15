from flask import Flask
from flask import request
import json

from my_responser import responser

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def my_server():
	if request.method == 'POST':
		return responser(request.form)
	else:
		return "Please request data by 'POST'"
