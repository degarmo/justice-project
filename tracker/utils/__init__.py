from tracker.models import VisitorLog

def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip

def get_current_visitor(request):
    ip = get_client_ip(request)
    visitor, _ = VisitorLog.objects.get_or_create(ip_address=ip)
    return visitor
