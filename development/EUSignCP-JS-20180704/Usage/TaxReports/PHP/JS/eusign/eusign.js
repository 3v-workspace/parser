//=============================================================================

var EUVS_WORKER_PATH = '/JS/eusign/eusign.worker.js?version=1.0.2';

//=============================================================================

function isWorkersSupported() {
	return (window.URL || window.webkitURL) &&
		window.Blob && window.Worker;
}

//=============================================================================

var EUSign = function() {
	this.Vendor = "JSC IIT";
	this.ClassVersion = "1.3.3";
	this.ClassName = "EUSign";

	this.m_debug = true;

	this.m_worker = null;
	this.m_isInitialized = false;
	this.m_langCode = EU_DEFAULT_LANG;
	this.m_isFileSyncAPISupported = false;
	this.m_isFileASyncAPISupported = false;
	this.m_callbacks = [];

	this.m_cas = null;
	this.m_isPrivateKeyReaded = false;
	
	this.m_base64Coder = new EndUserBase64Coder();
};

//--------------------------------------------------------------------------------

EUSign.prototype.postMessage = function(cmd, params, onSuccess, onError) {
	var callback_id = -1;

	if (onSuccess != null || onError != null) {
		var callback = {'onSuccess': onSuccess, 'onError': onError};
		callback_id = this.m_callbacks.push(callback);
	}

	this.m_worker.postMessage({
			'cmd': cmd,
			'params': params,
			'callback_id': callback_id
		});
};

//--------------------------------------------------------------------------------

EUSign.prototype.getCallback = function(callback_id) {
	var callback = this.m_callbacks[callback_id - 1];
	delete this.m_callbacks[callback_id - 1];

	return callback;
};

//--------------------------------------------------------------------------------

EUSign.prototype.initializeWorker = function() {
	var pThis = this;
	this.m_worker = new Worker(EUVS_WORKER_PATH);
	this.m_worker.onmessage = function(e) {
		var data = e.data;
		var params = data.params;
		var callback = null;

		callback = pThis.getCallback(data.callback_id);
		if (!callback)
			return;

		if (data.error != null) {
			if (callback != null) {
				var error = new EUVSError(
					data.error.errorCode, 
					data.error.message);
				callback.onError(error);
			}

			return;
		}

		switch (data.cmd) {
			case 'Initialize':
				pThis.m_isInitialized = true;
				pThis.m_isFileSyncAPISupported = 
					params.isFileSyncAPISupported;
				pThis.m_isFileASyncAPISupported = 
					params.isFileASyncAPISupported;
				pThis.m_cas = params.cas;
				callback.onSuccess();
				break;

			case 'SetCA':
				callback.onSuccess(null);
				break;

			case 'ReadPrivateKeyBinary':
			case 'ReadPrivateKeyFile':
				pThis.m_isPrivateKeyReaded = true;
				var ownerInfo = new EndUserOwnerInfo(null, null);
				ownerInfo.SetTransferableObject(params.ownerInfo);
				callback.onSuccess(ownerInfo);
				break;

			case 'SignFile':
				var signInfo = new EndUserSignInfo(null, null);
				signInfo.SetTransferableObject(params.signInfo);
				callback.onSuccess(signInfo, params.sign);
				break;

			case 'FilterSignFiles':
				callback.onSuccess(params.results);
				break;

			case 'GetDataFromSignedFile':
				callback.onSuccess(params.data);
				break;

			case 'VerifyFileWithExternalSign':
			case 'VerifyFileWithInternalSign':
				var signInfo = new EndUserSignInfo(null, null);
				signInfo.SetTransferableObject(params.signInfo);
				callback.onSuccess(signInfo);
				break;

			case 'VerifyFileWithInternalSigns':
				var signers = params.signerInfos;
				var signsInfo = [];

				for (var i = signers.length - 1; i >= 0 ; i--) {
					var _signerInfos = [];
					for (var j = 0; j < signers[i].length; j++){
						var signInfo = new EndUserSignInfo(null, null);
						signInfo.SetTransferableObject(
							signers[i][j].signerInfo);
						_signerInfos.push({
							"signerInfo": signInfo,
							"isTimeStamp": signers[i][j].isTimeStamp
						});
					}
					signsInfo.push(_signerInfos);
				}
				callback.onSuccess(signsInfo, params.data);
				break;
			
			case 'SetReportKeyFile': 
				var ownerInfo = new EndUserOwnerInfo(null, null);
				ownerInfo.SetTransferableObject(params.ownerInfo);
				callback.onSuccess(ownerInfo);
				break;

			case 'ProtectReports':
				callback.onSuccess(params.results);
				break;
			
			case 'UnprotectReceipts':
				var results = params.results;
				for (var i = 0; i < results.length; i++) {
					var initiators = results[i].initiators;
					for (var j = 0; j < initiators.length; j++) {
						var initiator;
						if (initiators[j].ClassName == 'EndUserSignInfo') {
							initiator = new EndUserSignInfo(null, null);
						} else {
							initiator = new EndUserSenderInfo(null, null);
						}
						
						initiator.SetTransferableObject(initiators[j]);
						initiators[j] = initiator;
					}
				}
				
				callback.onSuccess(params.results);
				break;
		}
	};

	this.m_worker.onerror = function(e) {
		if (pThis.m_debug)
			console.log(e);

		pThis.m_callbacks.forEach(function(callback) {
			var error = pThis.makeError(EU_ERROR_JS_LIBRARY_ERROR);
			callback.onError(error);
		});

		pThis.m_callbacks = [];
	};
};

//================================================================================

EUSign.prototype.makeError = function(errorCode) {
	var message = EU_ERRORS_STRINGS[this.m_langCode][errorCode];

	return new EUVSError(errorCode, message);
};

//--------------------------------------------------------------------------------

EUSign.prototype.isInitialized = function() {
	return this.m_isInitialized;
};

//--------------------------------------------------------------------------------

EUSign.prototype.initialize = function(onSuccess, onError) {
	if (!isWorkersSupported()) {
		onError(this.makeError(EU_ERROR_JS_BROWSER_NOT_SUPPORTED));
		return;
	}

	this.initializeWorker();

	var params = {
		'langCode': this.m_langCode,
		'verifyLargeFiles': EUVS_VERIFY_LARGE_FILES
	};

	this.postMessage('Initialize', params, onSuccess, onError);
};

//================================================================================

EUSign.prototype.base64Encode = function(data) {
	return this.m_base64Coder.encode(data);
}

//--------------------------------------------------------------------------------

EUSign.prototype.base64Decode = function(data) {
	return this.m_base64Coder.decode(data);
}

//=============================================================================

EUSign.prototype.getCAs = function() {
	return this.m_cas;
}

//--------------------------------------------------------------------------------

EUSign.prototype.setCA = function(ca, onSuccess, onError) {
	var params = {
		'caIssuerCN': ca != null ? ca.issuerCN : null
	};

	this.postMessage('SetCA', params, onSuccess, onError);
}

//=============================================================================

EUSign.prototype.isPrivateKeyReaded = function() {
	return this.m_isPrivateKeyReaded;
}

//--------------------------------------------------------------------------------

EUSign.prototype.readPrivateKeyBinary = function(
	key, password, certificates, ca, onSuccess, onError) {
	var pThis = this;

	this.m_isPrivateKeyReaded = false;

	if (!this.m_isInitialized) {
		var _onSuccess = function() {
			pThis.readPrivateKeyBinary(
				key, password, certificates, ca, 
				onSuccess, onError);
		}

		pThis.initialize(_onSuccess, onError);
		return;
	}

	var certsArr = null;
	if (certificates != null) {
		certsArr = [];
		var length = certificates.length;
		for (var i = 0; i < length; i++) {
			certsArr.push(certificates[i]);
		}
	}

	var params = {
		'key': key, 
		'password': password,
		'certificates': certsArr,
		'caIssuerCN': ca.issuerCN 
	};

	this.postMessage('ReadPrivateKeyBinary', params, onSuccess, onError);
}

//--------------------------------------------------------------------------------

EUSign.prototype.readPrivateKeyFile = function(
	keyFile, password, certificatesFiles, ca, onSuccess, onError) {
	var pThis = this;

	this.m_isPrivateKeyReaded = false;

	if (!this.m_isInitialized) {
		var _onSuccess = function() {
			pThis.readPrivateKeyFile(
				keyFile, password, certificatesFiles, ca, 
				onSuccess, onError);
		}

		pThis.initialize(_onSuccess, onError);
		return;
	}

	var certsArr = null;
	if (certificatesFiles != null) {
		certsArr = [];
		var length = certificatesFiles.length;
		for (var i = 0; i < length; i++) {
			certsArr.push(certificatesFiles[i]);
		}
	}

	var params = {
		'key': keyFile, 
		'password': password,
		'certificates': certsArr,
		'caIssuerCN': ca != null ? ca.issuerCN : null
	};

	this.postMessage('ReadPrivateKeyFile', params, onSuccess, onError);
}

//=============================================================================

EUSign.prototype.signFile = function(file, signAlgo,
	external, appendCert, onSuccess, onError) {
	var pThis = this;

	var params = {
		'file': file, 
		'signAlgo': signAlgo,
		'external': external,
		'appendCert': appendCert
	};

	this.postMessage('SignFile', params, onSuccess, onError);
}

//=============================================================================

EUSign.prototype.filterSignFiles = function(files, onSuccess, onError) {
	var pThis = this;

	if (!this.m_isInitialized) {
		var _onSuccess = function() {
			pThis.filterSignFiles(
				files, onSuccess, onError);
		}

		pThis.initialize(_onSuccess, onError);
		return;
	}

	var filesArr = [];
	var length = files.length;
	for (var i = 0; i < length; i++) {
		filesArr.push(files[i]);
	}

	var params = {'files': filesArr};

	this.postMessage('FilterSignFiles', params, onSuccess, onError);
};

//-----------------------------------------------------------------------------

EUSign.prototype.getDataFromSignedFile = function(
	signedFile, onSuccess, onError) {
	var pThis = this;

	if (!this.m_isInitialized) {
		var _onSuccess = function() {
			pThis.getDataFromSignedFile(
				signedFile, onSuccess, onError);
		}

		pThis.initialize(_onSuccess, onError);
		return;
	}

	var params = {'signedFile': signedFile};

	this.postMessage('GetDataFromSignedFile', params, onSuccess, onError);
};

//-----------------------------------------------------------------------------

EUSign.prototype.verifyFileWithExternalSign = function(
	file, fileWithSign, onSuccess, onError) {
	var pThis = this;

	if (!this.m_isInitialized) {
		var _onSuccess = function() {
			pThis.verifyFileWithExternalSign(
				file, fileWithSign, onSuccess, onError);
		}

		pThis.initialize(_onSuccess, onError);
		return;
	}

	var params = {'file': file, 'fileWithSign': fileWithSign};

	this.postMessage('VerifyFileWithExternalSign',
		params, onSuccess, onError);
};

//-----------------------------------------------------------------------------

EUSign.prototype.verifyFileWithInternalSign = function(
	signedFile, file, onSuccess, onError) {
	var pThis = this;

	if (!this.m_isInitialized) {
		var _onSuccess = function() {
			pThis.verifyFileWithInternalSign(
				signedFile, onSuccess, onError);
		}

		pThis.initialize(_onSuccess, onError);
		return;
	}

	var params = {'signedFile': signedFile, 'file': file};

	this.postMessage('VerifyFileWithInternalSign',
		params, onSuccess, onError);
};

//-----------------------------------------------------------------------------

EUSign.prototype.verifyFile = function(
	dataFile, signFile, onSuccess, onError) {
	if (dataFile == null) {
		this.verifyFileWithInternalSign(
			signFile, dataFile, onSuccess, onError);
	} else {
		this.verifyFileWithExternalSign(
			dataFile, signFile, onSuccess, onError);
	}
};

//-----------------------------------------------------------------------------

EUSign.prototype.verifyFileWithInternalSigns = function(
	signedFile, file, onSuccess, onError) {
	var pThis = this;

	if (!this.m_isInitialized) {
		var _onSuccess = function() {
			pThis.verifyFileWithInternalSign(
				signedFile, onSuccess, onError);
		}

		pThis.initialize(_onSuccess, onError);
		return;
	}

	var params = {'signedFile': signedFile, 'file': file};

	this.postMessage('VerifyFileWithInternalSigns',
		params, onSuccess, onError);
};

//=============================================================================

EUSign.prototype.setReportKeyFile = function(
	keyId, keyFile, password, certsFiles, onSuccess, onError) {
	var pThis = this;

	if (!this.m_isInitialized) {
		var _onSuccess = function() {
			pThis.setReportKeyFile(
				keyId, keyFile, password, 
				certsFiles, onSuccess, onError);
		}

		pThis.initialize(_onSuccess, onError);
		return;
	}

	var certsFilesArr = null;
	if (certsFiles != null) {
		certsFilesArr = [];
		var length = certsFiles.length;
		for (var i = 0; i < length; i++) {
			certsFilesArr.push(certsFiles[i]);
		}
	}

	var params = {
		'keyId': keyId,
		'keyFile': keyFile, 
		'password': password,
		'certsFiles': certsFiles
	};

	this.postMessage('SetReportKeyFile', params, onSuccess, onError);
}

//-----------------------------------------------------------------------------

EUSign.prototype.protectReports = function(
	reports, onSuccess, onError) {
	var pThis = this;

	if (!this.m_isInitialized) {
		var _onSuccess = function() {
			pThis.protectReports(
				keys, reports, onSuccess, onError);
		}

		pThis.initialize(_onSuccess, onError);
		return;
	}

	var params = {
		'reports': reports
	};

	this.postMessage('ProtectReports', params, onSuccess, onError);
};

//-----------------------------------------------------------------------------

EUSign.prototype.unprotectReceipts = function(
	keyId, receipts, onSuccess, onError) {
	var pThis = this;

	if (!this.m_isInitialized) {
		var _onSuccess = function() {
			pThis.unprotectReceipts(
				keyId, receipts, onSuccess, onError);
		}

		pThis.initialize(_onSuccess, onError);
		return;
	}

	var params = {'keyId': keyId, 'receipts': receipts};

	this.postMessage('UnprotectReceipts',
		params, onSuccess, onError);
};

//=============================================================================

var EndUserBase64Coder = function() {
	this.vendor = 'JSC IIT';
	this.classVersion = 1;
	this.className = 'EndUserBase64Coder';

	this.m_map = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
};

//--------------------------------------------------------------------------------

EndUserBase64Coder.prototype.encode = function(array) {
	var bytes;
	var i;
	var bytesLength;
	var base64Str = '';

	bytes = new Uint8Array(array);
	bytesLength = bytes.length;

	for (i = 0; i < bytesLength; i+=3) {
		base64Str += this.m_map[bytes[i] >> 2];
		base64Str += this.m_map[((bytes[i] & 3) << 4) | (bytes[i + 1] >> 4)];
		base64Str += this.m_map[((bytes[i + 1] & 15) << 2) | (bytes[i + 2] >> 6)];
		base64Str += this.m_map[bytes[i + 2] & 63];
	}

	if ((bytesLength % 3) === 2) {
		base64Str = base64Str.substring(0, base64Str.length - 1) + '=';
	} else if (bytesLength % 3 === 1) {
		base64Str = base64Str.substring(0, base64Str.length - 2) + '==';
	}

	return base64Str;
};

//--------------------------------------------------------------------------------

EndUserBase64Coder.prototype.decode = function(base64Str) {
	var bytes;
	var bytesLength;
	var i, p;
	var base64StrLength;
	var encoded1, encoded2, encoded3, encoded4;
	var arrayBuffer;

	bytesLength = base64Str.length * 0.75;
	base64StrLength = base64Str.length;

	if (base64Str[base64Str.length - 1] === '=') {
		bytesLength--;
		
		if (base64Str[base64Str.length - 2] === '=') {
			bytesLength--;
		}
	}

	arrayBuffer = new ArrayBuffer(bytesLength),
	bytes = new Uint8Array(arrayBuffer);

	p = 0;
	for (i = 0; i < base64StrLength; i+=4) {
		encoded1 = this.m_map.indexOf(base64Str[i]);
		encoded2 = this.m_map.indexOf(base64Str[i+1]);
		encoded3 = this.m_map.indexOf(base64Str[i+2]);
		encoded4 = this.m_map.indexOf(base64Str[i+3]);

		bytes[p++] = (encoded1 << 2) | (encoded2 >> 4);
		bytes[p++] = ((encoded2 & 15) << 4) | (encoded3 >> 2);
		bytes[p++] = ((encoded3 & 3) << 6) | (encoded4 & 63);
	}

	return bytes;
};

//================================================================================
