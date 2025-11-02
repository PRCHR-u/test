from django.urls import path
from .views import (
    HealthCheckView, 
    SimpleHealthCheckView, 
    ReadinessCheckView, 
    LivenessCheckView
)

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('health/simple/', SimpleHealthCheckView.as_view(), name='health-simple'),
    path('health/readiness/', ReadinessCheckView.as_view(), name='readiness-check'),
    path('health/liveness/', LivenessCheckView.as_view(), name='liveness-check'),
]
