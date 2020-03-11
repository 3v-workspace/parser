import base64
import random
from datetime import datetime
import string

import Crypto
from Crypto import Random
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Signature import PKCS1_v1_5 as PKCS1Signature
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from django.contrib.auth import get_user_model, authenticate
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings

from authorization.models import UserTemporaryCode, Token
from users.models import Organization
from users.models import Log_User


def generate_random_code(size=12, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))


def _get_RSA_key():
    return RSA.importKey(settings.PRIVATE_KEY)


def _decrypt_message(c, private_key):
    """Розшифрування за допомогою бібліотеки Crypto.

    Args:
        c: зашифровані дані.
        private_key: приватний ключ RSA.

    Returns:
        Розшифрована строка.
    """
    dsize = SHA.digest_size
    sentinel = Random.new().read(256+dsize)
    m = private_key.decrypt(c, sentinel)
    return m


def verify_message(message, RSA_key, signature):
    """Перевірка розшифрованої строки SHA1
    Args:
        message: розшифрована строка
        RSA_key: приватний ключ RSA;

    Returns:
        Булеве значення True або False
    """
    verifier = PKCS1Signature.new(RSA_key)
    h = SHA.new(message)
    return verifier.verify(h, signature)


def decrypt(c, private_key=None, signature=None):
    """ Використання методу розшифрування та перевірка розшифрованої строки.

    Args:
        c: зашифровані дані;
        private_key: приватний ключ RSA;
        signature: підпис SHA1 з BankID.

    Returns:
        Розшифрована строка або None
    """
    if not private_key:
        private_key = PKCS1_v1_5.new(_get_RSA_key())
    m = _decrypt_message(c, private_key)
    res = m
    if signature:
        if not verify_message(m, private_key, signature):
            res = None
    return res


class AuthService(object):
    """Автентифікація користувача в системі.

    Автентифікація на основі отриманих даних
    """

    def _decrypt_user_data(self, data):
        """Розшифрування даних.

        Args:
            data: дані отримані з BankID (ключ 'customer' з отриманого JSON об'єкта)

        Returns:
            Словник з розшифрованими даними.
            Ключі : "firstName", "middleName", "lastName", "phone", "inn", "clId", "clIdText", "birthDay", "email",
            "sex", "resident", "dateModification"
        """
        signature = data.get('signature', None)
        private_key = PKCS1_v1_5.new(_get_RSA_key())
        for k, v in data.items():
            c = base64.urlsafe_b64decode(v)
            data[k] = decrypt(c, private_key, signature).decode('utf-8', 'ignore')

        return data

    def _get_user_dict(self, user_data, source):
        """Формування "зручного" словника на основі розшифрованих даних.

        Args:
            user_data: розшифровані дані про користувача

        Returns:
            Словник з даними про користувача
        """
        if source == 'privatbank':
            if user_data.get('edrpou', None):
                len_edrpou = len(user_data.get('edrpou', None))
            else:
                len_edrpou = 0
            if (user_data.get('inn', None) and not user_data.get('edrpou', None)):
                dict = {
                    'email': user_data.get('email', '').lower(),
                    'last_name': user_data.get('lastName', '').capitalize(),
                    'first_name': user_data.get('firstName', '').capitalize(),
                    'middle_name': user_data.get('middleName', '').capitalize(),
                    'phone': user_data.get('phone', None),
                    'identification_code': user_data.get('inn', None),
                    'region': user_data.get('state', None),
                    'type': 'physical',
                    'auth_type': 'privatbank',
                    'verification_type': 'privatbank',
                }
            elif user_data.get('inn', None) and user_data.get('edrpou', None) and len_edrpou == 10:
                dict = {
                    'email': user_data.get('email', '').lower(),
                    'last_name': user_data.get('lastName', '').capitalize(),
                    'first_name': user_data.get('firstName', '').capitalize(),
                    'middle_name': user_data.get('middleName', '').capitalize(),
                    'phone': user_data.get('phone', None),
                    'identification_code': user_data.get('inn', None),
                    'region': user_data.get('state', None),
                    'type': 'physical',
                    'auth_type': 'privatbank',
                    'verification_type': 'privatbank',
                }
            elif not user_data.get('inn', None) and user_data.get('edrpou', None) and len_edrpou == 10:
                dict = {
                    'email': user_data.get('email', '').lower(),
                    'last_name': user_data.get('lastName', '').capitalize(),
                    'first_name': user_data.get('firstName', '').capitalize(),
                    'middle_name': user_data.get('middleName', '').capitalize(),
                    'phone': user_data.get('phone', None),
                    'identification_code': user_data.get('edrpou', None),
                    'region': user_data.get('state', None),
                    'type': 'physical',
                    'auth_type': 'privatbank',
                    'verification_type': 'privatbank',
                }

            elif user_data.get('edrpou', None) and len_edrpou != 10:
                dict = {
                    'email': user_data.get('email', '').lower(),
                    'last_name': user_data.get('lastName', '').capitalize(),
                    'first_name': user_data.get('firstName', '').capitalize(),
                    'middle_name': user_data.get('middleName', '').capitalize(),
                    'phone': user_data.get('phone', None),
                    'edrpoucode': user_data.get('edrpou', None),
                    'region': user_data.get('state', None),
                    'type': 'legal',
                    'auth_type': 'privatbank',
                    'verification_type': 'privatbank',
                }
            else:
                dict = {
                    'email': user_data.get('email', '').lower(),
                    'last_name': user_data.get('lastName', '').capitalize(),
                    'first_name': user_data.get('firstName', '').capitalize(),
                    'middle_name': user_data.get('middleName', '').capitalize(),
                    'phone': user_data.get('phone', None),
                    'identification_code': user_data.get('inn', None),
                    'edrpoucode': user_data.get('edrpou', None),
                    'region': user_data.get('state', None),
                    'auth_type': 'privatbank',
                    'verification_type': 'privatbank',
                }
        else:
            if user_data.get('edrpoucode', None):
                len_edrpou = len(user_data.get('edrpoucode', None))
            else:
                len_edrpou = 0

            if (user_data.get('o', None) == 'ФІЗИЧНА ОСОБА' or user_data.get('drfocode', None)) \
                    and not user_data.get('edrpoucode', None):
                dict = {
                    'email': user_data.get('email', ''),
                    'last_name': user_data.get('lastname', '').capitalize(),
                    'first_name': user_data.get('givenname', '').capitalize(),
                    'middle_name': user_data.get('middlename', '').capitalize(),
                    'phone': user_data.get('phone', None),
                    'passport': user_data.get('drfocode', None),
                    'identification_code': user_data.get('drfocode', None),
                    'serial': user_data.get('serial', None),
                    'issuer': user_data.get('issuer', None),
                    'region': user_data.get('state', None),
                    'auth_type': user_data.get('auth_type', None),
                    'verification_type': 'id_gov',
                    'type': 'physical'
                }
            elif user_data.get('drfocode', None) and user_data.get('edrpoucode', None) and len_edrpou == 10:
                dict = {
                    'email': user_data.get('email', ''),
                    'last_name': user_data.get('lastname', '').capitalize(),
                    'first_name': user_data.get('givenname', '').capitalize(),
                    'middle_name': user_data.get('middlename', '').capitalize(),
                    'phone': user_data.get('phone', None),
                    'passport': user_data.get('drfocode', None),
                    'identification_code': user_data.get('drfocode', None),
                    'serial': user_data.get('serial', None),
                    'issuer': user_data.get('issuer', None),
                    'region': user_data.get('state', None),
                    'auth_type': user_data.get('auth_type', None),
                    'verification_type': 'id_gov',
                    'type': 'physical'
                }
            elif not user_data.get('drfocode', None) and user_data.get('edrpoucode', None) and len_edrpou == 10:
                dict = {
                    'email': user_data.get('email', ''),
                    'last_name': user_data.get('lastname', '').capitalize(),
                    'first_name': user_data.get('givenname', '').capitalize(),
                    'middle_name': user_data.get('middlename', '').capitalize(),
                    'phone': user_data.get('phone', None),
                    'passport': user_data.get('drfocode', None),
                    'identification_code': user_data.get('edrpoucode', None),
                    'serial': user_data.get('serial', None),
                    'issuer': user_data.get('issuer', None),
                    'region': user_data.get('state', None),
                    'auth_type': user_data.get('auth_type', None),
                    'verification_type': 'id_gov',
                    'type': 'physical'
                }
            elif user_data.get('edrpoucode', None) and len_edrpou != 10:
                dict = {
                    'email': user_data.get('email', ''),
                    'last_name': user_data.get('lastname', '').capitalize(),
                    'first_name': user_data.get('givenname', '').capitalize(),
                    'middle_name': user_data.get('middlename', '').capitalize(),
                    'phone': user_data.get('phone', None),
                    'passport': user_data.get('drfocode', None),
                    'organization': user_data.get('o', None),
                    'edrpoucode': user_data.get('edrpoucode', None),
                    'serial': user_data.get('serial', None),
                    'issuer': user_data.get('issuer', None),
                    'region': user_data.get('state', None),
                    'verification_type': 'id_gov',
                    'auth_type': user_data.get('auth_type', None),
                    'type': 'legal'
                }
            else:
                dict = {
                    'email': user_data.get('email', ''),
                    'last_name': user_data.get('lastname', '').capitalize(),
                    'first_name': user_data.get('givenname', '').capitalize(),
                    'middle_name': user_data.get('middlename', '').capitalize(),
                    'phone': user_data.get('phone', None),
                    'passport': user_data.get('drfocode', None),
                    'identification_code': user_data.get('drfocode', None),
                    'organization': user_data.get('o', None),
                    'edrpoucode': user_data.get('edrpoucode', None),
                    'serial': user_data.get('serial', None),
                    'issuer': user_data.get('issuer', None),
                    'region': user_data.get('state', None),
                    'verification_type': 'id_gov',
                    'auth_type': user_data.get('auth_type', None),
                }
        return dict

    def authenticate(self, **kwargs):
        """Реєстрація користувача

        Створення або оновлення записів в базі для моделей BankIdToken та User.
        Створення тимчасового запису в базі UserTemporaryCode на час реєстрації користувача

        Args:
            **kwargs: словник всіх іменованих аргументів

        Returns:
            code - code з об'єкту UserTemporaryCode.
        """

        source = kwargs.pop('source')
        log_user = Log_User.objects.create(source=source)
        if source == 'privatbank':
            signature = kwargs.pop('signature')
            encrypted_data = kwargs.pop('encrypted_data')
            user_data = self._get_user_dict(self._decrypt_user_data(encrypted_data), 'privatbank')
        else:
            encrypted_data = kwargs.pop('encrypted_data')
            user_data = self._get_user_dict(encrypted_data, 'id_gov')

        log_user.json_login = user_data
        if user_data.get('auth_type', None):
            log_user.type = user_data.get('auth_type', None)
        log_user.save()

        if user_data.get('first_name', None):
            user_data['first_name'] = user_data.get('first_name', None).split(' ')[0]

        if user_data.get('edrpoucode', None):
            try:
                organization = Organization.objects.get(name=user_data.get('organization', None),
                                                        edrpou=user_data['edrpoucode'])
            except Organization.DoesNotExist:
                organization = Organization(name=user_data['organization'], edrpou=user_data['edrpoucode'])
                organization.save()
        else:
            organization = None

        user_drfocode = user_data.get('identification_code')
        user_edrpoucode = user_data.get('edrpoucode')

        if encrypted_data.get('organization', None) == 'М. КИЇВ':
            user_data['region'] = 'М. КИЇВ'

        if user_drfocode:
            user_drfocode_set = set(user_drfocode)
            if len(user_drfocode_set) <= 1 or user_drfocode[:3] == '555':
                user_drfocode = ''

        if user_data.get('serial', None):
            user_data.pop('serial')
        if user_data.get('issuer', None):
            user_data.pop('issuer')

        if user_data.get('organization', None):
            user_data.pop('organization')
            user_data.pop('edrpoucode')

        if 'edrpoucode' in user_data.keys():
            user_data.pop('edrpoucode')
        if 'organization' in user_data.keys():
            user_data.pop('organization')

        if user_data.get('email', None) == '':
            user_data.pop('email')

        if user_data.get('phone', None) == '':
            user_data.pop('phone')

        from random import randint
        range_start = 10 ** (10 - 1)
        range_end = (10 ** 10) - 1
        now = datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")
        user_data['unique_code'] = str(randint(range_start, range_end)) + str(now)

        if user_drfocode or user_edrpoucode:
            user = None
            if user_drfocode and not user_edrpoucode:
                try:
                    user = get_user_model().objects.get(identification_code=user_drfocode,
                                                        organization__isnull=True,
                                                        auth_type=user_data.get('auth_type', None))
                except:
                    user = get_user_model().objects.update_or_create(identification_code=user_drfocode, organization__isnull=True,
                                                                     defaults=user_data)[0]
                    if organization:
                        user.organization = organization
                        user.save()
                    if not user.subscribecode:
                        now = datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")
                        user.subscribecode = str(now) + str(user.id)
                        user.save()
            elif user_edrpoucode and not user_drfocode:
                try:
                    user = get_user_model().objects.get(identification_code='',
                                                        organization__edrpou=user_edrpoucode,
                                                        auth_type=user_data.get('auth_type', None))
                except:
                    user = get_user_model().objects.update_or_create(identification_code='',
                                                                     organization__edrpou=user_edrpoucode,
                                                                     defaults=user_data)[0]
                    if organization:
                        user.organization = organization
                        user.save()
                    if not user.subscribecode:
                        now = datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")
                        user.subscribecode = str(now) + str(user.id)
                        user.save()

            elif user_edrpoucode and user_drfocode:
                try:
                    user = get_user_model().objects.get(identification_code=user_drfocode,
                                                        organization__edrpou=user_edrpoucode,
                                                        auth_type=user_data.get('auth_type', None))
                except:
                    user = get_user_model().objects.update_or_create(identification_code=user_drfocode,
                                                                     organization__edrpou=user_edrpoucode,
                                                                     defaults=user_data)[0]
                    if organization:
                        user.organization = organization
                        user.save()
                    if not user.subscribecode:
                        now = datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")
                        user.subscribecode = str(now) + str(user.id)
                        user.save()

        else:
            user = None
            return redirect('/')


        return {'user': user}


    def authenticate_by_cl_id(self, cl_id):
        # user_model = get_user_model()
        user = None
        if Token.objects.filter(cl_id=cl_id).exists():
            user = Token.objects.filter(cl_id=cl_id).first().user
        return user
