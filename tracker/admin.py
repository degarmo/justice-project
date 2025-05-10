from django.contrib import admin
from django.urls import path, reverse
from django.template.response import TemplateResponse
from django.utils.html import format_html
from django.db.models import Count
from datetime import datetime, timedelta
from django.utils.timezone import make_aware, now
from .models import VisitorLog, TipSubmission, BehavioralLog, MessageOfLove, BlogPost
from django.contrib.contenttypes.models import ContentType
from tracker.utils.ai_analysis import analyze_behavior
from django.db.models import Max

# TipSubmission Admin
@admin.register(TipSubmission)
class TipSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'email', 'phone', 'timestamp',
        'get_ip_address', 'get_vpn_status', 'get_tor_status',
        'get_browser', 'get_os', 'get_device'
    )
    readonly_fields = ('visitor_log', 'timestamp', 'visitor_metadata')

    def get_ip_address(self, obj): return obj.visitor_log.ip_address if obj.visitor_log else None
    get_ip_address.short_description = 'IP Address'

    def get_vpn_status(self, obj): return obj.visitor_log.vpn_status if obj.visitor_log else None
    get_vpn_status.short_description = 'VPN?'

    def get_tor_status(self, obj): return obj.visitor_log.tor_status if obj.visitor_log else None
    get_tor_status.short_description = 'Tor?'

    def get_browser(self, obj): return obj.visitor_log.browser if obj.visitor_log else None
    get_browser.short_description = 'Browser'

    def get_os(self, obj): return obj.visitor_log.os if obj.visitor_log else None
    get_os.short_description = 'OS'

    def get_device(self, obj): return obj.visitor_log.device if obj.visitor_log else None
    get_device.short_description = 'Device'

    def visitor_metadata(self, obj):
        if not obj.visitor_log:
            return "No visitor data."
        log = obj.visitor_log
        return format_html(
            "<b>IP:</b> {}<br><b>ISP:</b> {}<br><b>ASN:</b> {}<br><b>City:</b> {}<br><b>Region:</b> {}<br><b>Country:</b> {}<br>"
            "<b>Latitude:</b> {}<br><b>Longitude:</b> {}<br><b>Browser:</b> {}<br><b>OS:</b> {}<br><b>Device:</b> {}<br>"
            "<b>VPN:</b> {}<br><b>Tor:</b> {}<br><b>Fingerprint:</b> {}<br><b>Referrer:</b> {}<br><b>User Agent:</b> {}",
            log.ip_address, log.isp, log.asn, log.city, log.region, log.country,
            log.latitude, log.longitude, log.browser, log.os, log.device,
            "Yes" if log.vpn_status else "No", "Yes" if log.tor_status else "No",
            log.fingerprint_hash, log.referrer, log.user_agent
        )
    visitor_metadata.short_description = "Visitor Metadata"


# BehavioralLog Admin
@admin.register(BehavioralLog)
class BehavioralLogAdmin(admin.ModelAdmin):
    list_display = ('get_visitor_ip', 'event_type', 'timestamp')
    list_filter = ('event_type',)
    search_fields = ('visitor__ip_address', 'event_type')

    def get_visitor_ip(self, obj):
        return obj.visitor.ip_address
    get_visitor_ip.short_description = 'Visitor IP'


# Report View Admin
class ReportAdminView(admin.ModelAdmin):
    change_list_template = 'admin/tracker/report.html'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('report/', self.admin_site.admin_view(self.report_view), name='tracker_report'),
        ]
        return custom_urls + urls

    def report_view(self, request):
        context = dict(
            self.admin_site.each_context(request),
            title='Visitor Behavior Report',
        )

        visitors = VisitorLog.objects.none()
        detailed_data = {}

        if request.GET.get('start') and request.GET.get('end'):
            try:
                start_date = datetime.strptime(request.GET.get('start'), '%Y-%m-%d')
                end_date = datetime.strptime(request.GET.get('end'), '%Y-%m-%d') + timedelta(days=1)
                start_date = make_aware(start_date)
                end_date = make_aware(end_date)

                visitors = VisitorLog.objects.filter(timestamp__range=[start_date, end_date])
                tips = TipSubmission.objects.filter(timestamp__range=[start_date, end_date])
                behaviors = BehavioralLog.objects.filter(timestamp__range=[start_date, end_date])

                visit_counts = visitors.values('ip_address', 'fingerprint_hash').annotate(visits=Count('id'))

                for visitor in visitors:
                    ip = visitor.ip_address or "Unknown IP"
                    fp = visitor.fingerprint_hash or "Unknown FP"
                    detailed_data.setdefault(ip, {})[fp] = {
                        'visitor': visitor,
                        'tips': tips.filter(visitor_log=visitor),
                        'behaviors': behaviors.filter(visitor=visitor),
                    }

                vpn_count = visitors.filter(vpn_status=True).count()
                tor_count = visitors.filter(tor_status=True).count()

                ai_summary = f"""
                Between {start_date.date()} and {(end_date - timedelta(days=1)).date()}:
                - {visitors.count()} unique visitors detected.
                - {vpn_count} visitors used VPN, {tor_count} used TOR.
                - Behavioral patterns flagged for impulsive and curious behaviors.
                """

                context.update({
                    'visit_counts': visit_counts,
                    'ai_summary': ai_summary,
                    'start_date': start_date.date(),
                    'end_date': (end_date - timedelta(days=1)).date(),
                    'detailed_data': detailed_data,
                })

            except ValueError:
                context['error'] = "Invalid date format."

        return TemplateResponse(request, "admin/tracker/report.html", context)


# Admin override for dashboard behavior
class CustomAdminSite(admin.AdminSite):
    site_header = "Tracker Admin Portal"

    def index(self, request, extra_context=None):
        if not extra_context:
            extra_context = {}

        cutoff_time = now() - timedelta(hours=72)
        recent_visitors = VisitorLog.objects.filter(timestamp__gte=cutoff_time)

        nervous_visitors = []

        for visitor in recent_visitors:
            behaviors = BehavioralLog.objects.filter(visitor=visitor)
            if behaviors.exists():
                score = analyze_behavior(visitor, behaviors)
                if score >= 5:
                    nervous_visitors.append({
                        'visitor': visitor,
                        'score': score,
                    })

        extra_context['nervous_visitors'] = nervous_visitors
        return super().index(request, extra_context=extra_context)


class VisitorLogReport(admin.ModelAdmin):
    list_display = [
        'fingerprint_link', 'first_seen', 'last_seen', 'visit_count',
        'has_tip', 'has_signed', 'has_gps', 'score', 'notes',
    ]
    readonly_fields = list_display

    def get_queryset(self, request):
        # Step 1: Get latest entry for each unique fingerprint
        latest_ids = VisitorLog.objects.values('fingerprint_hash').annotate(
            latest_id=Max('id')
        ).values_list('latest_id', flat=True)

        # Step 2: Filter queryset to just those IDs
        return VisitorLog.objects.filter(id__in=latest_ids)

    def fingerprint_link(self, obj):
        return obj.fingerprint_hash or obj.ip_address

    def first_seen(self, obj):
        return obj.timestamp

    def last_seen(self, obj):
        return obj.behavior_logs.order_by('-timestamp').first().timestamp if obj.behavior_logs.exists() else obj.timestamp

    def visit_count(self, obj):
        return obj.behavior_logs.count()

    def has_tip(self, obj):
        return TipSubmission.objects.filter(visitor_log=obj).exists()

    def has_signed(self, obj):
        return MessageOfLove.objects.filter(visitor=obj).exists()

    def has_gps(self, obj):
        return any([
            obj.latitude is not None,
            MessageOfLove.objects.filter(visitor=obj, latitude__isnull=False).exists()
        ])

    def score(self, obj):
        score = 10
        if obj.vpn_status or obj.tor_status:
            score -= 3
        if not self.has_signed(obj):
            score -= 2
        if not self.has_gps(obj):
            score -= 1
        return max(score, 0)

    def notes(self, obj):
        notes = []
        if obj.vpn_status or obj.tor_status:
            notes.append("⚠️ Anonymization tools detected")
        if not self.has_signed(obj):
            notes.append("No public engagement")
        if not self.has_gps(obj):
            notes.append("No geolocation")
        return ", ".join(notes) if notes else "Normal visitor"

admin.site.register(VisitorLog, VisitorLogReport)