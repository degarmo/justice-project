import requests
from device_detector import DeviceDetector
from .models import VisitorLog

class VisitorTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        return self.get_response(request)

    def process_request(self, request):
        if request.path.startswith('/admin/') or request.path.startswith('/static/'):
            return

        ip = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        referrer = request.META.get('HTTP_REFERER', '')

        # Device detection
        device_info = DeviceDetector(user_agent).parse()
        browser = device_info.client_name() or ''
        os = device_info.os_name() or ''
        device = device_info.device_type() or ''

        # IPinfo API
        ipinfo_token = 'YOUR_IPINFO_TOKEN'  # <-- Replace with your real token
        geo_data = {}
        try:
            resp = requests.get(f'https://ipinfo.io/{ip}?token={ae202455710ef6}')
            if resp.status_code == 200:
                geo_data = resp.json()
        except Exception:
            pass

        VisitorLog.objects.create(
            ip_address=ip,
            isp=geo_data.get('org', ''),
            asn=geo_data.get('asn', {}).get('asn', '') if geo_data.get('asn') else '',
            city=geo_data.get('city', ''),
            region=geo_data.get('region', ''),
            country=geo_data.get('country', ''),
            latitude=float(geo_data.get('loc', ',').split(',')[0]) if 'loc' in geo_data else None,
            longitude=float(geo_data.get('loc', ',').split(',')[1]) if 'loc' in geo_data else None,
            browser=browser,
            os=os,
            device=device,
            vpn_status=('privacy' in geo_data and geo_data['privacy'].get('vpn', False)),
            tor_status=('privacy' in geo_data and geo_data['privacy'].get('tor', False)),
            referrer=referrer,
            user_agent=user_agent
        )

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
