import scripts as cf

def handle_zone_creation(zone_name, account_id):
    zone_id = cf.create_zone(zone_name, account_id)
    if zone_id is None:
        raise Exception('Failed to Add Zone')
    return zone_id

def handle_set_ssl(zone_id):
    if not cf.set_ssl(zone_id, 'strict'):
        raise Exception('Failed to Set SSL')

def handle_add_dns_records(zone_id, records):
    responses = {}
    for record in records:
        response = cf.add_dns_record(zone_id, record)
        handle_response(response)

def handle_response(response):
    pass
