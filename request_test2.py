import urllib.request
import urllib.parse

data={}
data['request_type']='request_type_sign_in'
data['authentication']=0
data['data']={}
data['data']['account']='teacher_test'
data['data']['password']='123456'
data['data']['sign_in_type']=0

data = urllib.parse.urlencode(data)
data = data.encode('utf-8')
request = urllib.request.Request("http://45.78.19.59:5000")
# adding charset parameter to the Content-Type header.
request.add_header("Content-Type","application/x-www-form-urlencoded;charset=utf-8")
f = urllib.request.urlopen(request, data)
print(f.read().decode('utf-8'))
