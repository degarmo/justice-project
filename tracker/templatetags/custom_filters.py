from django import template

register = template.Library()

@register.filter(name='get_visitor')
def get_visitor(data_list, ip_fingerprint):
    ip, fingerprint = ip_fingerprint
    for item in data_list:
        if item['visitor'].ip_address == ip and item['visitor'].fingerprint_hash == fingerprint:
            return item['visitor'].fingerprint_hash
    return None

@register.filter(name='get_behaviors')
def get_behaviors(data_list, ip_fingerprint):
    ip, fingerprint = ip_fingerprint
    for item in data_list:
        if item['visitor'].ip_address == ip and item['visitor'].fingerprint_hash == fingerprint:
            return item['behaviors']
    return []

@register.filter(name='get_tips')
def get_tips(data_list, ip_fingerprint):
    ip, fingerprint = ip_fingerprint
    for item in data_list:
        if item['visitor'].ip_address == ip and item['visitor'].fingerprint_hash == fingerprint:
            return item['tips']
    return []
