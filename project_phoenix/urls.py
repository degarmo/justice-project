from django.contrib import admin
from django.urls import path, include
from tracker import views  # ✅ This is the missing import

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tracker.urls')),
    path('log-behavior/', views.log_behavior, name='log_behavior'), 
]
