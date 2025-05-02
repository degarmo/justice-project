from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tracker.urls')),  # Include tracker app URLs
    path('log-behavior/', views.log_behavior, name='log_behavior'),
]