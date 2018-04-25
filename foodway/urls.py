from django.conf.urls import url, include

urlpatterns = [
    url(r'^', include('apps.food_app.urls')),
]
