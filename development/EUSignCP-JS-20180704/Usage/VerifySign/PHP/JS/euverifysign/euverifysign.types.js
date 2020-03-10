//=============================================================================

var EUVSError = function(errorCode, message) {
	this.errorCode = errorCode;
	this.message = message;
};

EUVSError.prototype.toString = function() {
	return this.message + '(' + this.errorCode + ')';
};

//=============================================================================

var EUVS_FILTER_SIGN_FILE_RESULT_NO_ERROR = 0;
var EUVS_FILTER_SIGN_FILE_RESULT_NO_FILE_WITH_DATA = 1;
var EUVS_FILTER_SIGN_FILE_RESULT_INVALID_FILE_FORMAT = 2;
var EUVS_FILTER_SIGN_FILE_RESULT_FILE_TOO_BIG = 3;
var EUVS_FILTER_SIGN_FILE_RESULT_FILE_READ_ERROR = 4;

//-----------------------------------------------------------------------------

var EUVSFilterSignFileResult = function(
	resultCode, isInternal, signFile, dataFile) {
	this.resultCode = resultCode;
	this.isInternal = isInternal;
	this.signFile = signFile;
	this.dataFile = dataFile;
};

//=============================================================================

var EUVSIsMobileBrowser = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
var EUVS_MAX_FILE_SIZE_MB = EUVSIsMobileBrowser ? 20 : 100;
var EUVS_VERIFY_LARGE_FILES = true;

//=============================================================================
