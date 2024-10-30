from django.urls import path
from .views import MessageView

urlpatterns = [
    path('get_answer/', MessageView.as_view(), name='get_answer'),
]
