import json
import random
import urllib.request
import urllib.parse
import time



responser_table = {}
authentication_table = {}

partner_id = ''



def responser(json_object):
	request_type = json_object['request_type']
	#if(request_type != 'request_type_sign_in'):
		# authenticate the request
		# if(json_object['authentication'] not in authentication_table):
		#	json_reply_object = {}
		#	json_reply_object['return_code'] = 0
		#	json_reply_object['error_message'] = 'Authentication failed.'
		#	json_reply_object['data'] = {}
		#	return json.dumps(json_reply_object)
	#call the responser
	return responser_table[request_type](json_object['data'])



# -----------------------------------------------------------------------------
# responser for sign-in-request
def sign_in_responser(data=None):
	# open the account file
	if(data['sign_in_type']):	# login as a student
		account_file = open('student_account')
	else:				# login as a teacher
		account_file = open('teacher_account')

	# authenticate the sign in information
	try:
		# store the account info in a dictionary
		account_dict = {}
		for line in account_file:
			line = line.split()
			account_dict[line[0]] = line[1]

		# authenticate and assemble the response info
		if(account_dict[data['account']] == data['password']):
			json_reply_object = {}
			json_reply_object['return_code'] = 1
			json_reply_object['error_message'] = ''
			json_reply_data = {}

			# generate authentication code and store in a global table
			authentication = random.randint(0, 1023)
			authentication_table[data['account']] = authentication
			
			json_reply_data['authentication'] = authentication
			json_reply_object['data'] = json_reply_data
			return json.dumps(json_reply_object)
		else:
			pass

	#close the account file
	finally:
		account_file.close()
responser_table['request_type_sign_in'] = sign_in_responser



# -----------------------------------------------------------------------------
#responser for create-room-request
def create_room_responser(data=None):
	# assemble the request data
	call_api_dict = {}
	call_api_dict['title'] = data['title']
	call_api_dict['start_time'] = time_string_to_unix_timestamp(data['start_time'])
	call_api_dict['end_time'] = time_string_to_unix_timestamp(data['end_time'])
	call_api_dict['timestamp'] = int(time.time())
	# calculate the sign used to call API
	call_api_sign = calculate_sign(call_api_dict)
	call_api_dict['partner_id'] = partner_id
	call_api_dict['sign'] = call_api_sign

	# post the create-room-request to the Baijiacloud server
	request_data = urllib.parse.urlencode(call_api_dict)
	request_data = request_data.encode('ascii')
	url_create_room = 'https://api.baijiayun.com/openapi/room/create'
	request_result = urllib.request.urlopen(url_create_room, request_data)
	# get the return json object in the string format
	result_string = request_result.read().decode('utf-8')
	result_object = json.loads(result_string)

	#assemble the response info
	json_reply_object = {}
	json_reply_object['return_code'] = 1
	json_reply_object['error_message'] = ''
	json_reply_object['data'] = {'room_id': result_object['room_id']} 

	return json.dumps(json_reply_object)
	
responser_table['request_type_create_room'] = create_room_responser



# -----------------------------------------------------------------------------
#responser for update-room-request
def update_room_responser(data=None):
	pass
responser_table['request_type_update_room'] = update_room_responser



# -----------------------------------------------------------------------------
#responser for delete room
def delete_room_responser(data=None):
	pass
responser_table['request_type_delete_room'] = delete_room_responser



# -----------------------------------------------------------------------------
# Function that convert time from string to UNIX timestamp
def time_string_to_unix_timestamp(string):
	format = '%Y-%m-%d %H:%m'
	return int(time.mktime(time.strptime(string, format)))
