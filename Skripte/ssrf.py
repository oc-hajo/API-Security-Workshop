import requests

# TODO: Add correct authenticaiton header 
http_headers = {
    'Authorization': 'Bearer ...',
}


for port in range(1,1024):

    # TODO: Fix this dictionary to match the request made by the Web Application
    json_data = {
        'url': '',
    }
    
    
    # TODO: Use the correct DVAPI endpoint
    url_dvapi = "http://dvapi.local:3000..."
    response = requests.post(
        url_dvapi,
        headers=http_headers,
        json=json_data,
    )

    if "error" not in response.text:
        print(port)
        print(response.text)