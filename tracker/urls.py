
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from tracker import views

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
    path('memorial/', views.memorial_page, name='memorial_page'),
    path('debug/messages/', views.confirm_message_log, name='confirm_message_log'),
    path('memory-map/', views.memory_map, name='memory_map'),

]

# Serve media files during development (only when DEBUG = True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
