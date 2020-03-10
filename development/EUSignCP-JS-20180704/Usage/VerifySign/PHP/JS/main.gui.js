//=============================================================================

var euVerifySign;
var spinner;

//=============================================================================

var EUVS_SIGN_STATE_NOT_CHECKED = 0;
var EUVS_SIGN_STATE_CHECKING = 1;
var EUVS_SIGN_STATE_CHECKED = 2;
var EUVS_SIGN_STATE_FILE_NOT_FOUND = 3;
var EUVS_SIGN_STATE_FILE_INVALID = 4;
var EUVS_SIGN_STATE_FILE_READ_ERROR = 5;
var EUVS_SIGN_STATE_FILE_TOO_BIG = 6;
var EUVS_SIGN_STATE_CHECK_ERROR = 7;

var EUVS_SIGN_STATE_MSG_NOT_CHECKED = 'Не перевірено';
var EUVS_SIGN_STATE_MSG_CHECKING = 'Перевіряється...';
var EUVS_SIGN_STATE_MSG_CHECKED = 'Перевірено';
var EUVS_SIGN_STATE_MSG_CHECK_ERROR = 'Помилка при перевірці';

var EUVS_RESULT_TABLE_COLUMN_INDEX_STATE = 2;
var EUVS_RESULT_TABLE_COLUMN_INDEX_INFO = 3;
var EUVS_RESULT_TABLE_COLUMN_INDEX_FILE_WITH_DATA = 4;
var EUVS_RESULT_TABLE_COLUMN_INDEX_ROW_DATA = 5;

//=============================================================================

var EUVerifySignResultTR = function(
	dataFile, signFile, internalSign, state, info, error) {
	this.dataFile = dataFile;
	this.signFile = signFile;
	this.internalSign = internalSign;
	this.state = state;
	this.info = info;
	this.error = error;
	this.id = hashCode(signFile.name);
};

//-----------------------------------------------------------------------------

EUVerifySignResultTR.prototype.imageName = function() {
	switch(this.state) {
		case EUVS_SIGN_STATE_FILE_NOT_FOUND:
			return "CertificateWarning.png";
		case EUVS_SIGN_STATE_CHECK_ERROR:
		case EUVS_SIGN_STATE_FILE_INVALID:
		case EUVS_SIGN_STATE_FILE_READ_ERROR:
		case EUVS_SIGN_STATE_FILE_TOO_BIG:
			return "CertificateError.png";
		case EUVS_SIGN_STATE_CHECKED:
			return "CertificateCheck.png";
		case EUVS_SIGN_STATE_CHECKING:
		case EUVS_SIGN_STATE_NOT_CHECKED:
		default:
			return "CertificateProcess.png";
	}
};

//-----------------------------------------------------------------------------

EUVerifySignResultTR.prototype.stateMessage = function() {
	switch(this.state) {
		case EUVS_SIGN_STATE_CHECKED:
			return EUVS_SIGN_STATE_MSG_CHECKED;
		case EUVS_SIGN_STATE_CHECKING:
			return EUVS_SIGN_STATE_MSG_CHECKING;
		case EUVS_SIGN_STATE_CHECK_ERROR:
			return EUVS_SIGN_STATE_MSG_CHECK_ERROR;
		case EUVS_SIGN_STATE_FILE_NOT_FOUND:
		case EUVS_SIGN_STATE_NOT_CHECKED:
		case EUVS_SIGN_STATE_FILE_INVALID:
		case EUVS_SIGN_STATE_FILE_READ_ERROR:
		case EUVS_SIGN_STATE_FILE_TOO_BIG:
		default:
			return EUVS_SIGN_STATE_MSG_NOT_CHECKED;
	}
};

//-----------------------------------------------------------------------------

EUVerifySignResultTR.prototype.informationMessage = function() {
	switch(this.state) {
		case EUVS_SIGN_STATE_CHECK_ERROR:
			return this.error;
		case EUVS_SIGN_STATE_FILE_NOT_FOUND:
			return 'Не знайдено файл з даними для перевірки підпису';
		case EUVS_SIGN_STATE_FILE_INVALID:
			return 'Невірний тип файлу з підписом';
		case EUVS_SIGN_STATE_FILE_READ_ERROR:
			return 'Файл з підписом не зчитано';
		case EUVS_SIGN_STATE_FILE_TOO_BIG:
			return 'Завеликий розмір файлу (>' + 
				EUVS_MAX_FILE_SIZE_MB +  'МБ)';
		default:
			return '';
	}
}

//=============================================================================

function hashCode(str) {
	var hash = 0, i, chr, length;

	if (str.length == 0)
		return hash;

	for (i = 0, length = str.length; i < length; i++) {
		chr   = str.charCodeAt(i);
		hash  = ((hash << 5) - hash) + chr;
		hash |= 0;
	}

	return hash;
}

//-----------------------------------------------------------------------------

function dateToString(date) {
	var dateStr = 
		('0' + date.getDate()).slice(-2) + '.' + 
		('0' + (date.getMonth() + 1)).slice(-2) + '.' + 
		date.getFullYear();
	dateStr += ' ' + 
		('0' + date.getHours()).slice(-2) + ':' + 
		('0' + date.getMinutes()).slice(-2) + ':' + 
		('0' + date.getSeconds()).slice(-2);

	return dateStr;
}

//-----------------------------------------------------------------------------

function removeFileExtension(file) {
	var lastIndex = file.name.lastIndexOf('.');
	if (lastIndex <= 0)
		return file.name;

	return file.name.substr(0, lastIndex);
}

//-----------------------------------------------------------------------------

function readFile(file, onSuccess, onError) {
	if (file == null) {
		onError(euVerifySign.MakeError(EU_ERROR_BAD_PARAMETER));
		return;
	}

	function _onSuccess(evt) {
		if (evt.target.readyState != FileReader.DONE)
			return;

		try {
			var loadedFile = {
				'file': file,
				'data': new Uint8Array(evt.target.result)
			};

			onSuccess(loadedFile);
		} catch (e) {
			onError(euVerifySign.MakeError(EU_ERROR_JS_READ_FILE));
		}
	};

	function _onError(e) {
		onError(euVerifySign.MakeError(EU_ERROR_JS_READ_FILE));
	}

	var fileReader = new FileReader();
	fileReader.onloadend = _onSuccess;
	fileReader.onerror = _onError;
	fileReader.readAsArrayBuffer(file);
};

//-----------------------------------------------------------------------------

function saveFile(fileName, array) {
	try {
		var blob = new Blob([array], {type:"application/octet-stream"});
		saveAs(blob, fileName);
		return true;
	} catch (e) {
		return false;
	}
}

//=============================================================================

function addSaveButtonToRow(rowIndex, data) {
	var buttonId = 'button_' + data.id;
	var button = '<input type="button" value="Зберегти" id="' + buttonId + 
		'"style="width:100px"/>';

	updateCell(rowIndex, 
		EUVS_RESULT_TABLE_COLUMN_INDEX_FILE_WITH_DATA, button);

	$('#' + buttonId).click(function() {
		var _onError = function(e) {
			closeDimmerView();
			
			var msg = 'Виникла помилка при збереженні перевіреного файлу';
			if (e) {
				msg += '. Опис помилки:' + e.toString();
			}
			alert(msg);
		}

		var _saveFile = function(fileData) {
			var verifiedFile = removeFileExtension(data.signFile);
			if (!saveFile(verifiedFile, fileData)) {
				_onError();
				return;
			}

			closeDimmerView();
		};

		showDimmerView(
			'Збереження перевіреного файлу', 'Зачекайте будь ласка');
		if (data.internalSign) {
			euVerifySign.getDataFromSignedFile(
				data.signFile, _saveFile, _onError);
		} else {
			var _onFileRead = function (readedFile) {
				_saveFile(readedFile.data);
			};

			readFile(data.dataFile, _onFileRead, _onError);
		}

		return false;
	});
}

//-----------------------------------------------------------------------------

function addChooseDataFileButton(rowIndex, data) {
	var fileInputId = 'file_input_' + data.id;
	var buttonId = 'button_' + data.id;

	button = '<input type="file" style="display:none" ' + 
		'multiple="false" id="' + fileInputId + '" />';
	button += '<input type="button" value="Обрати" id="' + buttonId + 
		'"style="width:100px"/>';

	updateCell(rowIndex, 
		EUVS_RESULT_TABLE_COLUMN_INDEX_FILE_WITH_DATA, button);

	$('#' + buttonId).click(function(event) {
		$('#' + fileInputId).click();
		return false;
	});

	$('#' + fileInputId).click(function(event) {
		event.stopPropagation();
	});
	
	$('#' + fileInputId)
		.bind('change', function(evt) {
			var files = evt.target.files;
			if (files.length != 1)
				return false;

			if (!EUVS_VERIFY_LARGE_FILES && 
				(files[0].size > (EUVS_MAX_FILE_SIZE_MB * 1024 * 1024))) {
				alert("Занадто великий розмір файлу з данними. " + 
					"Оберіть файл меншого розміру (не більше " + 
					EUVS_MAX_FILE_SIZE_MB +  " МБ)");
				return;
			}

			data.dataFile = files[0];

			showDimmerView(
				'Перевірка підпису файлу', 'Зачекайте будь ласка');
			var _onVerifyFileEnd = function() {
				closeDimmerView();
			};

			verifyFile(rowIndex, data.dataFile, 
				data.signFile, _onVerifyFileEnd, _onVerifyFileEnd);
			return false;
	});
}

//-----------------------------------------------------------------------------

function makeRowData(data) {
	var row = [];

	row.push('<img src="Images/' + data.imageName() + 
		'" alt="" height="20" width="20">');
	row.push(data.signFile.name);
	row.push(data.stateMessage());

	if (data.info != null) {
		var info = data.info;
		row.push(
			'<nobr>Підписувач: ' + info.ownerInfo.subjCN + '<br></nobr>' + 
			'<nobr>ЦСК: ' + info.ownerInfo.issuerCN + '<br></nobr>' + 
			'<nobr>Серійний номер: ' + info.ownerInfo.serial) + '</nobr>';
	} else {
		row.push(data.informationMessage());
	}

	row.push('');
	row.push(data);

	return row;
}

//-----------------------------------------------------------------------------

function addRow(data) {
	var rowData = makeRowData(data);
	var row = $('#ResultsTable').DataTable().row.add(rowData);

	if (data.state == EUVS_SIGN_STATE_CHECKED) {
		addSaveButtonToRow(row.index(), data);
	} else if (data.state == EUVS_SIGN_STATE_FILE_NOT_FOUND) {
		addChooseDataFileButton(row.index(), data);
	}

	row.draw();
}

//-----------------------------------------------------------------------------

function updateCell(rowIndex, cellIndex, data) {
	$('#ResultsTable').dataTable().fnUpdate(data, rowIndex, cellIndex);
}

//-----------------------------------------------------------------------------

function updateRow(index, data) {
	var rowData = makeRowData(data);
	
	 $('#ResultsTable').dataTable().fnUpdate(rowData, index);

	if (data.state == EUVS_SIGN_STATE_CHECKED) {
		addSaveButtonToRow(index, data);
	} else if (data.state == EUVS_SIGN_STATE_FILE_NOT_FOUND) {
		addChooseDataFileButton(index, data);
	}
}

//-----------------------------------------------------------------------------

function clearTable() {
	$('#ResultsTable').DataTable().clear().draw();
}

//-----------------------------------------------------------------------------

function setColumnVisible(index, visible) {
	$('#ResultsTable').DataTable().column(index).visible(visible);
}

//=============================================================================

function showSignInfo(info, internalSign) {
	var message = '';

	var timeInfo = info.timeInfo;
	var ownerInfo = info.ownerInfo;

	var _appendField = function(name, value) {
		if (value != '')
			message += name + ': ' + value + '\n';
	};

	_appendField('Результат перевірки підпису', 'Підпис перевірено успішно');
	_appendField('Реквізити видавця', ownerInfo.issuer);
	_appendField('Ім\'я видавця', ownerInfo.issuerCN);
	_appendField('Серійний номер', ownerInfo.serial);
	_appendField('Реквізити власника', ownerInfo.subject);
	_appendField('Ім\'я власника', ownerInfo.subjCN);
	_appendField('Організація', ownerInfo.subjOrg);
	_appendField('Підрозділ', ownerInfo.subjOrgUnit);
	_appendField('Посада', ownerInfo.subjTitle);
	_appendField('Область', ownerInfo.subjState);
	_appendField('Місто', ownerInfo.subjLocality);
	_appendField('Повне ім\'я власника', ownerInfo.subjFullName);
	_appendField('Адреса', ownerInfo.subjAddress);
	_appendField('Телефон', ownerInfo.subjPhone);
	_appendField('Електронна пошта', ownerInfo.subjEMail);
	_appendField('Електронна адреса', ownerInfo.subjDNS);
	_appendField('Код ЄДРПОУ', ownerInfo.subjEDRPOUCode);
	_appendField('Код ДРФО', ownerInfo.subjDRFOCode);

	if (info.timeInfo.isTimeAvail) {
		message += (info.timeInfo.isTimeStamp ?
			'Мітка часу: ' : 'Час підпису: ') + 
				dateToString(info.timeInfo.time) + '\n';
	} else {
		message += 'Час підпису відсутній' + '\n';
	}

	if (internalSign) {
		message += 'Підпис містить дані';
	} else {
		message += 'Підпис не містить даних';
	}

	alert(message);
}

//-----------------------------------------------------------------------------

function onTableRowSelect(row) {
	rowData = row.data()[EUVS_RESULT_TABLE_COLUMN_INDEX_ROW_DATA];

	var message = 'Результат перевірки підпису:' + '\n';

	switch(rowData.state) {
		case EUVS_SIGN_STATE_CHECKED:
			showSignInfo(rowData.info, rowData.internalSign);
			return;
		
		case EUVS_SIGN_STATE_CHECKING:
			message += 'Перевіряється';
			break;
			
		case EUVS_SIGN_STATE_CHECK_ERROR:
			message += 'Виникла помилка при перевірці підпису. ' +
				'Опис помилки: ' + rowData.error;
			break;

		case EUVS_SIGN_STATE_FILE_NOT_FOUND:
			message += 'Не знайдено файл з даними для перевірки підпису. ' + 
				'Оберіть файл';
			break;

		case EUVS_SIGN_STATE_FILE_READ_ERROR:
		case EUVS_SIGN_STATE_FILE_TOO_BIG:
		case EUVS_SIGN_STATE_FILE_INVALID:
			message += 'Виникла помилка при зчитуванні файлу з підписом. ' + 
				'Опис помилки: ' + rowData.error;
			break;

		case EUVS_SIGN_STATE_NOT_CHECKED:
		default:
			message += 'Не перевірявся';
			break;
	}

	alert(message);
}

//=============================================================================

function setFilterSignFileResults(results) {
	for (var i = 0; i < results.length; i++) {
		var row;
	
		switch (results[i].resultCode) {
			case EUVS_FILTER_SIGN_FILE_RESULT_NO_ERROR:
				row = new EUVerifySignResultTR(
					results[i].dataFile, results[i].signFile,
					results[i].isInternal,
					EUVS_SIGN_STATE_NOT_CHECKED, null, "");
				break;
			case EUVS_FILTER_SIGN_FILE_RESULT_NO_FILE_WITH_DATA:
				row = new EUVerifySignResultTR(
					results[i].dataFile, results[i].signFile,
					results[i].isInternal,
					EUVS_SIGN_STATE_FILE_NOT_FOUND, null, "");
				break;
			case EUVS_FILTER_SIGN_FILE_RESULT_INVALID_FILE_FORMAT:
				row = new EUVerifySignResultTR(
					null, results[i].signFile, false,
					EUVS_SIGN_STATE_FILE_INVALID, null,
					"Файл має невірний формат");
				break;
			case EUVS_FILTER_SIGN_FILE_RESULT_FILE_TOO_BIG:
				row = new EUVerifySignResultTR(
					results[i].dataFile, results[i].signFile,
					results[i].isInternal,
					EUVS_SIGN_STATE_FILE_TOO_BIG, null,
					"Файл занадто великий" + " (>" + 
						EUVS_MAX_FILE_SIZE_MB +  " МБ)");
				break;
			case EUVS_FILTER_SIGN_FILE_RESULT_FILE_READ_ERROR:
				row = new EUVerifySignResultTR(
					null, results[i].signFile, false,
					EUVS_SIGN_STATE_FILE_READ_ERROR, null,
					"Файл відстуній або заборонено доступ до нього");
				break;
		}

		addRow(row);
	}
}

//=============================================================================

function verifyFile(rowIndex, dataFile, signFile, onSuccess, onFail) {
	var _onSuccess = function (signInfo) {
		var row = new EUVerifySignResultTR(
			dataFile, signFile, (dataFile == null),
			EUVS_SIGN_STATE_CHECKED, signInfo, "");
		updateRow(rowIndex, row);
		onSuccess();
	}

	var _onFail = function(result) {
		var row = new EUVerifySignResultTR(
			dataFile, signFile, (dataFile == null),
			EUVS_SIGN_STATE_CHECK_ERROR, null,
			result.message);
		updateRow(rowIndex, row);
		onFail();
	}

	updateCell(rowIndex, EUVS_RESULT_TABLE_COLUMN_INDEX_STATE,
		EUVS_SIGN_STATE_MSG_CHECKING);

	euVerifySign.verifyFile(dataFile, signFile, 
		_onSuccess, _onFail);
}

//-----------------------------------------------------------------------------

function verifyFiles(files) {
	clearTable();

	if (files.length <= 0)
		return;

	var _onSuccess = function(results) {
		setFilterSignFileResults(results);

		$('#FileDropZoneBorder').hide();
		$('#TableContainer').show();
		$('#BackButtonArea').show();
		$('#FilesDropZone').css('border', '0px');

		var curIndex = 0;

		var _verifyNextFile = function() {
			if (curIndex >= results.length) {
				closeDimmerView();
				stopSpinner();
				return;
			}
			
			if (results[curIndex].resultCode != 
					EUVS_FILTER_SIGN_FILE_RESULT_NO_ERROR) {
				curIndex++;
				_verifyNextFile();
				return;
			}

			verifyFile(curIndex, results[curIndex].dataFile,
				results[curIndex].signFile, 
				_verifyNextFile, _verifyNextFile);
			curIndex++;
		}

		_verifyNextFile();
	};

	var _onFail = function(results) {
		closeDimmerView();
		alert("Виникла помилка при перевірці файлів");
	};

	showDimmerView('Перевірка підпису файлів', 'Зачекайте будь ласка');
	euVerifySign.filterSignFiles(files, _onSuccess, _onFail);
}

//=============================================================================

function startSpinner() {
	$('#LoadingImage').show();
}

//-----------------------------------------------------------------------------

function stopSpinner() {
	$('#LoadingImage').hide();
}

//-----------------------------------------------------------------------------

function showDimmerView(title, msg) {
	startSpinner();
	$('#MainPageContent').block({
		message: '<h2 id="DimmerViewTitle" style="line-height:normal">' + 
					title + '</h2>' + 
				 '<span id="DimmerViewMessage" style="line-height:normal">' + 
					msg + '...</span>',
		css: {
			backgroundColor: 'rgba(0, 0, 0, 0)', 
			color: '#fff',
			border:'none',
			borderColor: '#000'
		}, 
		overlayCSS: {
			backgroundColor: '#0C234B'
		}
	}); 
}

//-----------------------------------------------------------------------------

function closeDimmerView() {
	$('#MainPageContent').unblock();
	stopSpinner();
}

//-----------------------------------------------------------------------------

function changeDimmerViewMessage(title, msg) {
	$('#DimmerViewTitle').html(title);
	$('#DimmerViewMessage').html(msg);
}

//=============================================================================

$(document).ready(function() {
	var table = $('#ResultsTable').DataTable({
			"paging": false,
			"ordering": false,
			"searching": false,
			"scrollY": "200px",
			"scrollX": true,
			//"scrollCollapse": true,
			"language": {
				"search": "Пошук:",
				"lengthMenu": "Відображати _MENU_ на сторінці",
				"zeroRecords": "Перетягніть файли для перевірки",
				"info": "", // "Сторінка _PAGE_ з _PAGES_",
				"infoEmpty": "", //"Записи відсутні",
				"infoFiltered": "(відфільтровано з _MAX_ записів)"
			},
			"columns": [
				{"width": "1px"},
				{"width": "120px"},
				{"width": "95px"},
				{"width": "250px"},
				{"width": "140px"}],
			"fnRowCallback": function(nRow, aData, ilInd, iIndFull) {
				var state = 
					aData[EUVS_RESULT_TABLE_COLUMN_INDEX_ROW_DATA].state;
				switch(state) {
					case EUVS_SIGN_STATE_CHECKING:
					case EUVS_SIGN_STATE_NOT_CHECKED:
						$('td', nRow).css(
							'background-color', 'rgba(4,39,81,0.1)');
						break;
					case EUVS_SIGN_STATE_CHECKED:
						$('td', nRow).css(
							'background-color', 'rgba(0,134,65,0.1)');
						break;
					case EUVS_SIGN_STATE_FILE_NOT_FOUND:
						$('td', nRow).css(
							'background-color', 'rgba(255,208,4,0.1)');
						break;
					case EUVS_SIGN_STATE_CHECK_ERROR:
					case EUVS_SIGN_STATE_FILE_INVALID:
					case EUVS_SIGN_STATE_FILE_READ_ERROR:
					case EUVS_SIGN_STATE_FILE_TOO_BIG:
					default:
						$('td', nRow).css(
							'background-color', 'rgba(192,39,34,0.1)');
					break;
				}
				$('td', nRow).css('line-height', '1.2');
			}
		});


	$('#ResultsTable td').css('overflow', 'hidden');
	
	$('#ResultsTable tbody').on('click', 'tr', function (e) {
		if ( $(this).hasClass('selected') ) {
			$(this).removeClass('selected');
		} else {
			table.$('tr.selected').removeClass('selected');
			$(this).addClass('selected');
			onTableRowSelect(table.row(this));
		}
	});

	$('#BackButton').on('click', function (e) {
		$('#FileDropZoneBorder').show();
		$('#TableContainer').hide();
		$('#BackButtonArea').hide();

		$('#ChooseFilesInput').val('');

		$('#FilesDropZone').css('border', '1px solid #0C234B');
		clearTable();
	});

	$('#FilesDropZone')
		.bind('dragover', function(evt) {
			evt.stopPropagation();
			evt.preventDefault();
			evt.originalEvent.dataTransfer.dropEffect = 'copy';
		})
		.bind('drop', function(evt) {
			evt.stopPropagation();
			evt.preventDefault();

			verifyFiles(
				evt.originalEvent.dataTransfer.files);
	});

	$('#ChooseFilesInput')
		.bind('change', function(evt) {
			verifyFiles(evt.target.files);
	});

	euVerifySign = new EUVerifySign();

	function _onSuccess() {
		closeDimmerView();
	};

	function _onError(e) {
		changeDimmerViewMessage('Не ініціалізовано', e.toString());
		stopSpinner();
	};

	showDimmerView('Ініціалізація', 'Зачекайте будь ласка');
	euVerifySign.initialize(_onSuccess, _onError);
});

//=============================================================================
