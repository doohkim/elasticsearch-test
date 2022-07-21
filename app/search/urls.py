from django.urls import path

from search.views import SearchBizUserAPIView, SearchProductionAPIView, SearchBizBrandAPIView

urlpatterns = [
    path('bizu/<str:query>/', SearchBizUserAPIView.as_view()),
    path('product/<str:query>/', SearchProductionAPIView.as_view()),
    path('brand/<str:query>/',SearchBizBrandAPIView.as_view() )
]