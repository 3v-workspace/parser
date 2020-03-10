from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64

from django.conf import settings


def generate_keys():
    modulus_length = 2048

    key = RSA.generate(modulus_length)
    # print (key.exportKey())

    pub_key = key.publickey()
    # print (pub_key.exportKey())

    return key, pub_key


def encrypt_private_key(a_message, private_key):
    encryptor = PKCS1_OAEP.new(RSA.importKey(private_key))
    # encryptor = PKCS1_OAEP.new(RSA.importKey(private_key))
    encrypted_msg = encryptor.encrypt(a_message)
    encoded_encrypted_msg = base64.b64encode(encrypted_msg)
    return encoded_encrypted_msg
    # return encrypted_msg


def decrypt_public_key(encoded_encrypted_msg, public_key):
    encryptor = PKCS1_OAEP.new(RSA.importKey(public_key))
    decoded_encrypted_msg = base64.b64decode(encoded_encrypted_msg)
    decoded_decrypted_msg = encryptor.decrypt(decoded_encrypted_msg)
    return decoded_decrypted_msg


def main():
    private, public = generate_keys()
    message = b'Hello world'
    encoded = encrypt_private_key(message, public)
    decrypt_public_key(encoded, private)


def send_to_another_sign(request, dict_sign):
    """
    :param request: contains `id_service_request`, `certificate`
    :return: status, error, ppszHash, ppbHash
    """

    import base64

    my_dict = dict_sign
    encoded_dict = str(my_dict).encode('utf-8')
    base64_dict = base64.b64encode(encoded_dict)

    public = settings.PUBLIC_KEY_SIGN

    message = base64_dict
    from crypto_info.views import encrypt_private_key
    encoded = encrypt_private_key(message, public)

    # from crypto_info.views import decrypt_public_key
    # decrupt_base64_dict = decrypt_public_key(encoded, private)
    #
    # my_dict_again = eval(base64.b64decode(decrupt_base64_dict))
    # print(my_dict_again)

    return encoded


# import base64
#
# my_dict = {'name': 'Rajiv Sharmadfdgfdgdfgdgfgdf', 'id': 2, 'email': 'liliya.bevcukddddfdf'}
# encoded_dict = str(my_dict).encode('utf-8')
# base64_dict = base64.b64encode(encoded_dict)
# from crypto_info.views import generate_keys
#
# # private, public = generate_keys()
# public = PUBLIC_KEY_SIGN
# private = PRIVATE_KEY_SIGN
# # print(private.exportKey())
# # print(public.exportKey())
# message = base64_dict
# from crypto_info.views import encrypt_private_key
#
# encoded = encrypt_private_key(message, public)
#
# print('enc', encoded)
#
# from crypto_info.views import decrypt_public_key
#
# decrupt_base64_dict = decrypt_public_key(encoded, private)
#
# my_dict_again = eval(base64.b64decode(decrupt_base64_dict))
# print(my_dict_again)
