from urllib import parse
from http.client import HTTPConnection
import base64


HttpRequestParameterAddress = "address"
HttpContentTypeBase64 = "X-user/base64-data"

UseProxy = False
ProxyAddress = ""
ProxyPort = 3128
IsProxyAnonymous = True
ProxyLoginPassword = "username:password"

HttpProxyHandlerPath = '/sign/server/proxyhandler'

knownHosts = [
	"czo.gov.ua",
	"acskidd.gov.ua",
	"ca.informjust.ua",
	"csk.uz.gov.ua",
	"masterkey.ua",
	"ocsp.masterkey.ua",
	"tsp.masterkey.ua",
	"ca.ksystems.com.ua",
	"csk.uss.gov.ua",
	"csk.ukrsibbank.com",
	"acsk.privatbank.ua",
	"ca.mil.gov.ua",
	"acsk.dpsu.gov.ua",
	"acsk.er.gov.ua",
	"ca.mvs.gov.ua",
	"canbu.bank.gov.ua",
	"uakey.com.ua",
	"ca.csd.ua",
	"altersign.com.ua",
	"ca.altersign.com.ua",
	"ocsp.altersign.com.ua",
	"acsk.uipv.org",
	"ocsp.acsk.uipv.org",
	"acsk.treasury.gov.ua",
    "ca.iit.com.ua"
]

def isKnownHost(uriValue):
    try:
        if uriValue.find("://") == -1:
            uriValue = "http://" + uriValue
        host = parse.urlparse(uriValue).hostname
        if host == None or host == "":
            host = uriValue
        if host in knownHosts:
            return True
    except:
        return False
    return False


def getContentType(uriValue):
    try:
        if uriValue.find("://") == -1:
            uriValue = "http://" + uriValue

        path = parse.urlparse(uriValue).path
        # print("path", path)
        if path == None or path == "":
            return ""

        if path[len(path) - 1] == '/':
            path = path[:-1]

        if path == "/services/cmp":
            return ""
        elif path == "/services/ocsp" or path == "/public/ocsp":
            return "application/ocsp-request"
        elif path == "/services/tsp":
            return "application/timestamp-query"
        else:
            return ""
    except:
        return ""


def handle_request(request):
    global HttpRequestParameterAddress
    global HttpContentTypeBase64
    global UseProxy
    global ProxyAddress
    global ProxyPort
    global IsProxyAnonymous
    global ProxyLoginPassword

    returnResponse = {'status': 200, 'data': ''}

    httpMethod = request.method
    httpHeaders = request.META
    httpURLParams = request.GET

    httpRequestData = request.body

    address = httpURLParams.get(HttpRequestParameterAddress, '')
    # print("address", address)
    if address == "":
        # print('here2')
        returnResponse['status'] = 400
        return returnResponse
    if isKnownHost(address) == False:
        # print('here3')
        returnResponse['status'] = 403
        return returnResponse

    url = address
    if url.find("://") == -1:
        url = "http://" + url
    headers = {"Accept": "*/*",
               "Pragma": "no-cache"}

    if UseProxy != False:
        httpReq = HTTPConnection(str(ProxyAddress), ProxyPort)
        if IsProxyAnonymous != False:
            headers['Proxy-Authorization'] = 'Basic ' + base64.b64encode(ProxyLoginPassword)
    else:
        httpReq = HTTPConnection(str(parse.urlparse(url).hostname), parse.urlparse(url).port)
        url = parse.urlparse(url).path

    if httpMethod == 'POST':
        if httpHeaders['CONTENT_TYPE'] != HttpContentTypeBase64:
            httpReq.close()
            # print('here4', httpHeaders['CONTENT_TYPE'], HttpContentTypeBase64)
            returnResponse['status'] = 400
            return returnResponse

        headers['Content-Type'] = getContentType(address)
        requestData = base64.b64decode(httpRequestData)
        headers['Content-Length'] = len(requestData)
        httpReq.request("POST", str(url), requestData, headers)
    else:
        httpReq.request("GET", str(url), None, headers)

    response = httpReq.getresponse()
    returnResponse['status'] = response.status
    if response.status != 200:
        httpReq.close()
        # print('here5', returnResponse)
        return returnResponse

    returnResponse['data'] = base64.b64encode(response.read())

    httpReq.close()

    return returnResponse
