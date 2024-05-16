import requests

def validate_key(api_key, email):
    headers = {
        'X-Auth-Email': email,
        'X-Auth-Key': api_key,
        'Content-Type': 'application/json'
    }
    url = "https://api.cloudflare.com/client/v4/user"
    response = requests.get(url, headers=headers)
    return response.status_code == 200