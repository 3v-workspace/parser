from django.conf.urls import url

from authorization.views import (
    logout_function,
    get_token_by_code,
)
from authorization.connectors.privatbank.privatbankid import (
    bank_id_log_in,
    bank_id_auth,
)
from authorization.connectors.id_gov_ua.id_gov_ua import (
    gov_ua_log_in,
    gov_ua_auth,
)

urlpatterns = [
    url(r'^log_in$', gov_ua_log_in, name='gov_ua_log_in'),
    url(r'^logout$', logout_function, name='logout'),
    url(r'^auth$', gov_ua_auth, name='gov_ua_auth'),

    url(r'^bank_id_log_in$', bank_id_log_in, name='bank_id_log_in'),
    url(r'^bank_id_auth$', bank_id_auth, name='bank_id_auth'),

    url(r'^token', get_token_by_code, name='get_token_by_code'),
]