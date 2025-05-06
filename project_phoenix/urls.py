from django.contrib import admin
from django.urls import path, include
from tracker import views  # ✅ This is the missing import

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tracker.urls')),
    path('log-behavior/', views.log_behavior, name='log_behavior'), 
    # urls.py
    path('memorial/', views.memorial_page, name='memorial_page'),
    path('debug/messages/', views.confirm_message_log, name='confirm_message_log'),
    path('memory-map/', views.memory_map, name='memory_map'),

]
