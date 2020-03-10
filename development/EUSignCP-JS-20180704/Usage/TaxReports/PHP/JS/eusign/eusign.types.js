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

//-----------------------------------------------------------------------------

var EUVSReportData = function(
	data, name, senderEMail, recipientCertFile) {
	this.ClassName = 'EUVSReportData';
	this.data = data;
	this.name = name;
	this.senderEMail = senderEMail;
	this.recipientCertFile = recipientCertFile;
}

//-----------------------------------------------------------------------------

var EUVSReportFile = function(
	file, senderEMail, recipientCertFile, outputFileName) {
	this.ClassName = 'EUVSReportFile';
	this.file = file;
	this.senderEMail = senderEMail;
	this.recipientCertFile = recipientCertFile;
	this.outputFileName = outputFileName;
}

//-----------------------------------------------------------------------------

var EUVSReportResultInfo = function(
	isSuccess, statusDescription, 
	inputFileName, outputFileName, outputData) {
	this.isSuccess = isSuccess;
	this.statusDescription = statusDescription;
	this.inputFileName = inputFileName;
	this.outputFileName = outputFileName;
	this.outputData = outputData;
}

//-----------------------------------------------------------------------------

var EUVSReceiptData = function(data) {
	this.ClassName = 'EUVSReceiptData';
	this.data = data;
}

//-----------------------------------------------------------------------------

var EUVSReceiptFile = function(
	file, outputFileName) {
	this.ClassName = 'EUVSReceiptFile';
	this.file = file;
	this.outputFileName = outputFileName;
}

//-----------------------------------------------------------------------------

var EUVSReceiptResultInfo = function(
	isSuccess, statusDescription, 
	inputFileName, outputFileName, outputData, 
	initiators, receiptNumber) {
	this.isSuccess = isSuccess;
	this.statusDescription = statusDescription;
	this.inputFileName = inputFileName;
	this.outputFileName = outputFileName;
	this.outputData = outputData;
	this.initiators = initiators;
	this.receiptNumber = receiptNumber;
}

//=============================================================================

var EUVSIsMobileBrowser = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
var EUVS_MAX_FILE_SIZE_MB = 2;
var EUVS_VERIFY_LARGE_FILES = true;

//=============================================================================
