from django.db import models
from django.utils.text import slugify

class VisitorLog(models.Model):
    ip_address = models.CharField(max_length=45)
    isp = models.CharField(max_length=255, null=True, blank=True)
    asn = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    browser = models.CharField(max_length=255, null=True, blank=True)
    os = models.CharField(max_length=255, null=True, blank=True)
    device = models.CharField(max_length=255, null=True, blank=True)
    vpn_status = models.BooleanField(default=False)
    tor_status = models.BooleanField(default=False)
    referrer = models.CharField(max_length=2048, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # 🔥 Fingerprint-related fields
    fingerprint_hash = models.CharField(max_length=255, null=True, blank=True)
    timezone = models.CharField(max_length=100, null=True, blank=True)
    screen_resolution = models.CharField(max_length=50, null=True, blank=True)
    color_depth = models.IntegerField(null=True, blank=True)
    languages = models.JSONField(null=True, blank=True)
    platform = models.CharField(max_length=255, null=True, blank=True)
    touch_support = models.BooleanField(default=False)
    adblocker = models.BooleanField(default=False)
    incognito = models.BooleanField(default=False)


class TipSubmission(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField()
    visitor_log = models.ForeignKey(VisitorLog, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class BehavioralLog(models.Model):
    visitor = models.ForeignKey(VisitorLog, on_delete=models.CASCADE, related_name='behavior_logs')
    event_type = models.CharField(max_length=50)
    data = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.visitor.ip_address} - {self.event_type} @ {self.timestamp}"


# tracker/models.py


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# Message Of Love
class MessageOfLove(models.Model):
    visitor = models.ForeignKey('VisitorLog', on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    message = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    show_location = models.BooleanField(default=False)
    shared_social = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


