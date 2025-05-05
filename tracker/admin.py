from django.contrib import admin
from django.urls import path, reverse
from django.template.response import TemplateResponse
from django.utils.html import format_html
from django.db.models import Count
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from .models import VisitorLog, TipSubmission, BehavioralLog
from django.contrib.contenttypes.models import ContentType
from tracker.utils.ai_analysis import analyze_behavior
from django.utils.timezone import now
from .models import BlogPost



# VisitorLog Admin
@admin.register(VisitorLog)
class VisitorLogAdmin(admin.ModelAdmin):
    list_display = ('ip_address', 'city', 'region', 'country', 'vpn_status', 'tor_status', 'fingerprint_hash', 'timestamp')
    readonly_fields = (
        'ip_address', 'isp', 'asn', 'city', 'region', 'country',
        'latitude', 'longitude', 'browser', 'os', 'device',
        'vpn_status', 'tor_status', 'fingerprint_hash',
        'referrer', 'user_agent', 'timestamp'
    )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['custom_button'] = format_html(
            '<a class="button" href="{}">Generate Report</a>',
            reverse('admin:tracker_report')
        )
        return super().changelist_view(request, extra_context=extra_context)


# TipSubmission Admin
@admin.register(TipSubmission)
class TipSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'email', 'phone', 'timestamp',
        'get_ip_address', 'get_vpn_status', 'get_tor_status',
        'get_browser', 'get_os', 'get_device'
    )
    readonly_fields = ('visitor_log', 'timestamp', 'visitor_metadata')

    def get_ip_address(self, obj):
        return obj.visitor_log.ip_address if obj.visitor_log else None
    get_ip_address.short_description = 'IP Address'

    def get_vpn_status(self, obj):
        return obj.visitor_log.vpn_status if obj.visitor_log else None
    get_vpn_status.short_description = 'VPN?'

    def get_tor_status(self, obj):
        return obj.visitor_log.tor_status if obj.visitor_log else None
    get_tor_status.short_description = 'Tor?'

    def get_browser(self, obj):
        return obj.visitor_log.browser if obj.visitor_log else None
    get_browser.short_description = 'Browser'

    def get_os(self, obj):
        return obj.visitor_log.os if obj.visitor_log else None
    get_os.short_description = 'OS'

    def get_device(self, obj):
        return obj.visitor_log.device if obj.visitor_log else None
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


# Report View
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

                # Build data
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
                if score >= 5:  # Threshold to be considered 'nervous'
                    nervous_visitors.append({
                        'visitor': visitor,
                        'score': score,
                    })

        extra_context['nervous_visitors'] = nervous_visitors
        return super().index(request, extra_context=extra_context)
    
@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ('title',)
    ordering = ('-created_at',)


# Register the report under ContentType
admin.site.register(ContentType, ReportAdminView)
