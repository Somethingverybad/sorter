from django.contrib import admin
from django.urls import path
from core.views import StoneSortingView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', StoneSortingView.as_view(), name='sorting'),
]