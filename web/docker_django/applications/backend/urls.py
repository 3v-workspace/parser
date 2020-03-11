from django.conf.urls import url
from django.urls import include

from applications.backend import views

app_name = 'backend'

urlpatterns = [
    url(r'^$', views.index_backend, name='index_backend'),
    url(r'^not_processed_eservice$', views.not_processed_eservice, name='not_processed_eservice'),
    url(r'^eservices$', views.eservices, name='eservices'),
    url(r'^eservices/rating/', views.eservices_bystar, name='bystar_rating'),
    url(r'^my_eservices', views.my_eservices, name='my_eservices'),
    url(r'^eservice/create/$', views.backend_eservice_create, name='backend_eservice_create'),
    url(r'^eservice/create/+(?P<eservice_type>[0-9a-zA-Z_]+)', views.create_eservice_backend,
        name='create_eservice_backend'),
    url(r'^eservice/delete/+(?P<eservice_id>[0-9_]+)', views.delete_eservice_backend,
        name='delete_eservice_backend'),
    url(r'^eservice/update/+(?P<eservice_id>[0-9_]+)/(?P<step>[0-9]+)', views.update_eservice_backend,
        name='update_eservice'),
    url(r'^', include('support.urls')),

    url(r'^workflow/+(?P<eservice_id>[0-9]+)/approve/', views.approve, name='approve'),
    url(r'^workflow/+(?P<eservice_id>[0-9]+)/reject/', views.reject, name='reject'),
    url(r'^workflow/+(?P<eservice_id>[0-9]+)/to_approve/', views.to_approve, name='approve'),
    url(r'^workflow/+(?P<eservice_id>[0-9]+)/to_edit/', views.to_edit, name='to_edit'),
    url(r'^eservice/+(?P<eservice_id>[0-9]+)', views.eservice_page, name='eservice_page'),

]