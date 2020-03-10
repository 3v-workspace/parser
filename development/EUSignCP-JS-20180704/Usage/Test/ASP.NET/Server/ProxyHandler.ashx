<%@ WebHandler Language="C#" Class="ProxyHandler" %>

/*
	Для підтримки відповідей від АЦСК "Україна" необхідно додати до web.config
	<system.net>
		<settings>
			<httpWebRequest useUnsafeHeaderParsing="true"/>
		</settings>
	</system.net>

	Для роботи через проксі-сервер необхідно встановити UseProxy = true, та 
	встановити ProxyAddress, ProxyPort, ProxyUser, ProxyPassword.
*/

using System;
using System.Web;
using System.Net;
using System.IO;

public class ProxyHandler : IHttpHandler
{
	private static string HttpRequestParameterAddress = "address";
	private static string HttpContentTypeMultipart = "multipart/form-data";
	private static string HttpContentTypeBase64 = "X-user/base64-data";
	private static int HttpMaxContentSize = 10000000;
	private static int HttpBufferChunk = 0xFFFF;

	private static bool UseProxy = false;
	private static string ProxyAddress = "";
	private static int ProxyPort = 3128;
	private static string ProxyUser = "";
	private static string ProxyPassword = "";

	private static string[] KnownHosts = {
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
		"altersign.com.ua",
		"ca.altersign.com.ua",
		"ocsp.altersign.com.ua",
		"acsk.uipv.org",
		"ocsp.acsk.uipv.org",
		"ca.iit.com.ua"
	};

	private bool IsKnownHost(string uriValue)
	{
		try
		{
			if (!uriValue.Contains("://"))
				uriValue = "http://" + uriValue;

			Uri uri = new Uri(uriValue);
			string host = uri.Host;

			if (host == null || host == "")
				host = uriValue;

			foreach (string knownHost in KnownHosts)
				if (knownHost == host)
					return true;
		}
		catch (Exception ex)
		{
		}

		return false;
	}

	private byte[] SafeReadDataStream(Stream stream)
	{
		byte[] buffer;
		int count;
		MemoryStream memoryStream;
		StreamReader streamReader;

		buffer = new byte[HttpBufferChunk];
		memoryStream = new MemoryStream();
		streamReader = new StreamReader(stream);

		while ((count = streamReader.BaseStream.Read(buffer, 0, buffer.Length)) > 0)
		{
			memoryStream.Write(buffer, 0, count);

			if (memoryStream.Length > HttpMaxContentSize)
				return null;
		}

		return memoryStream.ToArray();
	}

	private HttpStatusCode HandleRequest(HttpContext context)
	{
		HttpWebRequest serverRequest;
		HttpWebResponse serverResponse;
		string requestAddress;
		byte[] clientResponseData;

		requestAddress = 
			context.Request[HttpRequestParameterAddress];

		if (requestAddress == null || requestAddress == "" ||
			!IsKnownHost(requestAddress))
		{
			return HttpStatusCode.BadRequest;
		}

		serverRequest = (HttpWebRequest)WebRequest.Create(requestAddress);
		if (UseProxy)
		{
			serverRequest.Proxy = new WebProxy(ProxyAddress, ProxyPort);
			serverRequest.Proxy.Credentials = new NetworkCredential(
				ProxyUser, ProxyPassword);
		}
		serverRequest.Method = context.Request.RequestType;
		serverRequest.ServicePoint.Expect100Continue = false;

		if (serverRequest.Method == "POST")
		{
			byte[] requestData;
			string requestDataBase64String;
			byte[] serverRequestData;

			if (!context.Request.ContentType.Contains(HttpContentTypeBase64))
				return HttpStatusCode.BadRequest;

			requestData = SafeReadDataStream(context.Request.InputStream);
			if (requestData == null)
				return HttpStatusCode.RequestEntityTooLarge;

			requestDataBase64String = 
				System.Text.Encoding.UTF8.GetString(requestData);
			serverRequestData = Convert.FromBase64String(
				requestDataBase64String);
			
			serverRequest.ContentType = "";
			serverRequest.ContentLength = serverRequestData.Length;

			serverRequest.GetRequestStream().Write(
				serverRequestData, 0, serverRequestData.Length);
			serverRequest.GetRequestStream().Close();
		}

		serverResponse = (HttpWebResponse)serverRequest.GetResponse();
		if (serverResponse.StatusCode != HttpStatusCode.OK)
			return serverResponse.StatusCode;

		clientResponseData = SafeReadDataStream(
			serverResponse.GetResponseStream());
		if (clientResponseData == null)
		{
			serverResponse.Close();

			return HttpStatusCode.RequestEntityTooLarge;
		}

		serverResponse.Close();

		context.Response.ContentType = HttpContentTypeBase64;
		context.Response.StatusCode = (int)HttpStatusCode.OK;
		context.Response.Write(Convert.ToBase64String(clientResponseData));

		return HttpStatusCode.OK;
	}

	public void ProcessRequest(HttpContext context)
	{
		HttpStatusCode status = HttpStatusCode.InternalServerError;

		try
		{
			string requestType = context.Request.RequestType;

			if (requestType == "GET" || requestType == "POST")
				status = HandleRequest(context);
			else
				status = HttpStatusCode.BadRequest;
		}
		finally
		{
			if (status != HttpStatusCode.OK)
			{
				context.Response.Write("Виникла помилка при обробці запиту");
				context.Response.StatusCode = (int) status;
			}
		}
	}

	public bool IsReusable
	{
		get
		{
			return false;
		}
	}
}