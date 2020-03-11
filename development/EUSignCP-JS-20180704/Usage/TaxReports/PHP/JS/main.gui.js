//================================================================================

var euSign;
var s_certificates = [];

//================================================================================

function reportError(errorMessage) {
	alert(errorMessage);
}

//--------------------------------------------------------------------------------

function saveFile(fileName, array) {
	try {
		var blob = new Blob([array], {type:"application/octet-stream"});
		saveAs(blob, fileName);
		return true;
	} catch (e) {
		return false;
	}
}

//================================================================================

function setFileItemsToList(listId, items) {
	var output = [];
	for (var i = 0, item; item = items[i]; i++) {
		output.push('<li><strong>', item.name, '</strong></li>');
	}

	document.getElementById(listId).innerHTML = 
		'<ul>' + output.join('') + '</ul>';
}

//--------------------------------------------------------------------------------

function mainMenuItemClicked(tab, pageId) {
	var selectedTab = document.getElementsByClassName(
		'MainPageMenuSelectedTab')[0];
	if (selectedTab == tab)
		return false;

	selectedTab.className = 'MainPageMenuTab';
	tab.className = 'MainPageMenuSelectedTab';
	tab.href = 'Tab';

	var selectedPage = document.getElementsByClassName(
		'MainPageMenuPanelSelected')[0];
	selectedPage.className = 'MainPageMenuPanel';

	selectedPage = document.getElementById(pageId);
	selectedPage.className = 'MainPageMenuPanelSelected';
	
	return false;
}

//--------------------------------------------------------------------------------

function appendCAServers() {
	var servers = euSign.getCAs();

	var select = document.getElementById("CAsServersSelect");
	for (var i = 0; i < servers.length; i++){
		var option = document.createElement("option");
		option.text = servers[i].issuerCN;
		select.add(option);
	}

	var option = document.createElement("option");
	option.text = "інший";
	select.add(option);

	select.onchange = function() {
		changeCAServer(select.selectedIndex);
	};
}

//--------------------------------------------------------------------------------

function changeCAServer(selectedIndex) {
	var servers = euSign.getCAs();
	if ((selectedIndex <  servers.length) && 
		!servers[selectedIndex].loadPKCertsFromFile) {
		document.getElementById('CertsSelectZone').hidden = 'hidden';
	} else {
		document.getElementById('CertsSelectZone').hidden = '';
	}
	
	clearCertificatesList();
}

//--------------------------------------------------------------------------------

function getSelectedCA() {
	var caServers = euSign.getCAs();
	var index = document.getElementById('CAsServersSelect').selectedIndex;
	if (index < caServers.length) {
		return caServers[index];
	}

	return null;
}

//--------------------------------------------------------------------------------

function usePKeyCheckboxClicked(checkbox) {
	var panelId;

	switch (checkbox.id) {
		case 'UseAccountantCheckbox':
			panelId = 'AccountantPKeyPanel';
		break;

		case 'UseDirectorCheckbox':
			panelId = 'DirectorPKeyPanel';
		break;
		
		case 'UseStampCheckbox':
			panelId = 'StampPKeyPanel';
		break;

		default:
			return;
	}

	document.getElementById(panelId).hidden = checkbox.checked ? '' : 'hidden';
}

//--------------------------------------------------------------------------------

function selectPKeyFile(pkInput, event) {
	var fileNameEditId;
	var passwordEditId;
	
	switch (pkInput.id) {
		case 'AccountantPKeyFileInput':
			fileNameEditId = 'AccountantPKeyFileName';
			passwordEditId = 'AccountantPKeyPassword';
		break;

		case 'DirectorPKeyFileInput':
			fileNameEditId = 'DirectorPKeyFileName';
			passwordEditId = 'DirectorPKeyPassword';
		break;

		case 'StampPKeyFileInput':
			fileNameEditId = 'StampPKeyFileName';
			passwordEditId = 'StampPKeyPassword';
		break;

		case 'UnportectPKeyFileInput':
			fileNameEditId = 'UnportectPKeyFileName';
			passwordEditId = 'UnportectPKeyPassword';
		break;
		
		default:
			return;
	}

	var enable = (event.target.files.length == 1);
	document.getElementById(fileNameEditId).value = 
		enable ? event.target.files[0].name : '';
	document.getElementById(passwordEditId).disabled = 
		enable ? '' : 'disabled';
	document.getElementById(passwordEditId).value = '';
}

//--------------------------------------------------------------------------------

function selectRecipientCertFile(input, event) {
	var enable = (event.target.files.length == 1);
	document.getElementById('RecipientCertFileName').value = 
		enable ? event.target.files[0].name : '';
}

//--------------------------------------------------------------------------------

function clearCertificatesList() {
	s_certificates = null;
	document.getElementById('ChooseCertsInput').value = null;
	document.getElementById('SelectedCertsList').innerHTML = 
		"Сертифікати не обрано" + '<br>';
}

//--------------------------------------------------------------------------------

function setSelectCertificatesEvents() {
	document.getElementById('ChooseCertsInput').addEventListener(
		'change',  function(evt) {
			if (evt.target.files.length <= 0) {
				clearCertificatesList();
			} else {
				s_certificates = evt.target.files;
				setFileItemsToList("SelectedCertsList", 
					evt.target.files);
			}
		}, false);
	
	document.getElementById('CertsDropZone').addEventListener(
		'dragover', function(evt) {
			evt.stopPropagation();
			evt.preventDefault();
			evt.dataTransfer.dropEffect = 'copy';
		}, false);

	document.getElementById('CertsDropZone').addEventListener(
		'drop', function(evt) {
			evt.stopPropagation();
			evt.preventDefault();

			if (evt.dataTransfer.files.length <= 0) {
				clearCertificatesList();
			} else {
				s_certificates = evt.dataTransfer.files;
				setFileItemsToList("SelectedCertsList", 
					evt.dataTransfer.files);
			}
		}, false);
}

//--------------------------------------------------------------------------------

function selectReportFile(input, event) {
	var enable = (event.target.files.length == 1);
	document.getElementById('ReportFileName').value = 
		enable ? event.target.files[0].name : '';
	document.getElementById('ProtectedReportFileName').value = 
		enable ? event.target.files[0].name + '.prt' : '';
}

//--------------------------------------------------------------------------------

function selectReceiptFile(input, event) {
	var enable = (event.target.files.length == 1);
	document.getElementById('ReceiptFileName').value = 
		enable ? event.target.files[0].name : '';
	document.getElementById('UnprotectedReceiptFileName').value = 
		enable ? event.target.files[0].name + '.new' : '';
}

//--------------------------------------------------------------------------------

function setProtectReportKeys(onSuccess, onError) {
	var _onError = function(msg) {
		mainMenuItemClicked(
			document.getElementById('MainPageMenuPKeys'),
			'MainPageMenuPKeysPage');
		onError(msg);
	}

	if (!document.getElementById('UseAccountantCheckbox').checked && 
		!document.getElementById('UseDirectorCheckbox').checked && 
		!document.getElementById('UseStampCheckbox').checked) {
		_onError("Ключові дані не обрано");
		return;
	}

	var keys = {
		accountant: null,
		director: null,
		stampKey: null
	};

	if (document.getElementById('UseAccountantCheckbox').checked) {
		if (document.getElementById('AccountantPKeyFileInput').files.length != 1){
			_onError("Файл з ключем бухгалтера не обрано");
			document.getElementById('AccountantPKeyFileName').focus();
			return;
		}

		if (document.getElementById('AccountantPKeyPassword').value == ''){
			_onError("Пароль до файлу з ключем бухгалтера не вказано");
			document.getElementById('AccountantPKeyPassword').focus();
			return;
		}

		keys.accountant = {
			file: document.getElementById('AccountantPKeyFileInput').files[0],
			password: document.getElementById('AccountantPKeyPassword').value
		};
	}

	if (document.getElementById('UseDirectorCheckbox').checked) {
		if (document.getElementById('DirectorPKeyFileInput').files.length != 1){
			_onError("Файл з ключем директора не обрано");
			document.getElementById('DirectorPKeyFileName').focus();
			return;
		}

		if (document.getElementById('DirectorPKeyPassword').value == ''){
			_onError("Пароль до файлу з ключем директора не вказано");
			document.getElementById('DirectorPKeyPassword').focus();
			return;
		}

		keys.director = {
			file: document.getElementById('DirectorPKeyFileInput').files[0],
			password: document.getElementById('DirectorPKeyPassword').value
		};
	}

	if (document.getElementById('UseStampCheckbox').checked) {
		if (document.getElementById('StampPKeyFileInput').files.length != 1){
			_onError("Файл з ключем печатки не обрано");
			document.getElementById('StampPKeyFileName').focus();
			return;
		}

		if (document.getElementById('StampPKeyPassword').value == ''){
			_onError("Пароль до файлу з ключем печатки не вказано");
			document.getElementById('StampPKeyPassword').focus();
			return;
		}

		keys.stamp = {
			file: document.getElementById('StampPKeyFileInput').files[0],
			password: document.getElementById('StampPKeyPassword').value
		};
	}

	var useCerts = (s_certificates != null && 
		s_certificates.length != 0)

	eu_wait(function(runNext) {
		var ca = getSelectedCA();
		
		euSign.setCA(ca, runNext, function(e) {
			onError(
				"Виникла помилка при встановленні параметрів ЦСК. " + 
				e.toString());
		});
	}).eu_wait(function(runNext) {
		if (keys.accountant == null) {
			setTimeout(function() {
				runNext(null);
			}, 1);
			return;
		}
		
		euSign.setReportKeyFile(EU_KEY_ID_ACCOUNTANT,
			keys.accountant.file, keys.accountant.password,
			(useCerts ? s_certificates : null), 
			runNext, function(e) {
				onError(
					"Виникла помилка при встановленні " + 
					"особистого ключа бухгалтера. " + 
					e.toString());
			});
	}).eu_wait(function(runNext, ownerInfo) {
		if (keys.director == null) {
			setTimeout(function() {
				runNext(null);
			}, 1);
			return;
		}

		var passCerts = useCerts && 
			(keys.accountant == null);

		euSign.setReportKeyFile(EU_KEY_ID_DIRECTOR,
			keys.director.file, keys.director.password,
			(passCerts ? s_certificates : null),
			runNext, function(e) {
				onError(
					"Виникла помилка при встановленні " + 
					"особистого ключа директора. " + 
					e.toString());
			});
	}).eu_wait(function(runNext, ownerInfo) {
		if (keys.stamp == null) {
			setTimeout(function() {
				runNext(null);
			}, 1);
			return;
		}

		var passCerts = useCerts && 
			(keys.accountant == null) && 
			(keys.director == null);

		euSign.setReportKeyFile(EU_KEY_ID_STAMP,
			keys.stamp.file, keys.stamp.password,
			(passCerts ? s_certificates : null), 
			runNext, function(e) {
				onError(
					"Виникла помилка при встановленні " + 
					"особистого ключа печатки. " + 
					e.toString());
			});
	}).eu_wait(function(runNext, ownerInfo) {
		onSuccess();
	});
}

//--------------------------------------------------------------------------------

function setUnprotectReceiptKey(onSuccess, onError) {
	if (!document.getElementById('UseDirectorCheckbox').checked && 
		!document.getElementById('UseStampCheckbox').checked) {
		mainMenuItemClicked(
			document.getElementById('MainPageMenuPKeys'),
			'MainPageMenuPKeysPage');

		onError("Не встановлено ключ для відкриття квитанцій" + 
			"Встановіть особистий ключ директора або печатки");
		return;
	}

	var _onError = function(msg) {
		mainMenuItemClicked(
			document.getElementById('MainPageMenuPKeys'),
			'MainPageMenuPKeysPage');
		onError(msg);
	}
	
	var key;

	if (document.getElementById('UseDirectorCheckbox').checked) {
		if (document.getElementById('DirectorPKeyFileInput').files.length != 1){
			_onError("Файл з ключем директора не обрано");
			document.getElementById('DirectorPKeyFileName').focus();
			return;
		}

		if (document.getElementById('DirectorPKeyPassword').value == ''){
			_onError("Пароль до файлу з ключем директора не вказано");
			document.getElementById('DirectorPKeyPassword').focus();
			return;
		}

		key = {
			id: EU_KEY_ID_DIRECTOR,
			file: document.getElementById('DirectorPKeyFileInput').files[0],
			password: document.getElementById('DirectorPKeyPassword').value
		};
	} else {
		if (document.getElementById('StampPKeyFileInput').files.length != 1){
			_onError("Файл з ключем печатки не обрано");
			document.getElementById('StampPKeyFileName').focus();
			return;
		}

		if (document.getElementById('StampPKeyPassword').value == ''){
			_onError("Пароль до файлу з ключем печатки не вказано");
			document.getElementById('StampPKeyPassword').focus();
			return;
		}

		key = {
			id: EU_KEY_ID_STAMP,
			file: document.getElementById('StampPKeyFileInput').files[0],
			password: document.getElementById('StampPKeyPassword').value
		};
	}

	var useCerts = (s_certificates != null && 
		s_certificates.length != 0)

	eu_wait(function(runNext) {
		var ca = getSelectedCA();
		
		euSign.setCA(ca, runNext, function(e) {
			onError(
				"Виникла помилка при встановленні параметрів ЦСК. " + 
				e.toString());
		});
	}).eu_wait(function(runNext) {
		euSign.setReportKeyFile(
			key.id, key.file, key.password,
			(useCerts ? s_certificates : null), 
			runNext, function(e) {
				onError(
					"Виникла помилка при встановленні " + 
					"особистого ключа відкриття квитанцій. " + 
					e.toString());
			});
	}).eu_wait(function(runNext, ownerInfo) {
		onSuccess(key.id);
	});
}

//--------------------------------------------------------------------------------

function getReport(useFile) {
	if (document.getElementById("RecipientCertFileInput").files.length != 1) {
		document.getElementById("RecipientCertFileName").focus();
		reportError("Сертифікат одержувача не вказано");
		return null;
	}

	var senderEMail = document.getElementById("SenderEMailTextEdit").value;
	var recipientCertFile = 
		document.getElementById("RecipientCertFileInput").files[0];
	
	if (useFile) {
		if (document.getElementById("ReportFileInput").files.length != 1) {
			document.getElementById("ReportFileName").focus();
			reportError("Файл зі звітом для захисту не вказано");
			return;
		}

		if (document.getElementById("ProtectedReportFileName").value == '') {
			document.getElementById("ProtectedReportFileName").focus();
			reportError("Ім'я файлу з захищеним звітом не вказано");
			return;
		}

		var reportFile = document.getElementById("ReportFileInput").files[0];
		if (!EUVS_VERIFY_LARGE_FILES && 
			(reportFile.size > (EUVS_MAX_FILE_SIZE_MB * 1024 * 1024))) {
			document.getElementById("ReportFileName").focus();
			reportError("Занадто великий розмір файлу з звітом. " + 
				"Оберіть файл меншого розміру (не більше " + 
				EUVS_MAX_FILE_SIZE_MB +  " МБ)");
			return;
		}
		
		return new EUVSReportFile(
			reportFile, senderEMail, recipientCertFile,
			document.getElementById("ProtectedReportFileName").value);
	} else {
		if (document.getElementById("ReportNameTextEdit").value == '') {
			document.getElementById("ReportNameTextEdit").focus();
			reportError("Назву звіту не вказано");
			return null;
		}

		return new EUVSReportData(
			document.getElementById('ReportDataText').value,
			document.getElementById("ReportNameTextEdit").value,
			senderEMail, recipientCertFile);
	}
}

//--------------------------------------------------------------------------------

function getReceipt(useFile) {
	if (useFile) {
		if (document.getElementById("ReceiptFileInput").files.length != 1) {
			document.getElementById("ReceiptFileName").focus();
			reportError("Файл з квитанцією не вказано");
			return;
		}

		if (document.getElementById("UnprotectedReceiptFileName").value == '') {
			document.getElementById("UnprotectedReceiptFileName").focus();
			reportError("Ім'я файлу з відкритою квитанцією не вказано");
			return;
		}

		var receiptFile = document.getElementById("ReceiptFileInput").files[0];
		if (!EUVS_VERIFY_LARGE_FILES && 
			(receiptFile.size > (EUVS_MAX_FILE_SIZE_MB * 1024 * 1024))) {
			document.getElementById("ReceiptFileName").focus();
			reportError("Занадто великий розмір файлу з квитанцією. " + 
				"Оберіть файл меншого розміру (не більше " + 
				EUVS_MAX_FILE_SIZE_MB +  " МБ)");
			return;
		}
		
		return new EUVSReceiptFile(receiptFile,
			document.getElementById("UnprotectedReceiptFileName").value);
	} else {
			var data = document.getElementById('ReceiptDataText').value;
			if (data == '') {
				document.getElementById('ReceiptDataText').focus();
				reportError("Дані квитанції не вказано");
				return null;
			}

		var data = euSign.base64Decode(
			document.getElementById('ReceiptDataText').value);
			
		return new EUVSReceiptData(data);
	}
}

//--------------------------------------------------------------------------------

function protectReportData() {
	var _onError = function(errorMsg) {
		reportError(errorMsg);
	}

	eu_wait(function(runNext, ownerInfo) {
		setProtectReportKeys(runNext, _onError);
	}).eu_wait(function(runNext) {
		var report = getReport(false);
		if (report == null)
			return;
		
		euSign.protectReports([report] ,runNext, function(e) {
			_onError("Виникла помилка при захисті звіту. " + 
				e.toString());
		});
	}).eu_wait(function(runNext, results) {
		var report = results[0];
		if (!report.isSuccess) {
			_onError("Виникла помилка при захисті звіту " + 
				report.inputFileName + ". " + 
				report.statusDescription);
			return;
		}

		document.getElementById('ProtectedReportDataText').value = 
			euSign.base64Encode(report.outputData);
	});
}

//--------------------------------------------------------------------------------

function protectReportFile() {
	var _onError = function(errorMsg) {
		reportError(errorMsg);
	}

	eu_wait(function(runNext, ownerInfo) {
		setProtectReportKeys(runNext, _onError);
	}).eu_wait(function(runNext) {
		var report = getReport(true);
		if (report == null)
			return;
		
		euSign.protectReports([report] ,runNext, function(e) {
			_onError("Виникла помилка при захисті файлу зі звітом. " + 
				e.toString());
		});
	}).eu_wait(function(runNext, results) {
		var report = results[0];
		if (!report.isSuccess) {
			_onError("Виникла помилка при захисті файлу зі звітом " + 
				report.inputFileName + ". " + 
				report.statusDescription);
			return;
		}

		saveFile(report.outputFileName, report.outputData);
	});
}

//--------------------------------------------------------------------------------

function showReceiptInfo(receipt) {
	var info = 'Квитанція № ' + receipt.receiptNumber + '\n';

	info += 'Інформація про відправників :\n';
	var initiators = receipt.initiators;
	for (var i = 0; i < initiators.length; i++) {
		var isSigner = initiators[i].ClassName == 'EndUserSignInfo';
		var ownerInfo = initiators[i].GetOwnerInfo();
		
		info += (i+1) + '. ' + (isSigner ? 'Підписант:': 'Відправник:') + '\n';
		info += '    Ім\'я: ' + ownerInfo.GetSubjCN() + '\n';
		info += '    ЦСК: ' + ownerInfo.GetIssuerCN() + '\n';
		info += '    S\N: ' + ownerInfo.GetSerial() + '\n';
		info += '\n'
	}

	alert(info);
}

//--------------------------------------------------------------------------------

function unprotectReceiptData() {
	var _onError = function(errorMsg) {
		reportError(errorMsg);
	}

	eu_wait(function(runNext, ownerInfo) {
		setUnprotectReceiptKey(runNext, _onError);
	}).eu_wait(function(runNext, keyId) {
		var receipt = getReceipt(false);
		if (receipt == null)
			return;
		
		euSign.unprotectReceipts(keyId, [receipt] ,runNext, function(e) {
			_onError("Виникла помилка при відкритті квитанції. " + 
				e.toString());
		});
	}).eu_wait(function(runNext, results) {
		var receipt = results[0];
		if (!receipt.isSuccess) {
			_onError("Виникла помилка при відкритті квитанції " + 
				receipt.inputFileName + ". " + 
				receipt.statusDescription);
			return;
		}

		showReceiptInfo(receipt);
		document.getElementById('UnprotectedReceiptDataText').value = 
			euSign.base64Encode(receipt.outputData);
	});
}

//--------------------------------------------------------------------------------

function unprotectReceiptFile() {
	var _onError = function(errorMsg) {
		reportError(errorMsg);
	}

	eu_wait(function(runNext, ownerInfo) {
		setUnprotectReceiptKey(runNext, _onError);
	}).eu_wait(function(runNext, keyId) {
		var receipt = getReceipt(true);
		if (receipt == null)
			return;
		
		euSign.unprotectReceipts(keyId, [receipt] ,runNext, function(e) {
			_onError("Виникла помилка при відкритті файлу з квитанцією. " + 
				e.toString());
		});
	}).eu_wait(function(runNext, results) {
		var receipt = results[0];
		if (!receipt.isSuccess) {
			_onError("Виникла помилка при захисті файлу з квитанцією " + 
				receipt.inputFileName + ". " + 
				receipt.statusDescription);
			return;
		}

		showReceiptInfo(receipt);
		saveFile(receipt.outputFileName, receipt.outputData);
	});
}

//--------------------------------------------------------------------------------

function setStatus(message) {
	if (message != '')
		message = '(' + message + '...)';
	document.getElementById('status').innerHTML = message;
}

//--------------------------------------------------------------------------------

function pageLoaded() {
	setStatus('Ініціалізація');

	setSelectCertificatesEvents();

	euSign = new EUSign();

	function _onSuccess() {
		setStatus('');
		appendCAServers();
	};

	function _onError(e) {
		document.getElementById('status').innerHTML = 
			'Не ініціалізовано';
			alert(e.toString());
	};

	euSign.initialize(_onSuccess, _onError);
}

//================================================================================