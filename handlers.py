import scripts as cf
from app import RecordErrorDialog

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

def handle_add_dns_records(zone_id, records):
    responses = []
    for record in records:
        while True:     
            response = cf.add_dns_record(zone_id, record)
            action = handle_response(response)
            if action == 'retry':
                continue
            elif action == 'skip':
                break
            elif action == 'abort':
                return
            elif action == True:
                responses.append(response.json())
                break
    return responses

def handle_response(response):
    if response.status_code != 200:
        error_message = response.json().get('errors', [{}])[0].get('message', 'Unknown Error')
        result = response.json()['result']
        error_dialog = RecordErrorDialog(None, f'Failed to add DNS Record {result['type']} | {result['name']} | {result['content']}: {error_message}')
        action = error_dialog.show()
        return action
    return True
