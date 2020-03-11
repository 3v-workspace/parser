//=============================================================================

var EUVS_WORKER_PATH = 'JS/euverifysign/euverifysign.worker.js?=version=1.0.2';

//=============================================================================

function isWorkersSupported() {
	return (window.URL || window.webkitURL) &&
		window.Blob && window.Worker;
}

//=============================================================================

var EUVerifySign = function() {
	this.Vendor = "JSC IIT";
	this.ClassVersion = "1.1.0";
	this.ClassName = "EUVerifySign";

	this.m_debug = true;

	this.m_worker = null;
	this.m_isInitialized = false;
	this.m_langCode = EU_DEFAULT_LANG;
	this.m_isFileSyncAPISupported = false;
	this.m_isFileASyncAPISupported = false;
	this.m_callbacks = [];
};

//--------------------------------------------------------------------------------

EUVerifySign.prototype.postMessage = function(cmd, params, onSuccess, onError) {
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

EUVerifySign.prototype.getCallback = function(callback_id) {
	var callback = this.m_callbacks[callback_id - 1];
	delete this.m_callbacks[callback_id - 1];

	return callback;
};

//--------------------------------------------------------------------------------

EUVerifySign.prototype.initializeWorker = function() {
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
				callback.onSuccess();
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
							"isDigitalStamp": signers[i][j].isDigitalStamp
						});
					}
					signsInfo.push(_signerInfos);
				}
				callback.onSuccess(signsInfo, params.data);
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

EUVerifySign.prototype.makeError = function(errorCode) {
	var message = EU_ERRORS_STRINGS[this.m_langCode][errorCode];

	return new EUVSError(errorCode, message);
};

//--------------------------------------------------------------------------------

EUVerifySign.prototype.isInitialized = function() {
	return this.m_isInitialized;
};

//--------------------------------------------------------------------------------

EUVerifySign.prototype.initialize = function(onSuccess, onError) {
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

//=============================================================================

EUVerifySign.prototype.filterSignFiles = function(files, onSuccess, onError) {
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

EUVerifySign.prototype.getDataFromSignedFile = function(
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

EUVerifySign.prototype.verifyFileWithExternalSign = function(
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

EUVerifySign.prototype.verifyFileWithInternalSign = function(
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

EUVerifySign.prototype.verifyFile = function(
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

EUVerifySign.prototype.verifyFileWithInternalSigns = function(
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