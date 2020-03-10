//==============================================================================

importScripts(
	'euverifysign.types.js?version=1.0.2', 
	'euscpt.js?version=1.0.2',
	'euscpm.js?version=1.0.2',
	'euscp.js?version=1.0.2');

//==============================================================================

var URL_CAS_CERTIFICATES = "/verify/Data/CACertificates.p7b?version=1.0.17";
var URL_CAS = "/verify/Data/CAs.json?version=1.0.17";
var URL_XML_HTTP_PROXY_SERVICE = "/verify/Server/ProxyHandler.php";

var CZO_SERVER = "czo.gov.ua"

//==============================================================================

var s_loaded = false;
var s_verifyLargeFiles = true;
var s_cas = null;

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

			onSuccess(cas);
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
	CAsWithDirectAccess.push(CZO_SERVER);
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
		settings.SetPort('80');
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

//==============================================================================

function Initialize(data) {
	try {
		s_verifyLargeFiles = data.params.verifyLargeFiles;
		euSign.SetErrorMessageLanguage(data.params.langCode);
		euSign.Initialize();

		var _onSuccess = function() {
			var params = {
				'isFileSyncAPISupported' : euSign.isFileSyncAPISupported,
				'isFileASyncAPISupported': euSign.isFileASyncAPISupported
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

function IsSignerDigitalTimeStamp(info) {
	return info.GetExtKeyUsages().indexOf(UA_OID_EXT_KEY_USAGE_STAMP) > -1;
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
			"isDigitalStamp": IsSignerDigitalTimeStamp(signerCertInfo.infoEx)
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

		default:
			var error = euSign.MakeError(EU_ERROR_NOT_SUPPORTED);
			sendMessage(data.cmd, data, error, null);
			break;
	};
};

//==============================================================================

function EUSignCPModuleInitialized(isInitialized) {
	s_loaded = isInitialized;
}

var euSign = EUSignCP();

//==============================================================================
