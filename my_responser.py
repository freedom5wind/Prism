import json
import random
import urllib.request
import urllib.parse
import time
import hashlib
import pymysql



responser_table = {}
authentication_table = {}

partner_id = '33227392'
partner_key = 'hlQtoKynWKTvG5/PGiQL6UxAit9ABu3yK7Hvew0U0uSxTovXqGeEDz3Tw9iVyDcmbbIhQ5SGXXnt2wrSOz2N7g=='



def responser(json_object):

	print(json_object)
	if('request_type' not in json_object):
		return 'Lack of request type!'

	request_type = json_object['request_type']

	if(request_type != 'request_type_sign_in'):
		# authenticate the request
		db = pymysql.connect('localhost', 'root', 'Wlf5', 'account')
		cursor = db.cursor()
		sql = 'select timestamp from account where token=%d' % json_object['authentication']
		cursor.execute(sql)
		result_data = cursor.fetchone()
		if(result_data == None):
			json_reply_object = {}
			json_reply_object['return_code'] = 1
			json_reply_object['error_message'] = 'Authentication failed.'
			json_reply_object['data'] = {}
			return json.dumps(json_reply_object)
		elif(int(time.time()) - result_data[0] > 7200):
			json_reply_object = {}
			json_reply_object['return_code'] = 1
			json_reply_object['error_message'] = 'Login overtimed.'
			json_reply_object['data'] = {}
			return json.dumps(json_reply_object)

	#call the responser
	if(request_type not in responser_table):
		return 'Invalid request type!'
	elif('data' not in json_object):
		return 'Lack of request data!'
	else:
		try:
			return responser_table[request_type](json_object['data'])
		except:
			raise
			return 'Something go wrong!'



# -----------------------------------------------------------------------------
# Function that convert time from string to UNIX timestamp
def time_string_to_unix_timestamp(string):
	format = '%Y-%m-%d %H:%M'
	return int(time.mktime(time.strptime(string, format)))



# -----------------------------------------------------------------------------
# Function that convert time from UNIX timestamp to strng
def time_unix_timestamp_to_string(timestamp):
	format = '%Y-%m-%d %H:%M'
	return time.strftime(format, time.localtime(timestamp))



# -----------------------------------------------------------------------------
# Function that calculate sign for the request to Baijiacloud server
def calculate_sign(call_api_dict):
	global partner_key

	# assemble the request parameters
	key_table = sorted(iter(call_api_dict))
	request_string = ''
	for i in key_table:
		request_string += str(i) + '=' + str(call_api_dict[i]) + '&'
	request_string += 'partner_key=' + partner_key
	
	# calculate the md5	
	md5_obj = hashlib.md5()
	md5_obj.update(request_string.encode('utf-8'))
	return md5_obj.hexdigest()



# -----------------------------------------------------------------------------
# Function that generate call-api-dict
def generate_call_api_dict(data):
	global partner_id

	# assemble the request data
	call_api_dict = {}
	call_api_dict['partner_id'] = partner_id
	# put data in data to the dict
	if(data != None):
		for i in data:
			call_api_dict[i] = data[i]
	# convert the time into UNIX timestamp if needed
	if('start_time' in call_api_dict):
		call_api_dict['start_time'] = time_string_to_unix_timestamp(call_api_dict['start_time'])
	if('end_time' in call_api_dict):
		call_api_dict['end_time'] = time_string_to_unix_timestamp(call_api_dict['end_time'])
	call_api_dict['timestamp'] = int(time.time())
	# calculate the sign used to call API
	call_api_sign = calculate_sign(call_api_dict)
	call_api_dict['sign'] = call_api_sign

	return call_api_dict



# -----------------------------------------------------------------------------
# Function that send the request to the Baijiacloud server
def send_request(call_api_dict, url):
	# post the create-room-request to the Baijiacloud server
	request_data = urllib.parse.urlencode(call_api_dict)
	request_data = request_data.encode('ascii')
	request_result = urllib.request.urlopen(url, request_data)
	# get the return json object in the string format
	result_string = request_result.read().decode('utf-8')
	result = json.loads(result_string)

	return result



# -----------------------------------------------------------------------------
# responser for sign-in-request
def sign_in_responser(data=None):

	database = pymysql.connect('localhost', 'root', 'Wlf5', 'account')
	cursor = database.cursor()
	cursor.execute("select password from account where account='" + str(data['account']) + "' and type=" + str(data['sign_in_type']))
	mysql_result = cursor.fetchone()
	json_reply_object = {}
	if(mysql_result == None):
		json_reply_object['return_code'] = 1
		json_reply_object['error_message'] = 'Account not found.'
		json_reply_object['data'] = {}
	elif(mysql_result[0] != data['password']):
		json_reply_object['return_code'] = 1
		json_reply_object['error_message'] = 'Password is wrong.'
		json_reply_object['data'] = {}
	else:
		json_reply_object['return_code'] = 0
		json_reply_object['error_message'] = ''
		token = random.randint(0, 65535)
		json_reply_object['data'] = {'authentication' : token}
		sql = "update account set token=%d where account='%s'" % (token, data['account'])
		try:
			cursor.execute(sql)
			database.commit()
		except:
			database.rollback()
			raise
		sql = "update account set timestamp=%d where account='%s'" % (int(time.time()), data['account'])
		try:
			cursor.execute(sql)
			database.commit()
		except:
			database.rollback()
			raise
	
	database.close()

	print(json_reply_object)	
	return json.dumps(json_reply_object)
	


responser_table['request_type_sign_in'] = sign_in_responser



# -----------------------------------------------------------------------------
#responser for create-room-request
def create_room_responser(data=None):

	call_api_dict = generate_call_api_dict(data)
	url = 'https://api.baijiayun.com/openapi/room/create'
	result = send_request(call_api_dict, url)

	#assemble the response info
	json_reply_object = {}
	json_reply_object['return_code'] = result['code']
	json_reply_object['error_message'] = result['msg']
	if(result['data'] != None):
		if('room_id' in result['data']):
			json_reply_object['data'] = {'room_id' : result['data']['room_id']} 
	print(json_reply_object)
	return json.dumps(json_reply_object)
	
responser_table['request_type_create_room'] = create_room_responser



# -----------------------------------------------------------------------------
#responser for update-room-request
def update_room_responser(data=None):

	call_api_dict = generate_call_api_dict(data)
	url = 'https://api.baijiayun.com/openapi/room/update'
	result = send_request(call_api_dict, url)

	#assemble the response info
	json_reply_object = {}
	json_reply_object['return_code'] = result['code']
	json_reply_object['error_message'] = result['msg']
	json_reply_object['data'] = {} 

	print(json_reply_object)
	return json.dumps(json_reply_object)

responser_table['request_type_update_room'] = update_room_responser



# -----------------------------------------------------------------------------
#responser for delete-room-request
def delete_room_responser(data=None):

	call_api_dict = generate_call_api_dict(data)
	url = 'https://api.baijiayun.com/openapi/room/delete'
	result = send_request(call_api_dict, url)

	#assemble the response info
	json_reply_object = {}
	json_reply_object['return_code'] = result['code']
	json_reply_object['error_message'] = result['msg']
	json_reply_object['data'] = {} 

	print(json_reply_object)
	return json.dumps(json_reply_object)

responser_table['request_type_delete_room'] = delete_room_responser



# -----------------------------------------------------------------------------
# responser for get-room-info-request
def get_room_info_responser(data=None):

	call_api_dict = generate_call_api_dict(data)
	url = 'https://api.baijiayun.com/openapi/room/info'
	result = send_request(call_api_dict, url)

	#assemble the response info
	json_reply_object = {}
	json_reply_object['return_code'] = result['code']
	json_reply_object['error_message'] = result['msg']
	if(result['data'] != None):
		del result['data']['admin_code']
		del result['data']['teacher_code']
		json_reply_object['data'] = result['data']

	print(json_reply_object)
	return json.dumps(json_reply_object)

responser_table['request_type_get_room_info'] = get_room_info_responser



# -----------------------------------------------------------------------------
# responser for get-room-list-request
def get_room_list_responser(data=None):

	call_api_dict = generate_call_api_dict(data)
	url = 'https://api.baijiayun.com/openapi/room/list'
	result = send_request(call_api_dict, url)

	#assemble the response info
	json_reply_object = {}
	json_reply_object['return_code'] = result['code']
	json_reply_object['error_message'] = result['msg']
	for i in result['data']['list']:
		del i['admin_code']
		del i['teacher_code']
		del i['student_code']
		i['start_time'] = time_unix_timestamp_to_string(i['start_time'])
		i['end_time'] = time_unix_timestamp_to_string(i['end_time'])
		i['create_time'] = time_unix_timestamp_to_string(i['create_time'])
	json_reply_object['data'] = result['data']

	print(json_reply_object)
	return json.dumps(json_reply_object)

responser_table['request_type_get_room_list'] = get_room_list_responser



# -----------------------------------------------------------------------------
# responser for calculate-url-request
def calculate_url_responser(data=None):

	sign = calculate_sign(data)
	url = 'http://www.baijiayun.com/web/room/enter?'
	for i in data:
		url += str(i) + '=' + str(urllib.parse.quote(str(data[i]))) + '&'
	url += 'sign=' + str(sign)

	# assemble the request  info
	json_reply_object = {}
	json_reply_object['return_code'] = 0
	json_reply_object['error_message'] = ''
	json_reply_object['data'] = {'url':url}

	print(json_reply_object)
	return json.dumps(json_reply_object)

responser_table['request_type_calculate_url'] = calculate_url_responser



# -----------------------------------------------------------------------------
# responser for get-replay-list-request
def get_replay_list_responser(data=None):

	call_api_dict = generate_call_api_dict(data)
	url = 'https://api.baijiayun.com/openapi/playback/getList'
	result = send_request(call_api_dict, url)

	#assemble the response info
	json_reply_object = {}
	json_reply_object['return_code'] = result['code']
	json_reply_object['error_message'] = result['msg']
	json_reply_object['data'] = result['data']

	return json.dumps(json_reply_object)

responser_table['request_type_get_replay_list'] = get_replay_list_responser



# -----------------------------------------------------------------------------
# responser for get-replay-token-request
def get_replay_token_responser(data=None):

	call_api_dict = generate_call_api_dict(data)
	url = 'https://api.baijiayun.com/openapi/playback/getPlayerToken'
	result = send_request(call_api_dict, url)

	#assemble the response info
	json_reply_object = {}
	json_reply_object['return_code'] = result['code']
	json_reply_object['error_message'] = result['msg']
	json_reply_object['data'] = result['data']

	return json.dumps(json_reply_object)

responser_table['request_type_get_replay_token'] = get_replay_token_responser



# -----------------------------------------------------------------------------
# responser for get-replay-tokens-request
def get_replay_tokens_responser(data=None):

	call_api_dict = generate_call_api_dict(data)
	url = 'https://api.baijiayun.com/openapi/playback/getPlayerTokenBatch'
	result = send_request(call_api_dict, url)

	#assemble the response info
	json_reply_object = {}
	json_reply_object['return_code'] = result['code']
	json_reply_object['error_message'] = result['msg']
	json_reply_object['data'] = result['data']

	return json.dumps(json_reply_object)

responser_table['request_type_get_replay_tokens'] = get_replay_tokens_responser



