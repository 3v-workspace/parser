"""файл виклику фунцій модуля SEV OVV"""
import zeep

wsdl = 'modules/sev_ovv/schemes/DIR.wsdl'
client = zeep.Client(wsdl=wsdl)
print(client.service.GetVersion())