from django.urls import path

from popup.views import get_popup_modal

app_name = 'popup'

urlpatterns = [
    path('modal/<str:modal_type_name>/', get_popup_modal, name='get_popup_modal'),
]
