from django.urls import path
from llm.views import CallLLMView

urlpatterns = [
    path('llm/call-llms/', CallLLMView.as_view(), name='call-llms'),
]
