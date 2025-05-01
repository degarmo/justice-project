from django import template

register = template.Library()

@register.simple_tag
def get_visitor(detailed_data, ip, fingerprint):
    ip_data = detailed_data.get(ip)
    if ip_data:
        return ip_data.get(fingerprint)
    return None
