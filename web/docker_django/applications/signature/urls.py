from django.conf.urls import url

from .views import server_proxy_handler, get_file_hash, send_signed_file_hash, \
    ftp_interaction,\
    xml_access, hash_access


urlpatterns = [
    url(r'^server/proxyhandler$', server_proxy_handler, name='proxy_handler'),
    url(r'^get_file_hash$', get_file_hash, name='get_file_hash'),
    url(r'^send_signed_file_hash$', send_signed_file_hash, name='send_signed_file_hash'),
    url(r'^ftp_interaction$', ftp_interaction, name='ftp_interaction'),
    url(r'^(?P<id_xml>\d+)/xml_access$', xml_access, name='xml_access'),
    url(r'^(?P<id_hash>\d+)/hash_access$', hash_access, name='hash_access'),
]
