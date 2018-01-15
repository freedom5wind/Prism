import requests

data={}
data['request_type']='request_type_sign_in'
data['authentication']=0
data['data']={}
data['data']['account']='teacher_test'
data['data']['password']='123456'
data['data']['sign_in_type']=0
req = requests.post('http://45.78.19.59:5000', data=data)
print(req.text)
