from django.urls import path

from .views import AllResults, Home,Response,SelectedSurvey

app_name ='SurveyResult'

urlpatterns = [
    path('', Home.as_view(), name='home'),
    path('SelectedSurvey/',SelectedSurvey.as_view(),name='selected_survey'),
    path('ResponseList/',Response.as_view(),name='responselist'),
    path('allResults/',AllResults.as_view(),name='all_results')
]