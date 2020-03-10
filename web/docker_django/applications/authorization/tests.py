from django.test import TestCase

from authorization.models import Token
from authorization.services import AuthService
from django.contrib.auth import get_user_model

User = get_user_model()


def create_user():
    """
    """
    try:
        user = User.objects.get(identification_code="6743536436")
    except User.DoesNotExist:
        user = User.objects.create(email="lily.bevcuk@gmail.com", first_name="Користувач", last_name="Тестовий",
                                   middle_name="Петрович", identification_code="6743536436", type="physical")
        Token.objects.create(user=user, cl_id='6743536436',
                             cl_id_text='O=АТ "ІІТ";OU=Тестовий ЦСК;CN=Тестовий ЦСК АТ "ІІТ";Serial=UA-22723472;C=UA;L=Харків;ST=Харківська')
    return user


class QuestionViewTests(TestCase):

    def test_ezp(self):
        """
        """
        service = AuthService()
        user = create_user()
        data_response_ezp = {'issuer': 'O=АТ "ІІТ";OU=Тестовий ЦСК;CN=Тестовий ЦСК АТ "ІІТ";Serial=UA-22723472;C=UA;L=Харків;ST=Харківська', 'issuercn': 'Тестовий ЦСК АТ "ІІТ"', 'serial': '5B63D88375D920180400000013150000783B0000', 'subject': '', 'subjectcn': 'Тестовий фіз користувач кабінету водія', 'locality': 'Бориспіль', 'state': 'Київська', 'o': '', 'ou': '', 'title': '', 'givenname': 'Користувач', 'middlename': 'Петрович', 'lastname': 'Тестовий', 'email': 'lily.bevcuk@gmail.com', 'address': '', 'phone': '+38 (0 50) 121-46-46', 'dns': '', 'edrpoucode': '6743536436', 'drfocode': '6743536436'}
        self.assertEqual(service.authenticate(encrypted_data=data_response_ezp), user)

    def test_mobile(self):
        """
        """
        service = AuthService()
        user = create_user()
        data_response_ezp = {'issuer': 'O=State enterprise "NAIS";OU=Certification Authority;CN=CA of the Justice of Ukraine;Serial=UA-39787008-1217;C=UA;L=Kyiv;OI=NTRUA-39787008', 'issuercn': 'CA of the Justice of Ukraine', 'serial': '5358AA454903301404000000B8D90400D6180B00', 'subject': 'CN=MobileID KS Test250;SN=Test250;GivenName=MobileID KS;Serial=TAXUA-0192837465;C=UA;L=Kiev', 'subjectcn': 'MobileID KS Test250', 'locality': 'Kiev', 'state': '', 'o': '', 'ou': '', 'title': '', 'givenname': 'Користувач', 'middlename': 'Петрович', 'lastname': 'Тестовий', 'email': '', 'address': '', 'phone': '', 'dns': '', 'edrpoucode': '6743536436', 'drfocode': '6743536436'}
        self.assertEqual(service.authenticate(encrypted_data=data_response_ezp), user)

    def test_bank(self):
        """
        """
        service = AuthService()
        user = create_user()
        data_response_ezp = {'issuer': '', 'issuercn': '', 'serial': '', 'subject': '', 'subjectcn': '', 'locality': '', 'state': '', 'o': '', 'ou': '', 'title': '', 'givenname': 'Користувач', 'middlename': 'Петрович', 'lastname': 'Тестовий', 'email': '', 'address': 'UA  ВУЛ. ЧЕРНЯХОВСЬКОГО, БУД. 25Б, КВ. 67 1 1 ', 'phone': '380676643089', 'dns': '', 'edrpoucode': '6743536436', 'drfocode': '6743536436'}
        self.assertEqual(service.authenticate(encrypted_data=data_response_ezp), user)

