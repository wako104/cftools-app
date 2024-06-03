import requests
import time

REQUESTS_PER_MINUTE = 80
INTERVAL = 60/REQUESTS_PER_MINUTE

BASE_URL = "https://api.cloudflare.com/client/v4"

# limit request rate, to ensure we don't go over the limit
def rate_limited_request(url, method, **kwargs): 
    time.sleep(INTERVAL)
    response = getattr(requests, method)(url, **kwargs)
    return response

# validate api key and email, test connection to cloudflare
def validate_key(api_key, email):
    global headers 
    headers = {
        'X-Auth-Email': email,
        'X-Auth-Key': api_key,
        'Content-Type': 'application/json'
    }
    url = f'{BASE_URL}/user'
    response = rate_limited_request(url=url, method='get', headers=headers)
    return response.status_code == 200

def get_cloudflare_accounts():
    url = f'{BASE_URL}/accounts'
    response = rate_limited_request(url=url, method='get', headers=headers)
    if response.status_code == 200:
        accounts = response.json()
        return [(account['id'], account['name']) for account in accounts.get('result', [])]
    else:
        print('Failed to retrieve accounts')
        return []

def create_zone(zone_name, account_id):
    payload = {
        'account': {'id': account_id},
        'name': zone_name,
        'type': 'full',
    }
    url = f'{BASE_URL}/zones'
    response = rate_limited_request(url=url, method='post', json=payload, headers=headers)
    return response
    
def set_ssl(zone_id, value):
    payload = {
        'value': value,
    }
    url = f'{BASE_URL}/zones/{zone_id}/settings/ssl'
    response = rate_limited_request(url=url, method='patch', json=payload, headers=headers)
    return response

def add_dns_record(zone_id, record):
    url = f'{BASE_URL}/zones/{zone_id}/dns_records'
    response = rate_limited_request(url=url, method='post', json=record, headers=headers)
    return response