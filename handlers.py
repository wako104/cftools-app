import scripts as cf
from app import RecordErrorDialog

def handle_connection(api_key, email):
    return cf.validate_key(api_key, email)

def handle_zone_creation(zone_name, account_id):
    response = cf.create_zone(zone_name, account_id)
    if response.status_code != 200:
        error_message = response.json().get('errors', [{}])[0].get('message', 'Unknown Error')
        raise Exception(f'Failed to Add Zone: {error_message}')
    zone_id = response.json()['result']['id']
    name_servers = response.json()['result']['name_servers']
    return zone_id, name_servers

def handle_set_ssl(zone_id):
    response = cf.set_ssl(zone_id, 'strict')
    if response.status_code != 200:
        error_message = response.json().get('errors', [{}])[0].get('message', 'Unknown Error')
        raise Exception(f'Failed to Add Zone: {error_message}')
    
def handle_always_use_https(zone_id):
    response = cf.enable_always_use_https(zone_id)
    if response.status_code != 200:
        error_message = response.json().get('errors', [{}])[0].get('message', 'Unknown Error')
        raise Exception(f'Failed to Add Zone: {error_message}')

def handle_add_dns_records(zone_id, records):
    responses = []
    for record in records:  
        print(f'attempting to add record {record}')
        response = cf.add_dns_record(zone_id, record)
        print(response.json())
        if handle_response(response):
            responses.append(response.json())
    return responses

def handle_response(response):
    if response.status_code != 200:
        return False
    return True
