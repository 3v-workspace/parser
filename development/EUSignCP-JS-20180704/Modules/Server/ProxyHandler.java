package com.iit.eusign;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URI;

import javax.servlet.ServletException;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/*
    To support Oracle WebLogic server use -DUseSunHttpHandler=true
*/

class Base64 {
    private static final byte[] encodingTable = {
        (byte)'A', (byte)'B', (byte)'C', (byte)'D', (byte)'E', (byte)'F', (byte)'G', (byte)'H',
        (byte)'I', (byte)'J', (byte)'K', (byte)'L', (byte)'M', (byte)'N', (byte)'O', (byte)'P',
        (byte)'Q', (byte)'R', (byte)'S', (byte)'T', (byte)'U', (byte)'V', (byte)'W', (byte)'X',
        (byte)'Y', (byte)'Z', (byte)'a', (byte)'b', (byte)'c', (byte)'d', (byte)'e', (byte)'f',
        (byte)'g', (byte)'h', (byte)'i', (byte)'j', (byte)'k', (byte)'l', (byte)'m', (byte)'n',
        (byte)'o', (byte)'p', (byte)'q', (byte)'r', (byte)'s', (byte)'t', (byte)'u', (byte)'v',
        (byte)'w', (byte)'x', (byte)'y', (byte)'z', (byte)'0', (byte)'1', (byte)'2', (byte)'3',
        (byte)'4', (byte)'5', (byte)'6', (byte)'7', (byte)'8', (byte)'9', (byte)'+', (byte)'/'
    };

    private static final byte[] decodingTable;

    static {
        decodingTable = new byte[128];

        for (int i = 'A'; i <= 'Z'; i++) {
            decodingTable[i] = (byte)(i - 'A');
        }

        for (int i = 'a'; i <= 'z'; i++) {
            decodingTable[i] = (byte)(i - 'a' + 26);
        }

        for (int i = '0'; i <= '9'; i++) {
            decodingTable[i] = (byte)(i - '0' + 52);
        }

        decodingTable['+'] = 62;
        decodingTable['/'] = 63;
    }

    public static byte[] encode(byte[] data) {
        byte[]    bytes;

        int modulus = data.length % 3;
        if (modulus == 0) {
            bytes = new byte[4 * data.length / 3];
        }
        else {
            bytes = new byte[4 * ((data.length / 3) + 1)];
        }

        int dataLength = (data.length - modulus);
        int a1, a2, a3;
        for (int i = 0, j = 0; i < dataLength; i += 3, j += 4) {
            a1 = data[i] & 0xff;
            a2 = data[i + 1] & 0xff;
            a3 = data[i + 2] & 0xff;

            bytes[j] = encodingTable[(a1 >>> 2) & 0x3f];
            bytes[j + 1] = encodingTable[((a1 << 4) | (a2 >>> 4)) & 0x3f];
            bytes[j + 2] = encodingTable[((a2 << 2) | (a3 >>> 6)) & 0x3f];
            bytes[j + 3] = encodingTable[a3 & 0x3f];
        }

        int    b1, b2, b3;
        int    d1, d2;

        switch (modulus) {
            case 0:
                break;
            case 1:
                d1 = data[data.length - 1] & 0xff;
                b1 = (d1 >>> 2) & 0x3f;
                b2 = (d1 << 4) & 0x3f;

                bytes[bytes.length - 4] = encodingTable[b1];
                bytes[bytes.length - 3] = encodingTable[b2];
                bytes[bytes.length - 2] = (byte)'=';
                bytes[bytes.length - 1] = (byte)'=';
                break;
            case 2:
                d1 = data[data.length - 2] & 0xff;
                d2 = data[data.length - 1] & 0xff;

                b1 = (d1 >>> 2) & 0x3f;
                b2 = ((d1 << 4) | (d2 >>> 4)) & 0x3f;
                b3 = (d2 << 2) & 0x3f;

                bytes[bytes.length - 4] = encodingTable[b1];
                bytes[bytes.length - 3] = encodingTable[b2];
                bytes[bytes.length - 2] = encodingTable[b3];
                bytes[bytes.length - 1] = (byte)'=';
                break;
        }

        return bytes;
    }

    public static byte[] decode(byte[] data) {
        byte[]    bytes;
        byte    b1, b2, b3, b4;

        if (data[data.length - 2] == '=') {
            bytes = new byte[(((data.length / 4) - 1) * 3) + 1];
        }
        else if (data[data.length - 1] == '=') {
            bytes = new byte[(((data.length / 4) - 1) * 3) + 2];
        }
        else {
            bytes = new byte[((data.length / 4) * 3)];
        }

        for (int i = 0, j = 0; i < data.length - 4; i += 4, j += 3) {
            b1 = decodingTable[data[i]];
            b2 = decodingTable[data[i + 1]];
            b3 = decodingTable[data[i + 2]];
            b4 = decodingTable[data[i + 3]];

            bytes[j] = (byte)((b1 << 2) | (b2 >> 4));
            bytes[j + 1] = (byte)((b2 << 4) | (b3 >> 2));
            bytes[j + 2] = (byte)((b3 << 6) | b4);
        }

        if (data[data.length - 2] == '=') {
            b1 = decodingTable[data[data.length - 4]];
            b2 = decodingTable[data[data.length - 3]];

            bytes[bytes.length - 1] = (byte)((b1 << 2) | (b2 >> 4));
        }
        else if (data[data.length - 1] == '=') {
            b1 = decodingTable[data[data.length - 4]];
            b2 = decodingTable[data[data.length - 3]];
            b3 = decodingTable[data[data.length - 2]];

            bytes[bytes.length - 2] = (byte)((b1 << 2) | (b2 >> 4));
            bytes[bytes.length - 1] = (byte)((b2 << 4) | (b3 >> 2));
        }
        else {
            b1 = decodingTable[data[data.length - 4]];
            b2 = decodingTable[data[data.length - 3]];
            b3 = decodingTable[data[data.length - 2]];
            b4 = decodingTable[data[data.length - 1]];

            bytes[bytes.length - 3] = (byte)((b1 << 2) | (b2 >> 4));
            bytes[bytes.length - 2] = (byte)((b2 << 4) | (b3 >> 2));
            bytes[bytes.length - 1] = (byte)((b3 << 6) | b4);
        }

        return bytes;
    }

    public static byte[] decode(String data) {
        byte[]    bytes;
        byte    b1, b2, b3, b4;

        if (data.charAt(data.length() - 2) == '=') {
            bytes = new byte[(((data.length() / 4) - 1) * 3) + 1];
        }
        else if (data.charAt(data.length() - 1) == '=') {
            bytes = new byte[(((data.length() / 4) - 1) * 3) + 2];
        }
        else {
            bytes = new byte[((data.length() / 4) * 3)];
        }

        for (int i = 0, j = 0; i < data.length() - 4; i += 4, j += 3) {
            b1 = decodingTable[data.charAt(i)];
            b2 = decodingTable[data.charAt(i + 1)];
            b3 = decodingTable[data.charAt(i + 2)];
            b4 = decodingTable[data.charAt(i + 3)];

            bytes[j] = (byte)((b1 << 2) | (b2 >> 4));
            bytes[j + 1] = (byte)((b2 << 4) | (b3 >> 2));
            bytes[j + 2] = (byte)((b3 << 6) | b4);
        }

        if (data.charAt(data.length() - 2) == '=') {
            b1 = decodingTable[data.charAt(data.length() - 4)];
            b2 = decodingTable[data.charAt(data.length() - 3)];

            bytes[bytes.length - 1] = (byte)((b1 << 2) | (b2 >> 4));
        }
        else if (data.charAt(data.length() - 1) == '=') {
            b1 = decodingTable[data.charAt(data.length() - 4)];
            b2 = decodingTable[data.charAt(data.length() - 3)];
            b3 = decodingTable[data.charAt(data.length() - 2)];

            bytes[bytes.length - 2] = (byte)((b1 << 2) | (b2 >> 4));
            bytes[bytes.length - 1] = (byte)((b2 << 4) | (b3 >> 2));
        }
        else {
            b1 = decodingTable[data.charAt(data.length() - 4)];
            b2 = decodingTable[data.charAt(data.length() - 3)];
            b3 = decodingTable[data.charAt(data.length() - 2)];
            b4 = decodingTable[data.charAt(data.length() - 1)];

            bytes[bytes.length - 3] = (byte)((b1 << 2) | (b2 >> 4));
            bytes[bytes.length - 2] = (byte)((b2 << 4) | (b3 >> 2));
            bytes[bytes.length - 1] = (byte)((b3 << 6) | b4);
        }

        return bytes;
    }
}

@WebServlet("/ProxyHandler")
public class ProxyHandler extends HttpServlet {
    private static final long serialVersionUID = 1L;
    private static final String HTTP_REQUEST_PARAMETER_ADDRESS = "address";
    private static final String HTTP_CONTENT_TYPE_BASE64 = "X-user/base64-data";
    private static final int HTTP_MAX_CONTENT_SIZE = 10000000;
    private static final int HTTP_BUFFER_CHUNK = 0xFFFF;
    private static final String[] knownHosts = {
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
        "ca.oschadbank.ua"
    };

    /*Proxy settings*/
    class ProxySettings {
        private static final boolean useProxy = false;
        private static final String address = "";
        private static final String port = "3128";
        private static final boolean isAnonymous = true;
        private static final String user = "";
        private static final String password = "";
    }

    public ProxyHandler() {
        super();
    }

    private boolean isKnownHost(String uriValue)
    {
        try
        {
            if (!uriValue.contains("://"))
                uriValue = "http://" + uriValue;

            URI uri = new URI(uriValue);
            String host = uri.getHost();

            if (host == null || host.equals(""))
                host = uriValue;

            for (int i = 0; i < knownHosts.length; i++)
                if (knownHosts[i].equalsIgnoreCase(host))
                    return true;
        }
        catch (Exception ex)
        {
        }

        return false;
    }
    
    private String getContentType(String uriValue)
    {
        try
        {
            if (!uriValue.contains("://"))
                uriValue = "http://" + uriValue;

            URI uri = new URI(uriValue);
            String path = uri.getPath();

            if (path == null || path.equals(""))
            	return "";

            if (path.charAt(path.length() - 1) == '/')
            	path = path.substring(0, path.length() - 1);
            
			if (path.equals("/services/cmp") || 
					path.equals("/public/x509/cmp"))
			{
				return "";
			}
			else if (path.equals("/services/ocsp") ||
					path.equals("/public/ocsp"))
			{
				return "application/ocsp-request";
			}
			else if (path.equals("/services/tsp") || 
					path.equals("/public/tsa"))
			{
				return "application/timestamp-query";
			}
			else
			{
				return "";
			}
        }
        catch (Exception ex)
        {
        	return "";
        } 	
    }

    private HttpURLConnection createConnection(String method, 
            String paramString) throws Exception {
        URL url = new URL(paramString);
        HttpURLConnection connection;

        if (ProxySettings.useProxy) {
            System.setProperty("http.proxyHost", ProxySettings.address);
            System.setProperty("http.proxyPort", ProxySettings.port);

            connection = (HttpURLConnection) url.openConnection();

            if (!ProxySettings.isAnonymous) {
                String credentials = ProxySettings.user + ":" +
                    ProxySettings.password;
                credentials = new String
                    (Base64.encode(credentials.getBytes()));
                connection.setRequestProperty("Proxy-Authorization",
                    "Basic " + credentials);
            }
        } else {
            connection = (HttpURLConnection) url.openConnection();
        }
        
        connection.setDoInput(true);
        connection.setDoOutput(true);
        
        connection.setRequestMethod(method);
        connection.setRequestProperty("Accept", "*/*");
        connection.setRequestProperty("Pragma", "no-cache");
        connection.setInstanceFollowRedirects(false);
        
        return connection;
    }
    
    private byte[] safeReadDataStream(InputStream stream) throws Exception {
        ByteArrayOutputStream buffer = new ByteArrayOutputStream();

        int nRead;
        byte[] data = new byte[HTTP_BUFFER_CHUNK];

        while ((nRead = stream.read(data, 0, data.length)) != -1) {
            buffer.write(data, 0, nRead);
            
            if (buffer.size() > HTTP_MAX_CONTENT_SIZE)
                return null;
        }

        buffer.flush();

        return buffer.toByteArray();
    }

    private int handleRequest(String method, 
        HttpServletRequest request, HttpServletResponse response) throws Exception {
        
        HttpURLConnection serverConnection;
        String address;
        byte[] clientResponseData;
        
        address = request.getParameter(HTTP_REQUEST_PARAMETER_ADDRESS);
        if (address == null || address == "" || !isKnownHost(address)) {
            return HttpServletResponse.SC_BAD_REQUEST;
        }

        serverConnection = createConnection(method, address);

        if (method == "POST") {
            byte[] requestData;
            String requestDataBase64String;
            byte[] serverRequestData;
            OutputStream outStream;

            if (!request.getContentType().contains(HTTP_CONTENT_TYPE_BASE64))
                return HttpServletResponse.SC_BAD_REQUEST;

            requestData = safeReadDataStream(request.getInputStream());
            if (requestData == null)
                return HttpServletResponse.SC_REQUEST_ENTITY_TOO_LARGE;

            requestDataBase64String = new String(requestData, "UTF-8");
            serverRequestData = Base64.decode(requestDataBase64String);

            serverConnection.setRequestProperty("Content-Type", 
            	getContentType(address));
            serverConnection.setRequestProperty("Content-Length", 
                Integer.toString(serverRequestData.length));
            serverConnection.connect();

            outStream = serverConnection.getOutputStream();
            outStream.write(serverRequestData);
            outStream.flush();
            outStream.close();
        } else {
            serverConnection.connect();
        }

        if (serverConnection.getResponseCode() != HttpServletResponse.SC_OK)
            return serverConnection.getResponseCode();
        
        clientResponseData = safeReadDataStream(
            serverConnection.getInputStream());
        if (clientResponseData == null) {
            serverConnection.disconnect();
            return HttpServletResponse.SC_REQUEST_ENTITY_TOO_LARGE;
        }
        serverConnection.disconnect();

        response.setContentType(HTTP_CONTENT_TYPE_BASE64);
        response.setStatus(HttpServletResponse.SC_OK);
        response.getWriter().write(
            new String(Base64.encode(clientResponseData)));
        
        return HttpServletResponse.SC_OK;
    }
    
    protected void doGet(HttpServletRequest request, HttpServletResponse response)
        throws ServletException, IOException {
        int status = HttpServletResponse.SC_INTERNAL_SERVER_ERROR;
        try {
            status = handleRequest("GET", request, response);
        } catch (Exception ex) {
        } finally {
            if (status != HttpServletResponse.SC_OK) {
                response.getWriter().println("Виникла помилка при обробці запиту");
                response.setStatus(status);
            }
        }
    }

    protected void doPost(HttpServletRequest request, HttpServletResponse response)
        throws ServletException, IOException {
        int status = HttpServletResponse.SC_INTERNAL_SERVER_ERROR;
        try {
            status = handleRequest("POST", request, response);
        } catch (Exception ex) {
        } finally {
            if (status != HttpServletResponse.SC_OK) {
                response.getWriter().println("Виникла помилка при обробці запиту");
                response.setStatus(status);
            }
        }
    }
}