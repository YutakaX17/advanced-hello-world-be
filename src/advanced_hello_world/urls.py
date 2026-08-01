from django.urls import include, path

from advanced_hello_world.settings.base import MODULE_MANIFEST

urlpatterns = [
    path(selection.url_prefix, include(selection.urls)) for selection in MODULE_MANIFEST.selections
]
