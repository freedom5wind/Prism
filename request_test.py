import urllib.request
import urllib.parse
import json



url = 'http://127.0.0.1:5000'



# assemble the json request object and dump it into a string

# -----------------------------------------------------------------------------
# Test for request_type_sign_in

# json_request_object = {}
# json_request_object['request_type'] = 'request_type_sign_in'
# json_request_object['authentication'] = 0
# json_request_object['data'] = {'account':'teacher_test', 'password':'123456', 'sign_in_type':0}
# json_string = json.dumps(json_request_object)

# -----------------------------------------------------------------------------
# Test for request_type_create_room
json_request_object = {}
json_request_object['request_type'] = 'request_type_create_room'
json_request_object['authentication'] = 0	# Authentication will be disabled during the single creating room request test
d = {}
d['title'] = 'server-side test'
d['start_time'] = '2017-11-24 9:00'
d['end_time'] = '2017-11-24  10:00'
json_request_object['data'] = d



# parse the json_string according https://docs.python.org/3.6/library/urllib.request.html#urllib-examples
data = urllib.parse.urlencode({'json_string':json_string})
data = data.encode('ascii')
with urllib.request.urlopen(url, data) as f:
	print(f.read().decode('utf-8'))
