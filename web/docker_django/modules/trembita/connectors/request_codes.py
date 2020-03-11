"""
Файл із усіма конекторами розбитими як функції у вигляді шаблону
+ змінні, які задаються при виклику у головному файлі
"""
import requests
from django.shortcuts import HttpResponse
from xml.dom.minidom import parseString

#Отримуємо код країни
def country_code(params, urls, headers):
    #зміна params - задається у головному файлі
    #urls та headers використовуються із файлу сетінгів, але теж можуть бути зміненими при виклику
    code = """<?xml version="1.0" encoding="UTF-8"?>
                 <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xro="http://x-road.eu/xsd/xroad.xsd" xmlns:iden="http://x-road.eu/xsd/identifiers" xmlns:v1="http://uis/dev/service/GetCountryName/v1">
       <soapenv:Header>
          <xro:client iden:objectType="SUBSYSTEM">
             <iden:xRoadInstance>SEVDEIR-TEST</iden:xRoadInstance>
             <iden:memberClass>GOV</iden:memberClass>
             <iden:memberCode>37471818</iden:memberCode>
             <!--Optional:-->
             <iden:subsystemCode>MGMT</iden:subsystemCode>
          </xro:client>
          <xro:service iden:objectType="SERVICE">
             <iden:xRoadInstance>SEVDEIR-TEST</iden:xRoadInstance>
             <iden:memberClass>GOV</iden:memberClass>
             <iden:memberCode>37471818</iden:memberCode>
             <!--Optional:-->
             <iden:subsystemCode>MGMT</iden:subsystemCode>
             <iden:serviceCode>GetCountryName</iden:serviceCode>
             <!--Optional:-->
             <iden:serviceVersion>v1</iden:serviceVersion>
          </xro:service>
          <xro:userId>?</xro:userId>
          <xro:id>?</xro:id>
          <xro:protocolVersion>4.0</xro:protocolVersion>
       </soapenv:Header>
       <soapenv:Body>
          <v1:GetCountryName>
             <countrycode>"""+params+"""</countrycode>
          </v1:GetCountryName>
       </soapenv:Body>
    </soapenv:Envelope>"""
    response = requests.post(urls, data=code, headers=headers)
    xmldoc = parseString(response.content)
    # labels = xmldoc.getElementsByTagName("code")[0]
    description = xmldoc.getElementsByTagName("description")[0]
    # new = labels.firstChild.data
    desc = description.firstChild.data
    return HttpResponse(desc)
