from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from tracker import views  # ✅ this line is missing
from django.contrib import admin
from django.urls import path, include
from tracker import views  # ✅ This line fixes the NameError


urlpatterns = [
    path('', views.index, name='index'),  # Homepage
    path('api/visitor-logs/', views.visitor_logs_api, name='visitor_logs_api'),
    path('api/tip-submissions/', views.tip_submissions_api, name='tip_submissions_api'),
    path('api/behavior-log/', views.log_behavior, name='behavior_log'),
    path('api/fingerprint-log/', views.fingerprint_log, name='fingerprint_log'),
    path('log-behavior/', views.log_behavior, name='log_behavior'),
    
    
    # Blog URLs
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
]

# Serve media files during development (only when DEBUG = True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
