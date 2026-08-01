from django.urls import include, path

urlpatterns = [path("api/", include("advanced_hello_world_core.urls"))]
