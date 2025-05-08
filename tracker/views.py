from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from .models import VisitorLog, TipSubmission, BehavioralLog, MessageOfLove
from .forms import TipSubmissionForm, MessageOfLoveForm
import json
import json, requests
import requests
from django.contrib.admin.views.decorators import staff_member_required
from .models import MessageOfLove
from tracker.utils.ai_analysis import analyze_behavior
from django.shortcuts import redirect
from tracker.models import VisitorLog
from tracker.utils import get_current_visitor


def get_ip_data(ip):
    try:
        response = requests.get(f'https://ipapi.co/{ip}/json/')
        print(response.text)
        if response.status_code == 200:
            data = response.json()
            if 'error' not in data:
                return data
    except Exception as e:
        print(f"IP lookup failed: {e}")
    return {
        'org': '',
        'asn': '',
        'city': '',
        'region': '',
        'country_name': '',
        'latitude': None,
        'longitude': None
    }


@csrf_exempt
def log_visitor(request):
    if request.method == 'POST':
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR')).split(',')[0]
        ip_data = get_ip_data(ip)

        VisitorLog.objects.create(
            ip_address=ip,
            isp=ip_data.get('org'),
            asn=ip_data.get('asn'),
            city=ip_data.get('city'),
            region=ip_data.get('region'),
            country=ip_data.get('country_name'),
            latitude=ip_data.get('latitude'),
            longitude=ip_data.get('longitude'),
            # other fields...
        )
        return JsonResponse({'status': 'visitor logged'})
    return JsonResponse({'error': 'Invalid method'}, status=405)



def index(request):
    visitor_ip = get_client_ip(request)
    visitor_log = VisitorLog.objects.filter(ip_address=visitor_ip).order_by('-timestamp').first()
    latest_post = BlogPost.objects.order_by('-created_at').first()



    if request.method == 'POST':
        form = TipSubmissionForm(request.POST)
        if form.is_valid():
            tip = form.save(commit=False)
            tip.visitor_log = visitor_log  # Link to visitor log
            tip.save()
            print("Tip saved:", tip)  # Debug line
            return redirect('index')
    else:
        form = TipSubmissionForm()

    return render(request, 'tracker/index.html', {'form': form})


def visitor_logs_api(request):
    logs = VisitorLog.objects.all().values(
        'ip_address', 'isp', 'asn', 'city', 'region', 'country',
        'latitude', 'longitude', 'browser', 'os', 'device',
        'vpn_status', 'tor_status', 'fingerprint_hash',
        'referrer', 'user_agent', 'timestamp'
    )
    return JsonResponse(list(logs), safe=False)


def tip_submissions_api(request):
    tips = TipSubmission.objects.select_related('visitor_log').all()
    data = []
    for tip in tips:
        log = tip.visitor_log
        data.append({
            'name': tip.name,
            'email': tip.email,
            'phone': tip.phone,
            'message': tip.message,
            'timestamp': tip.timestamp,
            # VisitorLog data
            'ip_address': log.ip_address if log else None,
            'isp': log.isp if log else None,
            'asn': log.asn if log else None,
            'city': log.city if log else None,
            'region': log.region if log else None,
            'country': log.country if log else None,
            'latitude': log.latitude if log else None,
            'longitude': log.longitude if log else None,
            'browser': log.browser if log else None,
            'os': log.os if log else None,
            'device': log.device if log else None,
            'vpn_status': log.vpn_status if log else None,
            'tor_status': log.tor_status if log else None,
            'fingerprint_hash': log.fingerprint_hash if log else None,
            'referrer': log.referrer if log else None,
            'user_agent': log.user_agent if log else None,
        })
    return JsonResponse(data, safe=False)




@csrf_exempt
def log_behavior(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR')).split(',')[0]

            print("💬 Received behavior data:", data)
            print("🌐 IP Address:", ip)

            # Find visitor based on IP (optional: fingerprint later)
            visitor = VisitorLog.objects.filter(ip_address=ip).order_by('-timestamp').first()

            if visitor:
                BehavioralLog.objects.create(
                    visitor=visitor,
                    event_type=data.get('type'),
                    data=data
                )
                return JsonResponse({'status': 'behavior logged'})
            else:
                print("⚠️ Visitor not found")
                return JsonResponse({'error': 'Visitor not found'}, status=404)

        except Exception as e:
            print("❌ Error parsing behavior data:", str(e))
            return JsonResponse({'error': 'Bad request', 'details': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid method'}, status=405)


@csrf_exempt
def fingerprint_log(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print('Received fingerprint data:', data)  # <-- log it for review

            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR')).split(',')[0]
            visitor = VisitorLog.objects.filter(ip_address=ip).order_by('-timestamp').first()

            if visitor:
                visitor.fingerprint_hash = data.get('fingerprint_hash')
                visitor.timezone = data.get('timezone')
                visitor.screen_resolution = data.get('screen_resolution')
                visitor.color_depth = data.get('color_depth')
                visitor.languages = data.get('languages')
                visitor.platform = data.get('platform')
                visitor.touch_support = data.get('touch_support', False)
                visitor.adblocker = data.get('adblocker', False)
                visitor.incognito = data.get('incognito', False)
                visitor.save()

                return JsonResponse({'status': 'fingerprint logged'})
            else:
                return JsonResponse({'error': 'Visitor not found'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid method'}, status=405)



def report_view(request):
    visitors = VisitorLog.objects.all()
    behaviors = BehavioralLog.objects.all()
    tips = TipSubmission.objects.all()
    # Example: Combine as needed
    data = {
        'visitors': serialize('json', visitors),
        'behaviors': serialize('json', behaviors),
        'tips': serialize('json', tips),
    }
    return JsonResponse(data)

from django.shortcuts import render, get_object_or_404
from .models import BlogPost

def blog_list(request):
    posts = BlogPost.objects.order_by('-created_at')
    return render(request, 'tracker/blog_list.html', {'posts': posts})

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    return render(request, 'tracker/blog_detail.html', {'post': post})

def home_with_latest_post(request):
    latest_post = BlogPost.objects.order_by('-created_at').first()
    return render(request, 'tracker/index.html', {'latest_post': latest_post})

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    return render(request, 'tracker/blog_detail.html', {'post': post})

def index(request):
    latest_post = BlogPost.objects.order_by('-created_at').first()
    return render(request, 'tracker/index.html', {
        'form': TipSubmissionForm(),
        'latest_post': latest_post
    })




def memorial_page(request):
    if request.method == 'POST':
        form = MessageOfLoveForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.visitor = get_current_visitor(request)  # You need to define this function
            message.save()
            return redirect('memory_map')  # Make sure your URL name is correct
    else:
        form = MessageOfLoveForm()
    return render(request, 'tracker/memorial_page.html', {'form': form})

    messages = MessageOfLove.objects.all().order_by('-created_at')
    return render(request, 'tracker/memorial_page.html', {'form': form, 'messages': messages})


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

def confirm_message_log(request):
    messages = MessageOfLove.objects.all().order_by('-created_at')[:100]
    return render(request, 'tracker/confirm_data.html', {'messages': messages})

import json
from django.core.serializers.json import DjangoJSONEncoder

def memory_map(request):
    messages = MessageOfLove.objects.filter(show_location=True, latitude__isnull=False, longitude__isnull=False)
    messages_json = json.dumps([
        {
            'display_name': msg.display_name,
            'city': msg.city,
            'state': msg.state,
            'message': msg.message,
            'latitude': msg.latitude,
            'longitude': msg.longitude,
            'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M')
        } for msg in messages
    ], cls=DjangoJSONEncoder)
    
    return render(request, 'tracker/memory_map.html', {
        'messages': messages,
        'messages_json': messages_json
    })

