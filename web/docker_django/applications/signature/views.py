# -*- coding: utf-8 -*-
from os.path import abspath, exists



from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.core.management import call_command
from django.urls import reverse
from django.apps import apps

from system.cryptography.proxy_handler import handle_request
from system.cryptography.EUSignCP import *

@csrf_exempt
def server_proxy_handler(request):
    """
    The view for POLICE's requests that necessary for working with digital sign
    :param request:
    :return:
    """
    proxyResponse = handle_request(request)
    if proxyResponse['status'] != 200:
        raise Exception("status is not 200")

    returnResponse = HttpResponse(proxyResponse['data'], content_type="text/plain")
    return returnResponse


def get_file_hash(request):
    """
    This view is creating XML (`1.xml`) of earlier created ServiceRequest object.
    Creating Hash (`1.hash`) of the XML.
    :param request: contains `id_service_request`, `certificate`
    :return: status, error, ppszHash, ppbHash
    """
    if request.method == 'POST':
        # getting id of ServiceRequest object which
        id_service_request_obj = int(request.POST.get("id_service_request"))
        e_service_type = request.POST.get("eservice_type")
        apps_doc = request.POST.get("apps")

        model = apps.get_model(apps_doc, e_service_type)
        # start creating Xml file which will send
        xml_file = abspath("media/out/{}.xml".format(id_service_request_obj))
        XMLSerializer = serializers.get_serializer("xml")
        xml_serializer = XMLSerializer()
        with open(xml_file, "w") as out:
            xml_serializer.serialize(model.objects.filter(id=id_service_request_obj), stream=out)
        # end creating Xml file which will send

        # getting certificate
        pbCertificate = request.POST.get("certificate")
        # print("pbCertificate ", pbCertificate)

        if pbCertificate:
            pbCertificate = bytes(bytearray([int(i) for i in pbCertificate.split(',')]))
            dwCertificateLength = len(pbCertificate)
            # cer_file = abspath("../store_cer/{}.cer".format(id_service_request_obj))
            # with open(cer_file, "wb") as out:
            #     out.write(pbCertificate)
        else:
            return JsonResponse({"status": "fail", "error": "certificate in None"})

        # print("pbCertificate ", pbCertificate)
        # launching eusign library
        try:
            EULoad()
            pIface = EUGetInterface()
        except Exception as e:
            print("load or getinterface error")
            EUUnload()
            return JsonResponse({"status": "fail", "error": "load or getinterface error"})
        try:
            pIface.Initialize()
        except Exception as e:
            print("Initialize failed" + str(e))
            EUUnload()
            exit()

        # Creating Hash of xml_file. Hash is a string. It is ppszHash or ppbHash variable.
        ppszHash = []
        ppbHash = []
        pIface.HashFileWithParams(pbCertificate, dwCertificateLength, xml_file, ppszHash, ppbHash)
        pIface.Finalize()

        return JsonResponse({"status": "ok", "error": "",
                             "ppszHash": ppszHash[0].decode() if ppszHash[0] else None,
                             "ppbHash": ppbHash[0].decode() if ppbHash[0] else None})
    return JsonResponse({"status": "fail", "error": "Get request does not allow"})


def send_signed_file_hash(request):
    """
    getting and verifying signed hash and save one in 'media/out'
    :param request: contains `ppbHash`, `ppszHash`, `id_service_request`, `sign_hash` params
    :return: xml_url - url of xml file for downloading, pSignInfo - info from signed_hash
    """

    if request.method == 'POST':
        # launching eusign library
        try:
            EULoad()
            pIface = EUGetInterface()
        except Exception as e:
            print("load or getinterface error")
            EUUnload()
            return JsonResponse({"status": "fail", "error": "load or getinterface error"})
        try:
            pIface.Initialize()
        except Exception as e:
            print("Initialize failed" + str(e))
            EUUnload()
            exit()

        # getting hash - ppbHash or ppszHash
        ppbHash = request.POST.get('ppbHash')
        ppszHash = request.POST.get('ppszHash')
        # print("ppbHash ", ppbHash)
        # print("ppszHash ", ppszHash)
        # getting id of ServiceRequest object
        id_service_request = request.POST.get('id_service_request')
        dwHashLength = 0
        if not ppszHash: # if it is empty string
            ppszHash = None
        if not ppbHash: # if it is empty string
            ppbHash = None
        # getting signed hash
        sign_hash = request.POST.get('sign_hash')

        len_sign_hash = 0
        # this dict will contain data of verified hash(signed)
        pSignInfo = {}
        try:
            pIface.VerifyHash(ppszHash,
                              ppbHash,
                              dwHashLength,
                              sign_hash if ppszHash else None,
                              sign_hash if ppbHash else None,
                              len_sign_hash,
                              pSignInfo)
        # error during verification
        except Exception as e:
            pIface.Finalize()
            return JsonResponse({"status": "fail", "error": str(e),
                                 "pSignInfo": pSignInfo,
                                 "service_requests_link": ''})
            # pass

        # safe sign_hash to media/out/
        path_to_signed_hash = "media/out/{}.hash".format(id_service_request)
        with open(path_to_signed_hash, 'w') as out:
            out.write(sign_hash)

        pIface.Finalize()

        # write message for showing ...
        # messages.add_message(request, messages.SUCCESS, 'Ви успішно підписали послугу!')

        pSignInfo_translate = {}
        translate_dict = {"pszSubjState": "Назва області", "pszSubjDRFOCode": "Код ДРФО",
                          "pszSerial": "Реєстраційний номер сертифіката", "pszIssuer": "Реквізити ЦСК",
                          "pszSubjFullName": "Повне ім’я", "pszSubjLocality": "Назва населеного пункту",
                          "pszSubjEMail": "EMail", "pszSubjPhone": "Телефон"
                          }

        for k, v in pSignInfo.items():
            if k in translate_dict:
                pSignInfo_translate[translate_dict[k]] = v

        return JsonResponse({"status": "ok", "error": "", "pSignInfo": pSignInfo_translate,
                             "xml_url": request.scheme + "://" +
                             request.get_host() + reverse("xml_access",
                                                          kwargs={"id_xml": id_service_request}),
                             "hash_url": request.scheme + "://" +
                             request.get_host() + reverse("hash_access",
                                                          kwargs={"id_hash": id_service_request}),
                             "service_requests_link": "",
                             })

    return JsonResponse({'status': 'fail', 'error': 'do not allow get method'})


def get_key_info(request, document_id):
    """
    getting key information
    :param request: contains `ppbHash`, `ppszHash`, `id_service_request`, `sign_hash` params
    :return: xml_url - url of xml file for downloading, pSignInfo - info from signed_hash
    """


    try:
        EULoad()
        pIface = EUGetInterface()
    except Exception as e:
        print("load or getinterface error")
        EUUnload()
        return JsonResponse({"status": "fail", "error": "load or getinterface error"})
    try:
        pIface.Initialize()
    except Exception as e:
        print("Initialize failed" + str(e))
        EUUnload()
        exit()
    try:
        path_to_signed_hash = "media/out/{}.hash".format(document_id)
        with open(path_to_signed_hash, 'r') as file:
            hash_content = file.read()
    except:
        return None

    dwSignIndex = 0
    pszSign = hash_content
    pbSign = None
    dwSignLength = 0
    ppInfo = {}
    ppbCertificate = {}

    pIface.GetSignerInfo(dwSignIndex,
                         pszSign,
                         pbSign,
                         dwSignLength,
                         ppInfo,
                         ppbCertificate
    )


    pIface.Finalize()

    return ppInfo


def ftp_interaction(request):
    """
    The view for Linux Crontab which will send request here
    View sends .xml and .hash files from `media/out` to FTP server
    and receives .xml files to `media/in`
    :param request:
    :return:
    """
    try:
        call_command("ftp")
        # print("ftp_interaction view")
    except Exception as e:
        return JsonResponse({"status": "ok", "error": str(e)})
    return JsonResponse({"status": "ok", "error": ""})


def xml_access(request, id_xml):
    """
    Ця в'юшка в якості відповіді повертає .xml файл, щоб користувач перевірив дані.
    :param request: об'єкт запиту
    :param id_xml: ІД файлу
    :return: файл для скачування
    """
    path_to_xml = "media/out/{}.xml".format(id_xml)
    if exists(path_to_xml):
        # print(path_to_xml)
        with open(path_to_xml, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/xml')
            response['Content-Disposition'] = 'attachment; filename=' + "{}.xml".format(id_xml)
            response['Content-Type'] = 'application/xml; charset=utf-8'
            return response
    return JsonResponse({"status": "fail", "error": "bad link"})


def hash_access(request, id_hash):
    """
    Ця в'юшка в якості відповіді повертає .геш файл.
    :param request: об'єкт запиту
    :param id_hash: ІД файлу
    :return: геш файл для скачування
    """
    path_to_hash = "media/out/{}.hash".format(id_hash)
    if exists(path_to_hash):
        # print(path_to_hash)
        with open(path_to_hash, 'rb') as f:
            response = HttpResponse(f.read(), content_type='application/xml')
            response['Content-Disposition'] = 'attachment; filename=' + "{}.hash".format(id_hash)
            response['Content-Type'] = 'application/xml; charset=utf-8'
            return response
    return JsonResponse({"status": "fail", "error": "bad link"})


def send_to_another_sign(request, dict_sign):
    """
    :param request: contains `id_service_request`, `certificate`
    :return: status, error, ppszHash, ppbHash
    """
    hash_dict = hash(frozenset(dict_sign.items()))
    print()
    return True
