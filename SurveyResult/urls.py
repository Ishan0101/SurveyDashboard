from django.urls import path

from .views import Home,Response

app_name ='SurveyResult'

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('ResponseList/',Response.as_view(),name='responselist')
]