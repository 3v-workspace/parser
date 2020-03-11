"""
Файл із усіма конекторами розбитими як функції у вигляді шаблону
+ змінні, які задаються при виклику у головному файлі
"""
import requests
from django.shortcuts import HttpResponse


def sev(request):
    code = """<?xml version="1.0" encoding="UTF-8"?>
     <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/" xmlns:cov="http://schemas.datacontract.org/2004/07/Cover.Contracts">
       <soapenv:Header/>
       <soapenv:Body>
          <tem:GetInputMessages>
             <!--Optional:-->
             <tem:identity>
                <!--Optional:-->
                <cov:Password>8c25e921-e46c-4a71-a225-33eb0f4dcb78</cov:Password>
                <!--Optional:-->
                <cov:SystemId>3cc9e21e-d48e-4b44-a4da-18be01e603de</cov:SystemId>
             </tem:identity>
             <!--Optional:-->
             <tem:сount>1</tem:сount>
          </tem:GetInputMessages>
       </soapenv:Body>
    </soapenv:Envelope>""".encode('utf-8')
    response = requests.get('http://213.156.91.113:8082/csp/dirbus/bus.esb.IntegrationService.cls?wsdl', data=code, headers={'content-type': 'text/xml; charset=utf-8'})
    # xmldoc = parseString(response.content)
    # labels = xmldoc.getElementsByTagName("code")[0]
    # description = xmldoc.getElementsByTagName("description")[0]
    # new = labels.firstChild.data
    # desc = description.firstChild.data
    # print(response.text)
    return HttpResponse(response.text)

"""Zeep Version"""
# from zeep import Client
#
# client = Client('http://213.156.91.113:8082/csp/dirbus/bus.esb.IntegrationService.cls?WSDL')
# datas = {'Password': '8c25e921-e46c-4a71-a225-33eb0f4dcb78',
#         'SystemId': '3cc9e21e-d48e-4b44-a4da-18be01e603de'}
# data = {'8c25e921-e46c-4a71-a225-33eb0f4dcb78', '3cc9e21e-d48e-4b44-a4da-18be01e603de'}
# autent = client.get_type('ns0:Identity')
# passid = autent('8c25e921-e46c-4a71-a225-33eb0f4dcb78', '3cc9e21e-d48e-4b44-a4da-18be01e603de')
# result = client.get_type('ns0:GetInputMessages')
# res = result(passid,1)
# print (res)