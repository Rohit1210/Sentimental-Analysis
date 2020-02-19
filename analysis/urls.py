#created by me
from django.contrib import admin
from django.urls import path,include
from . import views
from analysis.views import Graph

urlpatterns = [
    path('',views.index,name='index'),
    path('graph/',Graph.as_view()),
    path('chart/',views.chart,name='chart'),
]
