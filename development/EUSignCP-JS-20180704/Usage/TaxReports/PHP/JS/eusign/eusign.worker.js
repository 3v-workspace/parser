//==============================================================================

var EU_MAX_DATA_SIZE_MB = 2;

//==============================================================================

importScripts(
	'eusign.types.js?version=1.0.4', 
	'euscpt.js?version=1.0.4',
	'euscpm.js?version=1.0.4',
	'euscp.js?version=1.0.4');

//==============================================================================

var URL_CAS_CERTIFICATES = "/Data/CACertificates.p7b?version=1.0.18";
var URL_CAS = "/Data/CAs.json?version=1.0.18";
var URL_XML_HTTP_PROXY_SERVICE = "/Server/ProxyHandler.php";

//==============================================================================

var CA_DEFAULT_SERVER = 'acskidd.gov.ua';
var CA_DEFAULT_PORT = '80';

var CZO_SERVER = "czo.gov.ua"

//==============================================================================

var s_loaded = false;
var s_verifyLargeFiles = true;
var s_cas = null;
var s_context = null;
var s_privKeyContext = null;

var s_reportsPKeys = [];

//==============================================================================

function sendMessage(data, e, params) {
	var error = (e != null) ? 
		{'errorCode': e.errorCode, 'message': e.message} : null;
	self.postMessage({
			'cmd': data.cmd,
			'callback_id': data.callback_id,
			'error': error,
			'params': params
		});
}

//==============================================================================

function LoadCAsCertificates(onSuccess, onError) {
	var _onSuccess = function(certificates) {
		try {
			euSign.SaveCertificates(certificates);
			onSuccess();
		} catch (e) {
			onError(e);
		}
	};

	euSign.LoadDataFromServer(URL_CAS_CERTIFICATES, 
		_onSuccess, onError, true);
};

//------------------------------------------------------------------------------

function LoadCAs(onSuccess, onError) {
	var _onSuccess = function(response) {
		try {
			var cas = JSON.parse(response.replace(/\\'/g, "'"));

			s_cas = cas;	

			onSuccess();
		} catch (e) {
			onError(e);
		}
	};

	euSign.LoadDataFromServer(URL_CAS, _onSuccess, onError, false);
};

//------------------------------------------------------------------------------

function SetOCSPAccessInfoSettings() {
	var settings = euSign.CreateOCSPAccessInfoModeSettings();
	settings.SetEnabled(true);
	euSign.SetOCSPAccessInfoModeSettings(settings);

	settings = euSign.CreateOCSPAccessInfoSettings();
	for (var i = 0; i < s_cas.length; i++) {
		settings.SetAddress(s_cas[i].ocspAccessPointAddress);
		settings.SetPort(s_cas[i].ocspAccessPointPort);

		for (var j = 0; j < s_cas[i].issuerCNs.length; j++) {
			settings.SetIssuerCN(s_cas[i].issuerCNs[j]);
			euSign.SetOCSPAccessInfoSettings(settings);
		}
	}
};

//------------------------------------------------------------------------------

function SetXMLHTTPDirectAccess() {
	var _addDNSName = function(uri, dnsNames) {
		if (uri == '')
			return;

		uri = (uri.indexOf("://") > -1) ? 
			uri.split('/')[2] : 
			uri.split('/')[0];

		if (dnsNames.indexOf(uri) >= 0)
			return;

		dnsNames.push(uri);
	};

	var CAsWithDirectAccess = [];
	euSign.SetXMLHTTPDirectAccess(true);
	//CAsWithDirectAccess.push(CZO_SERVER);
	for (var i = 0; i < s_cas.length; i++) {
		if (!s_cas[i].directAccess)
			continue;

		_addDNSName(s_cas[i].address, CAsWithDirectAccess);
		_addDNSName(s_cas[i].tspAddress, CAsWithDirectAccess);
		_addDNSName(s_cas[i].cmpAddress, CAsWithDirectAccess);
		_addDNSName(s_cas[i].ocspAccessPointAddress,
			CAsWithDirectAccess);
	}

	CAsWithDirectAccess.forEach(function(address) {
		euSign.AddXMLHTTPDirectAccessAddress(address);
	});
};

//------------------------------------------------------------------------------

function SetSettings(onSuccess, onError) {
	try {
		euSign.SetXMLHTTPProxyService(URL_XML_HTTP_PROXY_SERVICE);

		var settings = euSign.CreateFileStoreSettings();
		settings.SetPath('');
		settings.SetSaveLoadedCerts(true);
		euSign.SetFileStoreSettings(settings);

		settings = euSign.CreateProxySettings();
		euSign.SetProxySettings(settings);

		settings = euSign.CreateTSPSettings();
		euSign.SetTSPSettings(settings);

		settings = euSign.CreateOCSPSettings();
		settings.SetUseOCSP(true);
		settings.SetBeforeStore(true);
		settings.SetAddress('');
		settings.SetPort(CA_DEFAULT_PORT);
		euSign.SetOCSPSettings(settings);

		settings = euSign.CreateCMPSettings();
		euSign.SetCMPSettings(settings);

		settings = euSign.CreateLDAPSettings();
		euSign.SetLDAPSettings(settings);

		LoadCAs(
			function() {
				try {
					SetOCSPAccessInfoSettings();
					SetXMLHTTPDirectAccess();
					onSuccess();
				} catch (e) {
					onError(e);
				}
			}, onError);
	} catch (e) {
		onError(e);
	}
}

//------------------------------------------------------------------------------

function SetCASettings(caIssuerCN, onSuccess, onError) {
	try {
		var caServer = null;
		var offline = true;
		var useCMP = false;

		if (s_cas == null) {
			onError(euSign.MakeError(EU_ERROR_BAD_PARAMETER));
			return;
		}

		if (caIssuerCN != null) {
			for (var i = 0; i < s_cas.length; i++) {
				if (caIssuerCN == s_cas[i].issuerCNs[0]) {
					caServer = s_cas[i];
					break;
				}
			}
		}

		offline = ((caServer == null) || 
			(caServer.address == "")) ?
			true : false;
		useCMP = (!offline && (caServer.cmpAddress != ""));

		settings = euSign.CreateTSPSettings();
		if (!offline) {
			settings.SetGetStamps(true);
			if (caServer.tspAddress != "") {
				settings.SetAddress(caServer.tspAddress);
				settings.SetPort(caServer.tspAddressPort);
			} else {
				settings.SetAddress(CA_DEFAULT_SERVER);
				settings.SetPort(CA_DEFAULT_PORT);
			}
		}
		euSign.SetTSPSettings(settings);

		settings = euSign.CreateOCSPSettings();
		if (!offline) {
			settings.SetUseOCSP(true);
			settings.SetBeforeStore(true);
			settings.SetAddress(caServer.ocspAccessPointAddress);
			settings.SetPort(caServer.ocspAccessPointPort);
		}
		euSign.SetOCSPSettings(settings);

		settings = euSign.CreateCMPSettings();
		settings.SetUseCMP(useCMP);
		if (useCMP) {
			settings.SetAddress(caServer.cmpAddress);
			settings.SetPort(CA_DEFAULT_PORT);
		}
		euSign.SetCMPSettings(settings);

		onSuccess();
	} catch (e) {
		onError(e);
		return;
	}
}

//==============================================================================

function Initialize(data) {
	try {
		s_verifyLargeFiles = data.params.verifyLargeFiles;
		euSign.SetErrorMessageLanguage(data.params.langCode);
		euSign.Initialize();
		s_context = euSign.CtxCreate();

		s_reportsPKeys[EU_KEY_ID_ACCOUNTANT] = null;
		s_reportsPKeys[EU_KEY_ID_DIRECTOR] = null;
		s_reportsPKeys[EU_KEY_ID_STAMP] = null;

		var _onSuccess = function() {
			var cas = [];

			for (var i = 0; i < s_cas.length; i++) {
				var useCMP = (s_cas[i].cmpAddress != "");
				var certsInKey = s_cas[i].certsInKey;

				cas.push({
					"issuerCN":s_cas[i].issuerCNs[0],
					"loadPKCertsFromFile": !useCMP && !certsInKey});
			}

			var params = {
				'isFileSyncAPISupported' : euSign.isFileSyncAPISupported,
				'isFileASyncAPISupported': euSign.isFileASyncAPISupported,
				"cas": cas
			};

			sendMessage(data, null, params);
		}

		var _onError = function(e) {
			sendMessage(data, e, null);
		};

		if (euSign.DoesNeedSetSettings()) {
			var _onSuccessSetSettings = function() {
				LoadCAsCertificates(_onSuccess, _onError);
			};

			SetSettings(_onSuccessSetSettings, _onError);
		} else {
			LoadCAsCertificates(_onSuccess, _onError);
		}
	} catch (e) {
		sendMessage(data, e, null);
		return;
	}
}

//==============================================================================

function SetCA(data) {
	var _onError = function(e) {
		sendMessage(data, e, null);
	};

	var _onSuccess = function() {
		sendMessage(data, null, null);
	};

	SetCASettings(
		data.params.caIssuerCN, 
		_onSuccess, _onError);
}

//==============================================================================

function ReadPrivateKey(key, password, certificates,
	caIssuerCN, onSuccess, onError) {
	var _onSuccess = function() {
		try {
			var info;

			if ((key == null) || (password == null)) {
				onError(euSign.MakeError(EU_ERROR_BAD_PARAMETER));
				return;
			}

			if (certificates != null) {
				for (var i = 0; i < certificates.length; i++) {
					euSign.SaveCertificate(certificates[i]);
				}
			}

			if (s_privKeyContext != null) {
				euSign.CtxFreePrivateKey(s_privKeyContext);
				s_privKeyContext = null;
			}

			s_privKeyContext = euSign.CtxReadPrivateKeyBinary(
				s_context, key, password);

			onSuccess(s_privKeyContext.GetOwnerInfo());
		} catch (e) {
			onError(e);
			return;
		}
	};

	SetCASettings(caIssuerCN, 
		_onSuccess, onError);
}

//------------------------------------------------------------------------------

function ReadPrivateKeyBinary(data) {
	var _onError = function(e) {
		sendMessage(data, e, null);
	};

	var _onSuccess = function(info) {
		var params = {
			'ownerInfo' : info.GetTransferableObject()
		};

		sendMessage(data, null, params);
	};
	
	ReadPrivateKey(
		data.params.key, data.params.password, 
		data.params.certificates,
		data.params.caIssuerCN, 
		_onSuccess, _onError);
}

//------------------------------------------------------------------------------

function ReadPrivateKeyFile(data) {
	var _onError = function(e) {
		sendMessage(data, e, null);
	};

	var _onSuccess = function(info) {
		var params = {
			'ownerInfo' : info.GetTransferableObject()
		};

		sendMessage(data, null, params);
	};

	var _onSuccessReadPKeyFile = function(keyFile) {
		if (data.params.certificates != null) {
			var _onSuccessReadCerts = function(results) {
				var certs = [];
				for (var i = 0; i < results.length; i++) {
					certs.push(results[i].data);
				}

				ReadPrivateKey(
					keyFile.data, data.params.password, 
					certs, data.params.caIssuerCN, 
					_onSuccess, _onError);
			};

			euSign.ReadFiles(data.params.certificates, 
				_onSuccessReadCerts, _onError);
		} else {
				ReadPrivateKey(
					keyFile.data, data.params.password, 
					null, data.params.caIssuerCN, 
					_onSuccess, _onError);
		}
	};

	euSign.ReadFile(data.params.key, 
		_onSuccessReadPKeyFile, _onError);
}

//==============================================================================

function RemoveFileExtension(file) {
	var lastIndex = file.name.lastIndexOf('.');
	if (lastIndex <= 0)
		return file.name;

	return file.name.substr(0, lastIndex);
}

//------------------------------------------------------------------------------

function GetFileExtension(file) {
	var lastIndex = file.name.lastIndexOf('.');
	if (lastIndex <= 0)
		return "";

	return file.name.substr(lastIndex + 1, file.name.length - 1);
}

//------------------------------------------------------------------------------

function SearchFileByName(fileName, files) {
	for (var i = 0; i < files.length; i++) {
		if (fileName == files[i].name)
			return files[i];
	}

	return null;
}

//------------------------------------------------------------------------------

function FilterSignFiles(data) {
	var files = data.params.files;

	if ((files == null) || (files.length <= 0)) {
		sendMessage(data, euSign.MakeError(EU_ERROR_BAD_PARAMETER), null);
		return;
	}

	var _onSuccess = function(results) {
		var params = {'results': results};
		sendMessage(data, null, params);
	};

	var state = new Object();

	state.files = files;
	state.index = 0;
	state.filesSignInternal = [];
	state.filesSignExternal = [];
	state.filesData = [];
	state.filesBig = [];
	state.filesInvalid = [];

	var _onIsDataInSignedFileAvailableSuccess = function(isAvailable) {
		if (isAvailable)
			state.filesSignInternal.push(state.files[state.index]);
		else
			state.filesSignExternal.push(state.files[state.index]);

		state.index++;
		_filterWithState(state);
	};
	
	var _onIsDataInSignedFileAvailableError = function(e) {
		if (e.errorCode == EU_ERROR_PKI_FORMATS_FAILED) {
			state.filesData.push(state.files[state.index]);
		} else {
			state.filesInvalid.push(state.files[state.index]);
		}

		state.index++;
		_filterWithState(state);
	};

	var maxFileSize = EUVS_MAX_FILE_SIZE_MB * EU_ONE_MB;
	var _filterWithState = function(state) {
		if (state.index < state.files.length) {
			if (!s_verifyLargeFiles && 
				(state.files[state.index].size > maxFileSize)) {
				state.filesBig.push(state.files[state.index]);

				state.index++;
				_filterWithState(state);
				return;
			}

			euSign.IsDataInSignedFileAvailable(
				state.files[state.index], 
				_onIsDataInSignedFileAvailableSuccess,
				_onIsDataInSignedFileAvailableError);
			return;
		}

		var results = [];

		for (var i = 0; i < state.filesSignInternal.length; i++) {
			var result = new EUVSFilterSignFileResult(
				EUVS_FILTER_SIGN_FILE_RESULT_NO_ERROR, true, 
				state.filesSignInternal[i], null);
			results.push(result);
		}

		var filesSignExternal = [];
		for (var i = 0; i < state.filesSignExternal.length; i++) {
			var result;
			var signFile = state.filesSignExternal[i];
			var dataFile = null;
			var dataFileName;
			var resultCode = EUVS_FILTER_SIGN_FILE_RESULT_NO_FILE_WITH_DATA;

			if ((signFile.name.length > 5) && 
				(GetFileExtension(signFile) == "p7s")) {
				dataFileName = RemoveFileExtension(signFile);
				dataFile = SearchFileByName(dataFileName, state.filesData);

				if (dataFile != null) {
					state.filesData.splice(
						state.filesData.indexOf(dataFile), 1);
					resultCode = EUVS_FILTER_SIGN_FILE_RESULT_NO_ERROR;
				} else {
					dataFile = SearchFileByName(dataFileName, state.filesBig);
					if (dataFile != null) {
						state.filesBig.splice(
							state.filesBig.indexOf(dataFile), 1);
						resultCode = EUVS_FILTER_SIGN_FILE_RESULT_FILE_TOO_BIG;
					}
				}
			}

			var result = new EUVSFilterSignFileResult(
				resultCode, false, signFile, dataFile);
			results.push(result);
		}

		for (var i = 0; i < state.filesData.length; i++) {
			var result = new EUVSFilterSignFileResult(
				EUVS_FILTER_SIGN_FILE_RESULT_INVALID_FILE_FORMAT,
				false, state.filesData[i], null);
			results.push(result);
		}

		for (var i = 0; i < state.filesBig.length; i++) {
			var result = new EUVSFilterSignFileResult(
				EUVS_FILTER_SIGN_FILE_RESULT_FILE_TOO_BIG,
				false, state.filesBig[i], null);
			results.push(result);
		}

		for (var i = 0; i < state.filesInvalid.length; i++) {
			var result = new EUVSFilterSignFileResult(
				EUVS_FILTER_SIGN_FILE_RESULT_FILE_READ_ERROR,
				false, state.filesInvalid[i], null);
			results.push(result);
		}

		_onSuccess(results);
	}

	_filterWithState(state);
}

//==============================================================================

function GetDataFromSignedFile(data) {
	var signedFile = data.params.signedFile;

	var _onSuccess = function(signedFileData) {
		var params = {'data': signedFileData};
		self.sendMessage(data, null, params);
		signedFileData = null;
	};

	var _onError = function(e) {
		sendMessage(data, e, null);
	};

	euSign.GetDataFromSignedFile(signedFile, _onSuccess, _onError);
}

//------------------------------------------------------------------------------

function IsCertDigitalTimeStamp(info) {
	return info.GetExtKeyUsages().indexOf(UA_OID_EXT_KEY_USAGE_STAMP) > -1;
}

//==============================================================================

function GetCertKeyType(signAlgo) {
	switch (signAlgo) {
		case EU_CTX_SIGN_DSTU4145_WITH_GOST34311:
			return EU_CERT_KEY_TYPE_DSTU4145;
		
		case EU_CTX_SIGN_RSA_WITH_SHA:
			return EU_CERT_KEY_TYPE_RSA;
	}

	return EU_CERT_KEY_TYPE_UNKNOWN;
}

//------------------------------------------------------------------------------

function GetHashAlgo(signAlgo, publicKeyBits) {
	switch (signAlgo) {
		case EU_CTX_SIGN_DSTU4145_WITH_GOST34311:
			return EU_CTX_HASH_ALGO_GOST34311;
		
		case EU_CTX_SIGN_RSA_WITH_SHA:
			return (publicKeyBits < 2048) ? 
				EU_CTX_HASH_ALGO_SHA160 :
				EU_CTX_HASH_ALGO_SHA256;
	}

	return EU_CTX_HASH_ALGO_UNKNOWN;
}

//==============================================================================

function SignFileInternal(signAlgo, file, appendCert, data) {
	var _onError = function(e) {
		sendMessage(data, e, null);
	};

	var _onSuccess = function(signedData) {
		var signInfo;

		try {
			signInfo = euSign.CtxVerifyDataInternal(
				s_context, 0, signedData);
		} catch (e) {
			onError(e);
			return;
		}

		var params = {
			'sign': signedData,
			'signInfo': signInfo.GetTransferableObject()
		};

		sendMessage(data, null, params);
	}

	try {
		euSign.CtxSignFile(s_privKeyContext, signAlgo,
			file, false, appendCert, null, 
			_onSuccess, _onError);
	} catch (e) {
		_onError(e);
	}
}

//------------------------------------------------------------------------------

function SignFileExternal(signAlgo, file, appendCert, data) {
	var _onError = function(e) {
		sendMessage(data, e, null);
	};

	var _onSuccess = function(hash) {
		var sign;
		var signInfo;

		try {
			sign = euSign.CtxSignHashValue(
				s_privKeyContext, signAlgo, hash, appendCert);
			signInfo = euSign.CtxVerifyHashValue(
				s_context, hash, 0, sign);
		} catch (e) {
		
		}
		
		var params = {
			'sign': sign,
			'signInfo': signInfo.GetTransferableObject()
		};

		self.sendMessage(data, null, params);
	}

	var certData;
	var hashAlgo;
	
	try {
		var cert;

		cert = euSign.CtxGetOwnCertificate(
			s_privKeyContext, GetCertKeyType(signAlgo), 
			EU_KEY_USAGE_DIGITAL_SIGNATURE);
		hashAlgo = GetHashAlgo(signAlgo,
			cert.GetInfoEx().GetPublicKeyBits());
		certData = cert.GetData();
	} catch (e) {
		onError(e);
	}

	euSign.CtxHashFile(s_context, hashAlgo,
		certData, file, _onSuccess, _onError);
}

//------------------------------------------------------------------------------

function SignFile(data) {
	var file = data.params.file;
	var signAlgo = data.params.signAlgo;
	var external = data.params.external;
	var appendCert = data.params.appendCert;

	if (external)
		SignFileExternal(signAlgo, file, appendCert, data);
	else
		SignFileInternal(signAlgo, file, appendCert, data);
}

//==============================================================================

function VerifyFileWithExternalSign(data) {
	var file = data.params.file;
	var fileWithSign = data.params.fileWithSign;

	var _onSuccess = function(signInfo) {
		var params = {'signInfo': signInfo.GetTransferableObject()};
		self.sendMessage(data, null, params);
	};

	var _onError = function(e) {
		sendMessage(data, e, null);
	};

	euSign.VerifyFileWithExternalSign(file, fileWithSign, 
		_onSuccess, _onError);
}

//------------------------------------------------------------------------------

function VerifyFileWithInternalSign(data) {
	var signedFile = data.params.signedFile;
	var file = data.params.file;

	var _onSuccess = function(signInfo) {
		var params = {'signInfo': signInfo.GetTransferableObject()};
		self.sendMessage(data, null, params);
	};

	var _onError = function(e) {
		sendMessage(data, e, null);
	};

	euSign.VerifyFileWithInternalSign(signedFile, file,
		_onSuccess, _onError);
}

//------------------------------------------------------------------------------

function VerifyDataWithInternalSigns(context, signedData, signerInfos) {
	var isInternalSign;
	var signersCount;
	var signer;
	var data;

	try {
		isInternalSign = euSign.IsDataInSignedDataAvailable(signedData);
	} catch (e) {
		if (e.errorCode != EU_ERROR_PKI_FORMATS_FAILED)
			throw e;

		isInternalSign = false;
	}

	if (!isInternalSign) {
		return null;
	}

	signersCount = euSign.CtxGetSignsCount(context, signedData);
	for (var i = 0; i < signersCount; i++) {
		signer = euSign.CtxVerifyDataInternal(context, i, signedData);
		signerCertInfo = euSign.CtxGetSignerInfo(context, i, signedData);
		data = signer.data;
		signer.data = null;
		signerInfos.push({
			"signerInfo": signer.GetTransferableObject(),
			"isTimeStamp": IsCertDigitalTimeStamp(signerCertInfo.infoEx)
			});
	}

	return data;
}

//------------------------------------------------------------------------------

function VerifyFileWithInternalSigns(data) {
	var signedFile = data.params.signedFile;
	var file = data.params.file;

	var signerInfos = [];
	var signedData = null;

	var _onError = function(e) {
		sendMessage(data, e, null);
	};

	var _onSuccess = function(signedFileData) {
		var _tmpData = signedFileData.data;
		var _signers = [];
		var context = null;
		var verifiedData = signedFileData.data;

		try {
			context = euSign.CtxCreate();
			euSign.CtxSetParameter(context, EU_RESOLVE_OIDS_PARAMETER, false);
			while((_tmpData = VerifyDataWithInternalSigns(
						context, _tmpData, _signers)) != null) {
				verifiedData = _tmpData;
				signerInfos.push(_signers);
				_signers = [];
			}
			euSign.CtxFree(context);
		} catch (e) {
			if (context != null)
				euSign.CtxFree(context);
			_onError(e);
			return;
		}

		var params = {
			'signerInfos': signerInfos,
			'data': verifiedData
		};
		signerInfos = null;
		self.sendMessage(data, null, params);
	};

	euSign.ReadFile(signedFile, _onSuccess, _onError);
}

//==============================================================================

function SetReportKeyFile(data) {
	var keyId = data.params.keyId;
	var keyFile = data.params.keyFile;
	var password = data.params.password;
	var certsFiles = data.params.certsFiles;

	if (keyId != EU_KEY_ID_ACCOUNTANT &&
		keyId != EU_KEY_ID_DIRECTOR &&
		keyId != EU_KEY_ID_STAMP) {
		var e = euSign.MakeError(EU_ERROR_BAD_PARAMETER);
		sendMessage(data, e, null);
		return;
	}

	try {
		if (certsFiles != null &&
			certsFiles.length != 0) {
			var files = euSign.ReadFiles(certsFiles);
			for (var i = 0; i < files.length; i++) {
				euSign.SaveCertificate(files[i].GetData());
			}
		}

		var pkFile = euSign.ReadFile(keyFile);
		if (s_reportsPKeys[keyId] != null) {
			euSign.CtxFreePrivateKey(s_reportsPKeys[keyId]);
			s_reportsPKeys[keyId] = null;
		}

		s_reportsPKeys[keyId] = euSign.CtxReadPrivateKeyBinary(
			s_context, pkFile.GetData(), password);
		var ownerInfo = s_reportsPKeys[keyId].GetOwnerInfo();
		if (keyId == EU_KEY_ID_STAMP) {
			try {
				euSign.CtxSetParameter(s_context, 
					EU_RESOLVE_OIDS_CONTEXT_PARAMETER, false);
				var cert = euSign.CtxGetOwnCertificate(
						s_reportsPKeys[keyId], 
						EU_CERT_KEY_TYPE_DSTU4145,
						EU_KEY_USAGE_DIGITAL_SIGNATURE);
				if (!IsCertDigitalTimeStamp(cert.GetInfoEx()))
					euSign.RaiseError(EU_ERROR_BAD_PARAMETER);
			} catch (e) {
				euSign.CtxSetParameter(s_context, 
					EU_RESOLVE_OIDS_CONTEXT_PARAMETER, true);
				throw e;
			}

			euSign.CtxSetParameter(s_context, 
				EU_RESOLVE_OIDS_CONTEXT_PARAMETER, true);
		}
		
		var params = {
			'ownerInfo' : ownerInfo.GetTransferableObject()
		};
		sendMessage(data, null, params);
	} catch (e) {
		sendMessage(data, e, null);
	}
}

//------------------------------------------------------------------------------

function ProtectReport(report) {
	var isDataReport = true;

	try {
		var reportData;
		var reportName;
		var recipientCert;

		isDataReport = report.ClassName == 'EUVSReportData';
		reportName = isDataReport ? report.name : report.file.name;
		reportData = isDataReport ? 
			report.data : euSign.ReadFile(report.file).GetData();
		recipientCert = euSign.ReadFile(report.recipientCertFile);
		senderEMail = report.senderEMail;

		var _sign = function(keyCtx, data) {
			data = euSign.CtxSignData(keyCtx, 
				EU_CTX_SIGN_DSTU4145_WITH_GOST34311, 
				data, false, true);
			return euSign.AppendCryptoHeader(
				EU_HEADER_CA_TYPE, 
				EU_HEADER_PART_TYPE_SIGNED, data);
		}

		var _isMultiCert = function(keyCtx) {
			try {
				var cert = euSign.CtxGetOwnCertificate(
					keyCtx, EU_CERT_KEY_TYPE_DSTU4145,
					EU_KEY_USAGE_DIGITAL_SIGNATURE | 
						EU_KEY_USAGE_KEY_AGREEMENT);
				return true;
			} catch (e) {
				return false;
			}
		}

		var ownCert;
		var accountantPKey = s_reportsPKeys[EU_KEY_ID_ACCOUNTANT];
		var directorPKey = s_reportsPKeys[EU_KEY_ID_DIRECTOR];
		var stampPKey = s_reportsPKeys[EU_KEY_ID_STAMP];

		if (accountantPKey != null)
			reportData = _sign(accountantPKey, reportData);
		
		if (directorPKey != null)
			reportData = _sign(directorPKey, reportData);
		
		if (stampPKey != null)
			reportData = _sign(stampPKey, reportData);
		
		if (directorPKey != null || 
			stampPKey != null) {
			var pkCtx = (stampPKey != null) ? 
				stampPKey : directorPKey;

			reportData = euSign.CtxEnvelopData(pkCtx, 
				[recipientCert.GetData()],
				EU_RECIPIENT_APPEND_TYPE_BY_ISSUER_SERIAL,
				false, false, reportData);
			
			reportData = euSign.AppendCryptoHeader(
				EU_HEADER_CA_TYPE, 
				EU_HEADER_PART_TYPE_ENCRYPTED, reportData);
			
			ownCert = euSign.CtxGetOwnCertificate(
				pkCtx, EU_CERT_KEY_TYPE_DSTU4145,
				EU_KEY_USAGE_KEY_AGREEMENT);
			
			if (!_isMultiCert(pkCtx)) {
				var certHeader = euSign.AppendCryptoHeader(
					EU_HEADER_CA_TYPE, 
					EU_HEADER_PART_TYPE_CERTCRYPT, 
					ownCert.GetData());

				var tmp = new Uint8Array(certHeader.byteLength + 
					reportData.byteLength);
				tmp.set(new Uint8Array(certHeader), 0);
				tmp.set(new Uint8Array(reportData), certHeader.byteLength);

				reportData = tmp;
			}

			reportData = _sign(pkCtx, reportData);
		} else {
			ownCert = euSign.CtxGetOwnCertificate(
				accountantPKey, 
				EU_CERT_KEY_TYPE_DSTU4145,
				EU_KEY_USAGE_DIGITAL_SIGNATURE);
		}

		reportData = euSign.AppendTransportHeader(
			EU_HEADER_CA_TYPE, reportName, senderEMail,
			ownCert.GetData(), reportData);

		return new EUVSReportResultInfo(true, 
			euSign.GetErrorDescription(EU_ERROR_NONE), 
			isDataReport ? report.name : report.file.name, 
			isDataReport ? '' : report.outputFileName,
			reportData);
	} catch (e) {
		return new EUVSReportResultInfo(false,
			e.toString(), 
			isDataReport ? report.name : report.file.name, 
			isDataReport ? '' : report.outputFileName, null);
	}
}

//------------------------------------------------------------------------------

function ProtectReports(data) {
	var _onError = function(e) {
		sendMessage(data, e, null);
	};

	if (s_reportsPKeys[EU_KEY_ID_ACCOUNTANT] == null &&
		s_reportsPKeys[EU_KEY_ID_DIRECTOR] == null &&
		s_reportsPKeys[EU_KEY_ID_STAMP] == null) {
		_onError(euSign.MakeError(EU_ERROR_BAD_PARAMETER));
		return;
	}

	var results = [];
	var reports = data.params.reports;
	for (var i = 0; i < reports.length; i++) {
		results.push(ProtectReport(reports[i]));
	}

	var params = {
		'results' : results
	};

	sendMessage(data, null, params);
}

//------------------------------------------------------------------------------

function UnprotectReceipt(keyCtx, receipt) {
	var isDataReceipt = receipt.ClassName == 'EUVSReceiptData';;
	
	var result = new EUVSReceiptResultInfo(false, '',
		isDataReceipt ? '' : receipt.file.name, 
		isDataReceipt ? '' : receipt.outputFileName, 
		null, [], null);

	try {
		
		var receiptData = isDataReceipt ?
			receipt.data : euSign.ReadFile(receipt.file).GetData(); 
		
		var headerInfo = euSign.ParseTransportHeader(receiptData);
		result.receiptNumber = headerInfo.GetReceiptNumber();
		var receiptData = headerInfo.GetCryptoData();
		
		while (true) {
			try {
				headerInfo = euSign.ParseCryptoHeader(receiptData);
			} catch (e) {
				if (e.GetErrorCode() != EU_ERROR_BAD_PARAMETER) {
					throw e;
				}
				
				break;
			}

			var cryptoData = headerInfo.GetCryptoData();

			switch (headerInfo.GetHeaderType()) {
				case EU_HEADER_PART_TYPE_SIGNED:
					var signInfo = euSign.CtxVerifyDataInternal(
						s_context, 0, cryptoData);
					receiptData = signInfo.GetData();
					signInfo.data = null;
					result.initiators.push(
						signInfo.GetTransferableObject());
				break;
				
				case EU_HEADER_PART_TYPE_ENCRYPTED:
					var senderInfo = euSign.CtxDevelopData(
						keyCtx, cryptoData, null);
					receiptData = senderInfo.GetData();
					senderInfo.data = null;
					result.initiators.push(
						senderInfo.GetTransferableObject());
				break;

				case EU_HEADER_PART_TYPE_STAMPED:
				case EU_HEADER_PART_TYPE_CERTCRYPT:
					receiptData = receiptData.slice(
						headerInfo.GetHeaderSize() + cryptoData.length,
						receiptData.length);
				break;

				default:
					euSign.RaiseError(EU_ERROR_PKI_FORMATS_FAILED);
			}
		}

		result.isSuccess = true;
		result.statusDescription = 
			euSign.GetErrorDescription(EU_ERROR_NONE);
		result.outputData = receiptData;
		return result;
	} catch (e) {
		result.isSuccess = false;
		result.statusDescription = e.toString();
		return result;
	}
}

//------------------------------------------------------------------------------

function UnprotectReceipts(data) {
	var _onError = function(e) {
		sendMessage(data, e, null);
	};

	var keyId = data.params.keyId;
	if (s_reportsPKeys[keyId] == null) {
		_onError(euSign.MakeError(EU_ERROR_BAD_PARAMETER));
	}

	var results = [];
	var receipts = data.params.receipts;
	for (var i = 0; i < receipts.length; i++) {
		results.push(UnprotectReceipt(
			s_reportsPKeys[keyId], receipts[i]));
	}

	var params = {
		'results' : results
	};

	sendMessage(data, null, params);
}

//==============================================================================

onmessage = function(e) {
	if (!s_loaded) {
		setTimeout(function() {
				onmessage(e);
			}, 100);
		return;
	}

	var data = e.data;

	switch (data.cmd) {
		case 'Initialize':
			Initialize(data);
			break;

		case 'SetCA':
			SetCA(data);
			break;

		case 'ReadPrivateKeyBinary':
			ReadPrivateKeyBinary(data);
			break;

		case 'ReadPrivateKeyFile':
			ReadPrivateKeyFile(data);
			break;

		case 'SignFile':
			SignFile(data);
			break;

		case 'FilterSignFiles':
			FilterSignFiles(data);
			break;

		case 'GetDataFromSignedFile':
			GetDataFromSignedFile(data);
			break;

		case 'VerifyFileWithExternalSign':
			VerifyFileWithExternalSign(data);
			break;

		case 'VerifyFileWithInternalSign':
			VerifyFileWithInternalSign(data);
			break;
		
		case 'VerifyFileWithInternalSigns':
			VerifyFileWithInternalSigns(data);
			break;

		case 'SetReportKeyFile':
			SetReportKeyFile(data);
			break;

		case 'ProtectReports':
			ProtectReports(data);
			break;
			
		case 'UnprotectReceipts':
			UnprotectReceipts(data);
			break;

		default:
			var error = euSign.MakeError(EU_ERROR_NOT_SUPPORTED);
			sendMessage(data, error, null);
			break;
	};
};

//==============================================================================

function EUSignCPModuleInitialized(isInitialized) {
	s_loaded = isInitialized;
}

var euSign = EUSignCP();

//==============================================================================
