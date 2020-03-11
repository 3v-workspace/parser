//=============================================================================

var URL_EMAIL_PARAM = "@EMAIL_PARAM";
var URL_GET_KEP_CERTIFICATE_BY_EMAIL = "http://ca.iit.com.ua/services-cmp-getcert?eUserEMail=" + 
		URL_EMAIL_PARAM + "&certType=2&respType=2";

var URL_GET_CERTIFICATES = "/Data/CACertificates.p7b?version=1.0.18";
var URL_CAS = "/Data/CAs.json?version=1.0.18";
var URL_XML_HTTP_PROXY_SERVICE = "/Server/ProxyHandler.php";

//=============================================================================

var SubjectCertTypes = [
	{"type": EU_SUBJECT_TYPE_UNDIFFERENCED, "subtype": EU_SUBJECT_CA_SERVER_SUB_TYPE_UNDIFFERENCED},
	{"type": EU_SUBJECT_TYPE_CA, "subtype": EU_SUBJECT_CA_SERVER_SUB_TYPE_UNDIFFERENCED},
	{"type": EU_SUBJECT_TYPE_CA_SERVER, "subtype": EU_SUBJECT_CA_SERVER_SUB_TYPE_UNDIFFERENCED},
	{"type": EU_SUBJECT_TYPE_CA_SERVER, "subtype": EU_SUBJECT_CA_SERVER_SUB_TYPE_CMP},
	{"type": EU_SUBJECT_TYPE_CA_SERVER, "subtype": EU_SUBJECT_CA_SERVER_SUB_TYPE_OCSP},
	{"type": EU_SUBJECT_TYPE_CA_SERVER, "subtype": EU_SUBJECT_CA_SERVER_SUB_TYPE_TSP},
	{"type": EU_SUBJECT_TYPE_END_USER, "subtype": EU_SUBJECT_CA_SERVER_SUB_TYPE_UNDIFFERENCED},
	{"type": EU_SUBJECT_TYPE_RA_ADMINISTRATOR, "subtype": EU_SUBJECT_CA_SERVER_SUB_TYPE_UNDIFFERENCED}
];

var CertKeyTypes = [
	EU_CERT_KEY_TYPE_UNKNOWN,
	EU_CERT_KEY_TYPE_DSTU4145,
	EU_CERT_KEY_TYPE_RSA
];

var KeyUsages = [
	EU_KEY_USAGE_UNKNOWN,
	EU_KEY_USAGE_DIGITAL_SIGNATURE,
	EU_KEY_USAGE_KEY_AGREEMENT
];

var CAdESTypes = [
	EU_SIGN_TYPE_CADES_BES,
	EU_SIGN_TYPE_CADES_T,
	EU_SIGN_TYPE_CADES_C,
	EU_SIGN_TYPE_CADES_X_LONG
];

//=============================================================================

var EUSignCPTest = NewClass({
	"Vendor": "JSC IIT",
	"ClassVersion": "1.0.0",
	"ClassName": "EUSignCPTest",
	"CertsLocalStorageName": "Certificates",
	"CRLsLocalStorageName" : "CRLs",
	"recepientsCertsIssuers" : null,
	"recepientsCertsSerials" : null,
	"PrivateKeyNameSessionStorageName": "PrivateKeyName",
	"PrivateKeySessionStorageName": "PrivateKey",
	"PrivateKeyPasswordSessionStorageName": "PrivateKeyPassword",
	"PrivateKeyCertificatesSessionStorageName": "PrivateKeyCertificates",
	"PrivateKeyCertificatesChainSessionStorageName": "PrivateKeyCertificatesChain",
	"CACertificatesSessionStorageName" : "CACertificates",
	"CAServerIndexSessionStorageName": "CAServerIndex",
	"CAsServers": null,
	"CAServer": null,
	"offline": false,
	"useCMP": false,
	"loadPKCertsFromFile": false,
	"privateKeyCerts": null
},
function() {
},
{
	initialize: function() {
		setStatus('ініціалізація');

		var _onSuccess = function() {
			try {
				euSign.Initialize();
				euSign.SetJavaStringCompliant(true);
				euSign.SetCharset("UTF-16LE");

				if (euSign.DoesNeedSetSettings()) {
					euSignTest.setDefaultSettings();

					if (utils.IsStorageSupported()) {
						euSignTest.loadCertsAndCRLsFromLocalStorage();
					} else {
						document.getElementById(
							'SelectedCertsList').innerHTML = 
								"Локальне сховище не підтримується";
						document.getElementById(
							'SelectedCRLsList').innerHTML = 
								"Локальне сховище не підтримується";
					}
				}

				euSignTest.loadCertsFromServer();
				euSignTest.setCASettings(0);

				setPointerEvents(
					document.getElementById('PGenKeyButton'), true);
				setPointerEvents(
					document.getElementById('VerifyDataButton'), true);

				euSignTest.setSelectPKCertificatesEvents();

				if (utils.IsSessionStorageSupported()) {
					var _readPrivateKeyAsStoredFile = function() {
						euSignTest.readPrivateKeyAsStoredFile();
					}
					setTimeout(_readPrivateKeyAsStoredFile, 10);
				}

				euSignTest.updateCertList();
				
				setStatus('');
			} catch (e) {
				setStatus('не ініціалізовано');
				alert(e);
			}
		};

		var _onError = function() {
			setStatus('Не ініціалізовано');
			alert('Виникла помилка ' + 
				'при завантаженні криптографічної бібліотеки');
		};

		euSignTest.loadCAsSettings(_onSuccess, _onError);
	},
	loadCAsSettings: function(onSuccess, onError) {
		var pThis = this;

		var _onSuccess = function(casResponse) {
			try {
				var servers = JSON.parse(casResponse.replace(/\\'/g, "'"));

				var select = document.getElementById("CAsServersSelect");
				for (var i = 0; i < servers.length; i++){
					var option = document.createElement("option");
					option.text = servers[i].issuerCNs[0];
					select.add(option);
				}

				var option = document.createElement("option");
				option.text = "інший";
				select.add(option);

				select.onchange = function() {
					pThis.setCASettings(select.selectedIndex);
				};

				pThis.CAsServers = servers;

				onSuccess();
			} catch (e) {
				onError();
			}
		};

		euSign.LoadDataFromServer(URL_CAS, _onSuccess, onError, false);
	},
	loadCertsAndCRLsFromLocalStorage: function() {
		try {
			var files = euSignTest.loadFilesFromLocalStorage(
				euSignTest.CertsLocalStorageName, 
				function(fileName, fileData) {
						if (fileName.indexOf(".cer") >= 0)
							euSign.SaveCertificate(fileData);
						else if (fileName.indexOf(".p7b") >= 0)
							euSign.SaveCertificates(fileData);
					});
			if (files != null && files.length > 0)
				euSignTest.setItemsToList('SelectedCertsList', files);
			else {
				document.getElementById('SelectedCertsList').innerHTML = 
					"Сертифікати відсутні в локальному сховищі";
			}
		} catch (e) {
			document.getElementById('SelectedCertsList').innerHTML = 
				"Виникла помилка при завантаженні сертифікатів " + 
				"з локального сховища";
		}
		
		try {
			var files = euSignTest.loadFilesFromLocalStorage(
				euSignTest.CRLsLocalStorageName, 
				function(fileName, fileData) {
						if (fileName.indexOf(".crl") >= 0) {
							try {
								euSign.SaveCRL(true, fileData);
							} catch (e) {
								euSign.SaveCRL(false, fileData);
							}
						}
					});
			if (files != null && files.length > 0)
				euSignTest.setItemsToList('SelectedCRLsList', files);
			else {
				document.getElementById('SelectedCRLsList').innerHTML = 
					"СВС відсутні в локальному сховищі";
			}
		} catch (e) {
			document.getElementById('SelectedCRLsList').innerHTML = 
				"Виникла помилка при завантаженні СВС з локального сховища";
		}
	},
	loadCertsFromServer: function() {
		var certificates = utils.GetSessionStorageItem(
			euSignTest.CACertificatesSessionStorageName, true, false);
		if (certificates != null) {
			try {
				euSign.SaveCertificates(certificates);
				euSignTest.updateCertList();
				return;
			} catch (e) {
				alert("Виникла помилка при імпорті " + 
					"завантажених з сервера сертифікатів " + 
					"до файлового сховища");
			}
		}

		var _onSuccess = function(certificates) {
			try {
				euSign.SaveCertificates(certificates);
				utils.SetSessionStorageItem(
					euSignTest.CACertificatesSessionStorageName,
					certificates, false);
				euSignTest.updateCertList();
			} catch (e) {
				alert("Виникла помилка при імпорті " + 
					"завантажених з сервера сертифікатів " + 
					"до файлового сховища");
			}
		};

		var _onFail = function(errorCode) {
			console.log("Виникла помилка при завантаженні сертифікатів з сервера. " + 
				"(HTTP статус " + errorCode + ")");
		};

		utils.GetDataFromServerAsync(URL_GET_CERTIFICATES, _onSuccess, _onFail, true);
	},
	setDefaultSettings: function() {
		try {
			euSign.SetXMLHTTPProxyService(URL_XML_HTTP_PROXY_SERVICE);

			var settings = euSign.CreateFileStoreSettings();
			settings.SetPath("/certificates");
			settings.SetSaveLoadedCerts(true);
			euSign.SetFileStoreSettings(settings);

			settings = euSign.CreateProxySettings();
			euSign.SetProxySettings(settings);
			
			settings = euSign.CreateTSPSettings();
			euSign.SetTSPSettings(settings);

			settings = euSign.CreateOCSPSettings();
			euSign.SetOCSPSettings(settings);

			settings = euSign.CreateCMPSettings();
			euSign.SetCMPSettings(settings);

			settings = euSign.CreateLDAPSettings();
			euSign.SetLDAPSettings(settings);
			
			settings = euSign.CreateOCSPAccessInfoModeSettings();
			settings.SetEnabled(true);
			euSign.SetOCSPAccessInfoModeSettings(settings);

			var CAs = this.CAsServers;
			settings = euSign.CreateOCSPAccessInfoSettings();
			for (var i = 0; i < CAs.length; i++) {
				settings.SetAddress(CAs[i].ocspAccessPointAddress);
				settings.SetPort(CAs[i].ocspAccessPointPort);

				for (var j = 0; j < CAs[i].issuerCNs.length; j++) {
					settings.SetIssuerCN(CAs[i].issuerCNs[j]);
					euSign.SetOCSPAccessInfoSettings(settings);
				}
			}
		} catch (e) {
			alert("Виникла помилка при встановленні налашувань: " + e);
		}
	},
	setCASettings: function(caIndex) {
		try {
			var caServer = (caIndex < this.CAsServers.length) ? 
				this.CAsServers[caIndex] : null;
			var offline = ((caServer == null) || 
				(caServer.address == "")) ?
				true : false;
			var useCMP = (!offline && (caServer.cmpAddress != ""));
			var loadPKCertsFromFile = (caServer == null) || 
				(!useCMP && !caServer.certsInKey);

			euSignTest.CAServer = caServer;
			euSignTest.offline = offline;
			euSignTest.useCMP = useCMP;
			euSignTest.loadPKCertsFromFile = loadPKCertsFromFile;

			document.getElementById('ChoosePKFileText').innerHTML = 
				"Оберіть файл з особистим ключем " + 
				"(зазвичай з ім'ям Key-6.dat) та вкажіть пароль захисту";
			if (loadPKCertsFromFile) {
				document.getElementById('ChoosePKFileText').innerHTML +=
					", а також оберіть сертифікат(и)";
			}

			var settings;

			document.getElementById('PKCertsSelectZone').hidden = 
				loadPKCertsFromFile ? '' : 'hidden';
			euSignTest.clearPrivateKeyCertificatesList();
			
			settings = euSign.CreateTSPSettings();
			if (!offline) {
				settings.SetGetStamps(true);
				if (caServer.tspAddress != "") {
					settings.SetAddress(caServer.tspAddress);
					settings.SetPort(caServer.tspAddressPort);
				} else {
					settings.SetAddress('acskidd.gov.ua');
					settings.SetPort('80');
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
				settings.SetPort("80");
			}
			euSign.SetCMPSettings(settings);

			settings = euSign.CreateLDAPSettings();
			euSign.SetLDAPSettings(settings);
		} catch (e) {
			alert("Виникла помилка при встановленні налашувань: " + e);
		}
	},
//-----------------------------------------------------------------------------
	chooseCertsAndCRLs: function(event) {
		var files = event.target.files;
		var certsFiles = [];
		var crlsFiles = [];

		if (utils.IsStorageSupported()) {
			utils.ClearFolder(euSignTest.CertsLocalStorageName);
			utils.ClearFolder(euSignTest.CRLsLocalStorageName);
		}

		for (var i = 0, file; file = files[i]; i++) {
			if (euSignTest.isCertificateExtension(file.name))
				certsFiles.push(file);
			else if (euSignTest.isCRLExtension(file.name))
				crlsFiles.push(file);
			else
				continue;

			var fileReader = new FileReader();
			fileReader.onloadend  = (function(fileName) {
				return function(evt) {
					if (evt.target.readyState == FileReader.DONE) {
						euSignTest.saveFileToModuleFileStorage(fileName, 
							evt.target.result);
					}
				};
			})(file.name);

			fileReader.readAsArrayBuffer(file);
		}
		
		if (certsFiles.length > 0) {
			euSignTest.setFileItemsToList('SelectedCertsList', certsFiles);
		} else {
			document.getElementById('SelectedCertsList').innerHTML = 
				"Не обрано жодного сертифіката";
		}

		if (crlsFiles.length > 0) {
			euSignTest.setFileItemsToList('SelectedCRLsList', crlsFiles);
		} else {
			document.getElementById('SelectedCRLsList').innerHTML = 
				"Не обрано жодного СВС";
		}
	},
	updateCertList: function() {
		var certSubjType = SubjectCertTypes[
			document.getElementById('CertTypeSelect').selectedIndex];
		var certKeyType = CertKeyTypes[
			document.getElementById('CertKeyTypeSelect').selectedIndex];
		var keyUsage = KeyUsages[
			document.getElementById('KeyUsageSelect').selectedIndex];

		try {
			var index = 0;
			var cert;
			var certs = [];

			while (true) {
				cert = euSign.EnumCertificatesEx(
					certSubjType.type, certSubjType.subtype,
					certKeyType, keyUsage, index);
				if (cert == null)
					break;
				
				certs.push(cert);
				index++;
			};
			
			if (certs.length == 0) {
				document.getElementById('StorageCertList').innerHTML = 
					"Сертифікати відсутні";
				return;
			}
			
			var _makeCertField = function(name, value, addNewLine) {
				return name + ': ' + 
					value  + 
					(addNewLine ? '<br>' : '');
			}
			
			var certInfos = [];

			for (var i = 0; i < certs.length; i++) {
				var certInfoStr = '';
				var certInfo = certs[i].GetInfoEx();
				var publicKeyType = '';
				switch (certInfo.GetPublicKeyType()) {
					case EU_CERT_KEY_TYPE_DSTU4145:
						publicKeyType += 'ДСТУ-4145';
						break;
					case EU_CERT_KEY_TYPE_RSA:
						publicKeyType += 'RSA';
						break;
					default:
						publicKeyType = 'Невизначено';
						break;
				}
				
				certInfoStr += _makeCertField('Власник', certInfo.GetSubjCN(), true);
				certInfoStr += _makeCertField('ЦСК', certInfo.GetIssuerCN(), true);
				certInfoStr += _makeCertField('Серійний номер', certInfo.GetSerial(), true);
				certInfoStr += _makeCertField('Тип', publicKeyType, true);
				certInfoStr += _makeCertField('Призначення', certInfo.GetKeyUsage(), false);
				
				certInfos.push(certInfoStr);
			}
			
			euSignTest.setItemsToList(
				'StorageCertList', certInfos);
		} catch (e) {
			alert("Виникла помилка при " + 
				"отриманні сертифікатів з файлового сховища: " + e);
		}
	},
//-----------------------------------------------------------------------------
	getCAServer: function() {
		var index = document.getElementById("CAsServersSelect").selectedIndex;

		if (index < euSignTest.CAsServers.length)
			return euSignTest.CAsServers[index];

		return null;
	},
	loadCAServer: function() {
		var index = utils.GetSessionStorageItem(
			euSignTest.CAServerIndexSessionStorageName, false, false);
		if (index != null) {
			document.getElementById("CAsServersSelect").selectedIndex = 
				parseInt(index);
			euSignTest.setCASettings(parseInt(index));
		}
	},
	storeCAServer: function() {
		var index = document.getElementById("CAsServersSelect").selectedIndex;
		return utils.SetSessionStorageItem(
			euSignTest.CAServerIndexSessionStorageName, index.toString(), false);
	},
	removeCAServer: function() {
		utils.RemoveSessionStorageItem(
			euSignTest.CAServerIndexSessionStorageName);
	},
//-----------------------------------------------------------------------------
	storePrivateKey: function(keyName, key, password, certificates) {
		if (!utils.SetSessionStorageItem(
				euSignTest.PrivateKeyNameSessionStorageName, keyName, false) ||
			!utils.SetSessionStorageItem(
				euSignTest.PrivateKeySessionStorageName, key, false) ||
			!utils.SetSessionStorageItem(
				euSignTest.PrivateKeyPasswordSessionStorageName, password, true) ||
			!euSignTest.storeCAServer()) {
			return false;
		}

		if (Array.isArray(certificates)) {
			if (!utils.SetSessionStorageItems(
					euSignTest.PrivateKeyCertificatesSessionStorageName,
					certificates, false)) {
				return false;
			}
		} else {
			if (!utils.SetSessionStorageItem(
					euSignTest.PrivateKeyCertificatesChainSessionStorageName,
					certificates, false)) {
				return false;
			}
		}

		return true;
	},
	removeStoredPrivateKey: function() {
		utils.RemoveSessionStorageItem(
			euSignTest.PrivateKeyNameSessionStorageName);
		utils.RemoveSessionStorageItem(
			euSignTest.PrivateKeySessionStorageName);
		utils.RemoveSessionStorageItem(
			euSignTest.PrivateKeyPasswordSessionStorageName);
		utils.RemoveSessionStorageItem(
			euSignTest.PrivateKeyCertificatesChainSessionStorageName);
		utils.RemoveSessionStorageItem(
		euSignTest.PrivateKeyCertificatesSessionStorageName);

		euSignTest.removeCAServer();
	},
//-----------------------------------------------------------------------------
	selectPrivateKeyFile: function(event) {
		var enable = (event.target.files.length == 1);

		setPointerEvents(document.getElementById('PKeyReadButton'), enable);
		document.getElementById('PKeyPassword').disabled = 
			enable ? '' : 'disabled';
		document.getElementById('PKeyFileName').value = 
			enable ? event.target.files[0].name : '';
		document.getElementById('PKeyPassword').value = '';
		
		if (enable) {
			var file = event.target.files[0];
			setPointerEvents(document.getElementById('PKeySaveInfo'), 
				file.name.endsWith(".jks"));
		}
	},
//-----------------------------------------------------------------------------
	getPrivateKeyCertificatesByCMP: function(key, password, onSuccess, onError) {
		try {
			var cmpAddress = euSignTest.getCAServer().cmpAddress + ":80";
			var keyInfo = euSign.GetKeyInfoBinary(key, password);
			onSuccess(euSign.GetCertificatesByKeyInfo(keyInfo, [cmpAddress]));
		} catch (e) {
			onError(e);
		}
	},
	getPrivateKeyCertificates: function(key, password, fromCache, onSuccess, onError) {
		var certificates;

		if (euSignTest.CAServer != null && 
			euSignTest.CAServer.certsInKey) {
			onSuccess([]);
			return;
		}
		
		if (fromCache) {
			if (euSignTest.useCMP) {
				certificates = utils.GetSessionStorageItem(
					euSignTest.PrivateKeyCertificatesChainSessionStorageName, true, false);
			} else if (euSignTest.loadPKCertsFromFile) {
				certificates = utils.GetSessionStorageItems(
					euSignTest.PrivateKeyCertificatesSessionStorageName, true, false)
			}

			onSuccess(certificates);
		} else if (euSignTest.useCMP) {
			euSignTest.getPrivateKeyCertificatesByCMP(
				key, password, onSuccess, onError);
		} else if (euSignTest.loadPKCertsFromFile){
			var _onSuccess = function(files) {
				var certificates = [];
				for (var i = 0; i < files.length; i++) {
					certificates.push(files[i].data);
				}

				onSuccess(certificates);
			};

			euSign.ReadFiles(
				euSignTest.privateKeyCerts,
				_onSuccess, onError);
		}
	},
	readPrivateKey: function(keyName, key, password, certificates, fromCache) {
		var _onError = function(e) {
			setStatus('');

			if (fromCache) {
				euSignTest.removeStoredPrivateKey();
				euSignTest.privateKeyReaded(false);
			} else {
				alert(e);
			}

			if (e.GetErrorCode != null && 
				e.GetErrorCode() == EU_ERROR_CERT_NOT_FOUND) {

				euSignTest.mainMenuItemClicked(
					document.getElementById('MainPageMenuCertsAndCRLs'),
					'MainPageMenuCertsAndCRLsPage');
			}
		};

		if (certificates == null) {
			var _onGetCertificates = function(certs) {
				if (certs == null) {
					_onError(euSign.MakeError(EU_ERROR_CERT_NOT_FOUND));
					return;
				}

				euSignTest.readPrivateKey(keyName, key, password, certs, fromCache);
			}

			euSignTest.getPrivateKeyCertificates(
				key, password, fromCache, _onGetCertificates, _onError);
			return;
		}
	
		try {
			if (Array.isArray(certificates)) {
				for (var i = 0; i < certificates.length; i++) {
					euSign.SaveCertificate(certificates[i]);
				}
			} else {
				euSign.SaveCertificates(certificates);
			}

			euSign.ReadPrivateKeyBinary(key, password);

			if (!fromCache && utils.IsSessionStorageSupported()) {
				if (!euSignTest.storePrivateKey(
						keyName, key, password, certificates)) {
					euSignTest.removeStoredPrivateKey();
				}
			}

			euSignTest.privateKeyReaded(true);

			euSignTest.updateCertList();

			if (!fromCache)
				euSignTest.showOwnerInfo();
		} catch (e) {
			_onError(e);
		}
	},
	readPrivateKeyAsImage: function(file, onSuccess, onError) {
		var image = new Image();
		image.onload=function(){
			try {
				var qr = new QRCodeDecode();
				
				var canvas = document.createElement('canvas');
				var context = canvas.getContext('2d');

				canvas.width = image.width;
				canvas.height = image.height;

				context.drawImage(image, 0, 0, canvas.width, canvas.height);
				var imagedata = context.getImageData(0, 0, canvas.width, canvas.height);
				var decoded = qr.decodeImageData(imagedata, canvas.width, canvas.height);
				var arr = [];
				for (var i = 0; i < decoded.length; i++)
					arr.push(decoded.charCodeAt(i));
				onSuccess(file.name, arr);
			} catch (e) {
				onError();
			}
		}
		
		image.src = utils.CreateObjectURL(file);
	},
	readPrivateKeyAsStoredFile: function() {
		var keyName = utils.GetSessionStorageItem(
			euSignTest.PrivateKeyNameSessionStorageName, false, false);
		var key = utils.GetSessionStorageItem(
			euSignTest.PrivateKeySessionStorageName, true, false);
		var password = utils.GetSessionStorageItem(
			euSignTest.PrivateKeyPasswordSessionStorageName, false, true);
		if (keyName == null || key == null || password == null) 
			return;

		euSignTest.loadCAServer();

		setStatus('зчитування ключа');
		setPointerEvents(document.getElementById('PKeyReadButton'), true);
		document.getElementById('PKeyFileName').value = keyName;
		document.getElementById('PKeyPassword').value = password;
		var _readPK = function() {
			euSignTest.readPrivateKey(keyName, key, password, null, true);
		}
		setTimeout(_readPK, 10);

		return;
	},
	readPrivateKeyButtonClick: function() {
		var passwordTextField = document.getElementById('PKeyPassword');
		var certificatesFiles = euSignTest.privateKeyCerts;

		var _onError = function(e) {
			setStatus('');
			alert(e);
		};
		
		var _onSuccess = function(keyName, key) {
			euSignTest.readPrivateKey(keyName, new Uint8Array(key),
				passwordTextField.value, null, false);
		}

		try {
			if (document.getElementById('PKeyReadButton').title == 'Зчитати') {
				setStatus('зчитування ключа');

				var files = document.getElementById('PKeyFileInput').files;

				if (files.length != 1) {
					_onError("Виникла помилка при зчитуванні особистого ключа. " + 
						"Опис помилки: файл з особистим ключем не обрано");
					return;
				}

				if (passwordTextField.value == "") {
					passwordTextField.focus();
					_onError("Виникла помилка при зчитуванні особистого ключа. " + 
						"Опис помилки: не вказано пароль доступу до особистого ключа");
					return;
				}
				
				if (euSignTest.loadPKCertsFromFile && 
					(certificatesFiles == null ||
					certificatesFiles.length <= 0)) {
					_onError("Виникла помилка при зчитуванні особистого ключа. " + 
						"Опис помилки: не обрано жодного сертифіката відкритого ключа");
					return;
				}

				if (utils.IsFileImage(files[0])) {
					euSignTest.readPrivateKeyAsImage(files[0], _onSuccess, _onError);
				}
				else {
					var _onFileRead = function(readedFile) {
						_onSuccess(readedFile.file.name, readedFile.data);
					};

					euSign.ReadFile(files[0], _onFileRead, _onError);
				}
			} else {
				euSignTest.removeStoredPrivateKey();
				euSign.ResetPrivateKey();
				euSignTest.privateKeyReaded(false);
				passwordTextField.value = "";
				euSignTest.clearPrivateKeyCertificatesList();
			}
		} catch (e) {
			_onError(e);
		}
	},
	showOwnerInfo: function () {
		try {
			var ownerInfo = euSign.GetPrivateKeyOwnerInfo();

			alert("Власник: " + ownerInfo.GetSubjCN() + "\n" + 
					"ЦСК: " + ownerInfo.GetIssuerCN() + "\n" + 
					"Серійний номер: " + ownerInfo.GetSerial());
		} catch (e) {
			alert(e);
		}
	},
	showOwnCertificates: function () {
		try {
			var splitLine = "--------------------------------------------------";
			var message = "Інформація про сертифікат(и) користувача:\n";
			var i = 0;
			while (true) {
				var info = euSign.EnumOwnCertificates(i);
				if (info == null)
					break;
				
				var isNationalAlgs = 
					(info.GetPublicKeyType() == EU_CERT_KEY_TYPE_DSTU4145);
				
				message += splitLine + "\n";
				message += "Сертифікат № " + (i + 1) + "\n" + 
					"Власник: " + info.GetSubjCN() + "\n" + 
					"ЦСК: " + info.GetIssuerCN() + "\n" + 
					"Серійний номер: " + info.GetSerial() + "\n" + 
					"Призначення: " + info.GetKeyUsage() + 
						(isNationalAlgs ? " в державних " : " в міжнародних ")  + 
						"алгоритмах та протоколах" + "\n";
				message += splitLine + "\n";

				i++;
			}
			
			if (i == 0)
				message += "Відсутня";
			
			alert(message);
			
		} catch (e) {
			alert(e);
		}
	},
	getJKSContainerInfo: function(jksContainer, password) {
		var info = '\tІнформація про JKS контейнер:\n';
		
		try {
			var keyIndex = 0;
			while (true) {
				var keyAlias = euSign.EnumJKSPrivateKeys(jksContainer, keyIndex);
				if (keyAlias == null)
					break;
				var jksKey = euSign.GetJKSPrivateKey(jksContainer, keyAlias);

				info += (keyIndex + 1) + '\n';
				info += 'Alias ключа: ' + keyAlias + '\n';
				info += 'Сертифікати: ' + '\n';

				for (var i = 0; i < jksKey.GetCertificatesCount(); i++) {
					var cert = jksKey.GetCertificate(i);
					var certInfo = euSign.ParseCertificate(cert);
					info += "Сертифікат № " + (i + 1) + '\n';
					info += "Власник: " + certInfo.GetSubject() + '\n';
					info += "ЦСК: " + certInfo.GetIssuer() + '\n';
					info += "Реєстраційний номер: " + certInfo.GetSerial() + '\n';
					info += "Призначення: " + certInfo.GetKeyUsage() + '\n';
					info += "Розширенне призначення: " + certInfo.GetExtKeyUsages() + '\n';
					info += "Бінарне подання: " + euSign.Base64Encode(cert) + '\n';
				}
				
				info += 'Інформація про відкриті ключі:\n';
				try {
					var keyInfo = euSign.GetKeyInfoBinary(
						jksKey.GetPrivateKey(), password);
					info += "Бінарне подання: " + euSign.Base64Encode(keyInfo) + '\n';
				} catch (e) {
					info += e + '\n';
				}
				
				keyIndex++;
			}
		} catch (e) {
			info += e + '\n';
		}
		
		return info;
	},
	savePKeyInfo: function() {
		var pThis = this;
		var pkFileInput = document.getElementById('PKeyFileInput');

		if (pkFileInput.files.length == 0) {
			alert('Файл з особистим ключем не обрано');
			return;
		}

		var _onError = function(msg) {
			alert("Виникла помилка при " + 
				"збереженні інформації про ос. ключ. " + msg);
		};
		
		var pkFile = pkFileInput.files[0];
		var password = document.getElementById('PKeyPassword').value;
		var info = 'Інформація про ос. ключ:\n';
		info += 'Ім`я файлу:' + pkFile.name + '\n\n';

		var encoder = new StringEncoder("UTF-8", true);

		eu_wait(function(runNext) {
			euSign.ReadFile(
				pkFile, 
				runNext, 
				function(e) {
					_onError(e);
				}
			);
		}).eu_wait(function(runNext, pkFileData) {
			var keyData = pkFileData.data;
			if (pkFile.name.endsWith(".jks")) {
				info += pThis.getJKSContainerInfo(keyData, password) + '\n';
			} else {
				info += 'Інформація про відкритий ключ:\n';
				try {
					var keyInfo = euSign.GetKeyInfoBinary(keyData, password);
					info += "Бінарне подання: " + euSign.Base64Encode(keyInfo) + '\n';
				} catch (e) {
					info += e + '\n';
				}
			}
			
			info += 'Інформація про зчитаний ключ:\n';
			try {
				if (euSign.IsPrivateKeyReaded()) {
					var i = 0;
					while (true) {
						var certInfo = euSign.EnumOwnCertificates(i);
						if (certInfo == null)
							break;
						var cert = euSign.GetCertificate(
							certInfo.GetIssuer(), certInfo.GetSerial());

						info += "Сертифікат № " + (i + 1) + '\n';
						info += "Власник: " + certInfo.GetSubject() + '\n';
						info += "ЦСК: " + certInfo.GetIssuer() + '\n';
						info += "Реєстраційний номер: " + certInfo.GetSerial() + '\n';
						info += "Призначення: " + certInfo.GetKeyUsage() + '\n';
						info += "Розширенне призначення: " + certInfo.GetExtKeyUsages() + '\n';
						info += "Бінарне подання: " + euSign.Base64Encode(cert) + '\n';

						i++;
					}
				} else {
					info += 'Ключ не зчитано' + '\n';
				}
			} catch (e) {
				info += e + '\n';
			}

			saveFile(pkFile.name + '.txt', 
				new Uint8Array(encoder.encode(info)));
		});
	},
	blockOwnCertificates: function() {
		if (!confirm('Після блокування сертифікатів ос. ключа ' + 
				'їх розблокування можливе лише при особистому ' + 
				'зверненні до АЦСК. Продовжити?')) {
			return;
		}

		try {
			euSign.ChangeOwnCertificatesStatus(
				EU_CCS_TYPE_HOLD, EU_REVOCATION_REASON_UNKNOWN);
			alert('Сертифікати ос. ключа успішно заблоковано');
		} catch (e) {
			alert(e);
		}
	},
	revokeOwnCertificates: function() {
		if (!confirm('Після скасування сертифікатів ос. ключа ' + 
				'використання ос. ключа буде не можливе. Продовжити?')) {
			return;
		}

		try {
			var revocationReason = parseInt(
				document.getElementById("PKeyRevokationReasonSelect").value);

			euSign.ChangeOwnCertificatesStatus(
				EU_CCS_TYPE_REVOKE, revocationReason);
			alert('Сертифікати ос. ключа успішно скасовано');
		} catch (e) {
			alert(e);
		}
	},
//-----------------------------------------------------------------------------
	changePrivKeyType: function() {
		var useUA = document.getElementById('ChooseKeysUARadioBtn').checked;
		var useRSA = document.getElementById('ChooseKeysRSARadioBtn').checked;
		
		if (document.getElementById('ChooseKeysUARSARadioBtn').checked)
			useUA = useRSA = true;

		document.getElementById('UAPrivKeyParams').style.display = 
			useUA ? 'block' : 'none';
		document.getElementById('InternationalPrivKeyParams').style.display = 
			useRSA ? 'block': 'none';
	},
	generatePK: function() {
		var pkPassword = document.getElementById('PGenKeyPassword').value;
		
		if (pkPassword == "") {
			alert("Пароль особистого ключа не вказано");
			document.getElementById('PGenKeyPassword').focus();
			return;
		}

		var useUA = document.getElementById('ChooseKeysUARadioBtn').checked;
		var useRSA = document.getElementById('ChooseKeysRSARadioBtn').checked;

		if (document.getElementById('ChooseKeysUARSARadioBtn').checked)
			useUA = useRSA = true;

		var uaKeysType = useUA ? 
			EU_KEYS_TYPE_DSTU_AND_ECDH_WITH_GOST : EU_KEYS_TYPE_NONE; 
		var uaDSKeysSpec = useUA ? 
			parseInt(document.getElementById("UAKeySpecSelect").value) : 0;
		var uaKEPSpec = useUA ?
			parseInt(document.getElementById("UAKEPKeySpecSelect").value) : 0;

		var intKeysType = useRSA ? 
			EU_KEYS_TYPE_RSA_WITH_SHA : EU_KEYS_TYPE_NONE; 

		var intKeysSpec = useRSA ? 
			parseInt(document.getElementById("InternationalKeySpecSelect").value) : 0;

		var userInfo = EndUserInfo();
		userInfo.commonName = "User 1";
		userInfo.locality = "Kharkov";
		userInfo.state = "Kharkovska";

		var _generatePKFunction = function() {
			try {
				euSign.SetRuntimeParameter(
					EU_MAKE_PKEY_PFX_CONTAINER_PARAMETER,
					document.getElementById('PKPFXContainerCheckbox').checked);
			
				var privKey = euSign.GeneratePrivateKey(
					pkPassword, uaKeysType, uaDSKeysSpec, false, uaKEPSpec, 
					intKeysType, intKeysSpec, null, null);

				saveFile(privKey.privateKeyName, privKey.privateKey);
				/*saveFile(privKey.privateKeyInfoName, privKey.privateKeyInfo);*/
			
				if (useUA) {
					saveFile(privKey.uaRequestName, privKey.uaRequest);
					saveFile(privKey.uaKEPRequestName, privKey.uaKEPRequest);
				}
			
				if (useRSA) {
					saveFile(privKey.internationalRequestName, 
						privKey.internationalRequest);
				}
				setStatus('');
			} catch (e) {
				setStatus('');
				alert("Виникла помилка при генерації особистого ключа. " + 
					"Опис помилки: " + e);
			}
		};

		setStatus('генерація ключа');
		setTimeout(_generatePKFunction, 10);
},
//-----------------------------------------------------------------------------
	signData: function () {
		var data = document.getElementById('DataToSignTextEdit').value + "";
		var isInternalSign = 
			document.getElementById("InternalSignCheckbox").checked;
		var isAddCert = 
			document.getElementById("AddCertToInternalSignCheckbox").checked;
		var isSignHash = 
			document.getElementById("SignHashCheckbox").checked;
		var signedDataText = document.getElementById("SignedDataText"); 
		var dsAlgType = parseInt(document.getElementById("DSAlgTypeSelect").value)
		
		signedDataText.value = "";

		var _signDataFunction = function() {
			try {
				var sign = "";
				if (dsAlgType == 1) {
					if (isInternalSign) {
						sign = euSign.SignDataInternal(isAddCert, data, true);
					} else {
						if (isSignHash) {
							var hash = euSign.HashData(data);
							sign = euSign.SignHash(hash, true);
						} else {
							sign = euSign.SignData(data, true);
						}
					}
				} else {
					sign = euSign.SignDataRSA(data, isAddCert, 
						!isInternalSign, true);
				}

				signedDataText.value = sign;
				setStatus('');
			} catch (e) {
				setStatus('');
				alert(e);
			}
		};

		setStatus('підпис данних');
		setTimeout(_signDataFunction, 10);
	},
	verifyData: function () {
		var data = document.getElementById('DataToSignTextEdit').value + "";
		var signedData = document.getElementById('SignedDataText').value;
		var isInternalSign = 
			document.getElementById("InternalSignCheckbox").checked;
		var isSignHash = 
			document.getElementById("SignHashCheckbox").checked;
		var isGetSignerInfo = 
			document.getElementById("GetSignInfoCheckbox").checked;
		var verifiedDataText = document.getElementById("VerifiedDataText");
		var dsAlgType = parseInt(document.getElementById("DSAlgTypeSelect").value)
		verifiedDataText.value = "";

		var _verifyDataFunction = function() {
			try {
				var info = "";
				if (isInternalSign) {
					info = euSign.VerifyDataInternal(signedData);
				} else {
					if (isSignHash && dsAlgType == 1) {
						var hash = euSign.HashData(data);
						info = euSign.VerifyHash(hash, signedData);
					} else {
						info = euSign.VerifyData(data, signedData);
					}
				}
			
				var message = "Підпис успішно перевірено";
			
				if (isGetSignerInfo) {
					var ownerInfo = info.GetOwnerInfo();
					var timeInfo = info.GetTimeInfo();

					message += "\n";
					message += "Підписувач: " + ownerInfo.GetSubjCN() + "\n" + 
								"ЦСК: " + ownerInfo.GetIssuerCN() + "\n" + 
								"Серійний номер: " + ownerInfo.GetSerial() + "\n";
					if (timeInfo.IsTimeAvail()) {
						message += (timeInfo.IsTimeStamp() ? 
							"Мітка часу (від даних):" : "Час підпису: ") + timeInfo.GetTime();
					} else {
						message += "Час підпису відсутній";
					}

					if (timeInfo.IsSignTimeStampAvail()) {
						message += "\nМітка часу (від підпису):" + timeInfo.GetSignTimeStamp();
					}
				}
			
				if (isInternalSign) {
					message += "\n";
					verifiedDataText.value = euSign.ArrayToString(info.GetData());
					message += "Підписані дані: " + verifiedDataText.value + "\n";
				}
			
				setStatus('');
				alert(message);
			} catch (e) {
				setStatus('');
				alert(e);
			}
		}

		setStatus('перевірка підпису даних');
		setTimeout(_verifyDataFunction, 10);
	},
//-----------------------------------------------------------------------------
	chooseFileToSign: function (event) {
		var enable = (event.target.files.length == 1);

		setPointerEvents(document.getElementById('SignFileButton'), enable);
	},
	chooseFileToVerify: function (event) {
		var enable = (document.getElementById('FileToVerify').files.length == 1) && 
		(document.getElementById("InternalSignCheckbox").checked || 
			document.getElementById('FileWithSign').files.length == 1)

		setPointerEvents(document.getElementById('VerifyFileButton'), enable);
	},
	signFile: function() {
		var file = document.getElementById('FileToSign').files[0];
		
		if (file.size > Module.MAX_DATA_SIZE) {
			alert("Розмір файлу для піпису занадто великий. Оберіть файл меншого розміру");
			return;
		}
		
		var fileReader = new FileReader();

		fileReader.onloadend  = (function(fileName) {
			return function(evt) {
				if (evt.target.readyState != FileReader.DONE)
					return;

				var isInternalSign = 
					document.getElementById("InternalSignCheckbox").checked;
				var isAddCert = document.getElementById(
					"AddCertToInternalSignCheckbox").checked;
				var dsAlgType = parseInt(
					document.getElementById("DSAlgTypeSelect").value);

				var data = new Uint8Array(evt.target.result);

				try {
					var sign;

					if (dsAlgType == 1) {
						if (isInternalSign)
							sign = euSign.SignDataInternal(isAddCert, data, false);
						else
							sign = euSign.SignData(data, false);
					} else {
						sign = euSign.SignDataRSA(data, isAddCert, 
							!isInternalSign, false);
					}

					saveFile(fileName + ".p7s", sign);

					setStatus('');
					alert("Файл успішно підписано");
				} catch (e) {
					setStatus('');
					alert(e);
				}
			};
		})(file.name);

		setStatus('підпис файлу');
		fileReader.readAsArrayBuffer(file);
	},
	verifyFile: function() {
		var isInternalSign = 
			document.getElementById("InternalSignCheckbox").checked;
		var isGetSignerInfo = 
			document.getElementById("GetSignInfoCheckbox").checked;
		var files = [];

		files.push(document.getElementById('FileToVerify').files[0]);
		if (!isInternalSign)
			files.push(document.getElementById('FileWithSign').files[0]);
			
		if ((files[0].size > (Module.MAX_DATA_SIZE + EU_MAX_P7S_CONTAINER_SIZE)) ||
			(!isInternalSign && (files[1].size > Module.MAX_DATA_SIZE))) {
			alert("Розмір файлу для перевірки підпису занадто великий. Оберіть файл меншого розміру");
			return;
		}
		
		var _onSuccess = function(files) {
			try {
				var info = "";
				if (isInternalSign) {
					info = euSign.VerifyDataInternal(files[0].data);
				} else {
					info = euSign.VerifyData(files[0].data, files[1].data);
				}

				var message = "Підпис успішно перевірено";
				
				if (isGetSignerInfo) {
					var ownerInfo = info.GetOwnerInfo();
					var timeInfo = info.GetTimeInfo();

					message += "\n";
					message += "Підписувач: " + ownerInfo.GetSubjCN() + "\n" + 
								"ЦСК: " + ownerInfo.GetIssuerCN() + "\n" + 
								"Серійний номер: " + ownerInfo.GetSerial() + "\n";
					if (timeInfo.IsTimeAvail()) {
						message += (timeInfo.IsTimeStamp() ? 
							"Мітка часу (від даних):" : "Час підпису: ") + timeInfo.GetTime();
					} else {
						message += "Час підпису відсутній";
					}

					if (timeInfo.IsSignTimeStampAvail()) {
						message += "\nМітка часу (від підпису):" + timeInfo.GetSignTimeStamp();
					}
				}

				if (isInternalSign) {
					saveFile(files[0].name.substring(0, 
						files[0].name.length - 4), info.GetData());
				}

				alert(message);
				setStatus('');
			} catch (e) {
				alert(e);
				setStatus('');
			}
		}
		
		var _onFail = function(files) {
			setStatus('');
			alert("Виникла помилка при зчитуванні файлів для перевірки підпису");
		}

		setStatus('перевірка підпису файлів');
		utils.LoadFilesToArray(files, _onSuccess, _onFail);
	},
//-----------------------------------------------------------------------------
	envelopData: function() {
		var issuers = euSignTest.recepientsCertsIssuers;
		var serials = euSignTest.recepientsCertsSerials;

		if (issuers == null || serials == null || 
			issuers.length <= 0 || serials.length <= 0) {
			alert("Не обрано жодного сертифіката отримувача");
			return;
		}

		var isAddSign = document.getElementById("AddSignCheckbox").checked;
		var data = document.getElementById("DataToEnvelopTextEdit").value;
		var envelopedText = document.getElementById("EnvelopedDataText");
		var developedText = document.getElementById("DevelopedDataText");
		var kepAlgType = parseInt(document.getElementById("KEPAlgTypeSelect").value);
					
		envelopedText.value = "";
		developedText.value = "";

		var _envelopDataFunction = function() {
			try {
				if (kepAlgType == 1) {
					envelopedText.value = euSign.EnvelopDataEx(
						issuers, serials, isAddSign, data, true);
				} else {
					envelopedText.value = euSign.EnvelopDataRSAEx(
						kepAlgType, issuers, serials, isAddSign, data, true);
				}
				setStatus('');
			} catch (e) {
				setStatus('');
				alert(e);
			} 
		};

		setStatus('зашифрування даних');
		setTimeout(_envelopDataFunction, 10);
	},
	developData: function () {
		var envelopedText = document.getElementById("EnvelopedDataText");
		var developedText = document.getElementById("DevelopedDataText");

		developedText.value = "";

		var _developDataFunction = function() {
			try {
				var info = euSign.DevelopData(envelopedText.value);
				var ownerInfo = info.GetOwnerInfo();
				var timeInfo = info.GetTimeInfo();
				
				var message = "Дані успішно розшифровано";
				message += "\n";
				message += "Відправник: " + ownerInfo.GetSubjCN() + "\n" + 
							"ЦСК: " + ownerInfo.GetIssuerCN() + "\n" + 
							"Серійний номер: " + ownerInfo.GetSerial() + "\n";
				if (timeInfo.IsTimeAvail()) {
					message += (timeInfo.IsTimeStamp() ? 
						"Мітка часу:" : "Час підпису: ") + timeInfo.GetTime();
				} else {
					message += "Підпис відсутній";
				}
			
				developedText.value = euSign.ArrayToString(info.GetData());

				setStatus('');
				alert(message);
			} catch (e) {
				setStatus('');
				alert(e);
			}
		};

		setStatus('розшифрування даних');
		setTimeout(_developDataFunction, 10);
	},
//-----------------------------------------------------------------------------
	chooseEnvelopFile: function (event) {
		var enable = (event.target.files.length == 1);

		setPointerEvents(document.getElementById('EnvelopFileButton'), enable);
		setPointerEvents(document.getElementById('DevelopedFileButton'), enable);
	},
	envelopFile: function() {
		var issuers = euSignTest.recepientsCertsIssuers;
		var serials = euSignTest.recepientsCertsSerials;

		if (issuers == null || serials == null || 
			issuers.length <= 0 || serials.length <= 0) {
			alert("Не обрано жодного сертифіката отримувача");
			return;
		}	
	
		var file = document.getElementById('EnvelopFiles').files[0];
		var fileReader = new FileReader();
		
		fileReader.onloadend  = (function(fileName) {
			return function(evt) {
				if (evt.target.readyState != FileReader.DONE)
					return;

				var fileData = new Uint8Array(evt.target.result);
				var isAddSign = document.getElementById("AddSignCheckbox").checked;
				var kepAlgType = parseInt(document.getElementById("KEPAlgTypeSelect").value);
				var envelopedFileData;
				try {
					if (kepAlgType == 1) {
						envelopedFileData = euSign.EnvelopDataEx(
							issuers, serials, isAddSign, fileData, false);
					} else {
						envelopedFileData = euSign.EnvelopDataRSAEx(
							kepAlgType, issuers, serials, isAddSign, fileData, false);
					}
					saveFile(fileName + ".p7e", envelopedFileData);

					setStatus('');
					alert("Файл успішно зашифровано");
				} catch (e) {
					setStatus('');
					alert(e);
				}
			};
		})(file.name);

		fileReader.readAsArrayBuffer(file);
	},
	developFile: function() {
		var file = document.getElementById('EnvelopFiles').files[0];
		var fileReader = new FileReader();

		if (file.size > (Module.MAX_DATA_SIZE + EU_MAX_P7E_CONTAINER_SIZE)) {
			alert("Розмір файлу для розшифрування занадто великий. Оберіть файл меншого розміру");
			return;
		}
		
		fileReader.onloadend  = (function(fileName) {
			return function(evt) {
				if (evt.target.readyState != FileReader.DONE)
					return;

				var fileData = new Uint8Array(evt.target.result);

				try {
					var info = euSign.DevelopData(fileData);
					var ownerInfo = info.GetOwnerInfo();
					var timeInfo = info.GetTimeInfo();
						
					var message = "Файл успішно розшифровано";
					message += "\n";
					message += "Відправник: " + ownerInfo.GetSubjCN() + "\n" + 
								"ЦСК: " + ownerInfo.GetIssuerCN() + "\n" + 
								"Серійний номер: " + ownerInfo.GetSerial() + "\n";
					if (timeInfo.IsTimeAvail()) {
						message += (timeInfo.IsTimeStamp() ? 
							"Мітка часу:" : "Час підпису: ") + timeInfo.GetTime();
					} else {
						message += "Підпис відсутній";
					}

					setStatus('');
					alert(message);

					saveFile(fileName.substring(0, fileName.length - 4), info.GetData());
				} catch (e) {
					setStatus('');
					alert(e);
				}
			};
		})(file.name);

		setStatus('розшифрування файлу');
		fileReader.readAsArrayBuffer(file);
	},
//-----------------------------------------------------------------------------
	getOwnCertificateInfo: function(keyType, keyUsage) {
		try {
			var index = 0;
			while (true) {
				var info = euSign.EnumOwnCertificates(index);
				if (info == null)
					return null;
					
				if ((info.GetPublicKeyType() == keyType) && 
					((info.GetKeyUsageType() & keyUsage) == keyUsage))
				{
					return info;
				}

				index++;
			}
		} catch(e) {
			alert(e);
		}

		return null;
	},
	getOwnCertificate: function(keyType, keyUsage) {
		try {
			var info = euSignTest.getOwnCertificateInfo(
				keyType, keyUsage);
			if (info == null)
				return null;
			
			return euSign.GetCertificate(
				info.GetIssuer(), info.GetSerial());
		} catch(e) {
			alert(e);
		}
		
		return null;
	},
	recepientCertLoaded: function (files, curIndex, processedFiles) {
		return function(evt) {
			if (evt.target.readyState != FileReader.DONE)
				return;

			var file = new Object();
			file.name = files[curIndex].name;
			file.isCertificate = 
				euSignTest.isCertificateExtension(file.name);
			if (file.isCertificate) {
				file.data = new Uint8Array(evt.target.result);
			}

			processedFiles.push(file);
			curIndex++;

			if (curIndex < files.length) {
				var fileReader = new FileReader();
				fileReader.onloadend = euSignTest.recepientCertLoaded(
						files, curIndex, processedFiles);
				fileReader.readAsArrayBuffer(files[curIndex]);
				return;
			}
			
			euSignTest.recepientCertsLoaded(processedFiles);
		};
	},
	recepientCertsLoaded: function(processedFiles) {
		var loadedFiles = [];
		var issuers = [];
		var serials = [];
		
		for (var i = 0; i < processedFiles.length; i++) {
			var file = processedFiles[i];
			var fileInfo = file.name;
			if (!file.isCertificate) {
				fileInfo += "<br>(Не завантажено: " + 
					"не вірне розширення файлу '.cer')";
			} else {
				try {
					var certInfo = euSign.ParseCertificate(file.data);
					fileInfo += "<br>Власник: " + certInfo.subjCN + "<br>" + 
							"ЦСК: " + certInfo.issuerCN + "<br>" +
							"Серійний номер: " +  certInfo.serial;
					issuers.push(certInfo.issuer);
					serials.push(certInfo.serial);
					euSign.SaveCertificate(file.data);
				} catch (e) {
					fileInfo += "<br>(Не завантажено: " + e.toString() + ")";
				}
			}
			
			loadedFiles.push(fileInfo);
		}

		euSignTest.setItemsToList(
			'SelectedRecipientsCertsList', loadedFiles);

		euSignTest.recepientsCertsIssuers = issuers;
		euSignTest.recepientsCertsSerials = serials;
	},
	chooseRecepientsCertificates: function(event) {
		euSignTest.recepientsCertsIssuers = [];
		euSignTest.recepientsCertsSerials = [];

		var files = event.target.files;
		if (files.length <= 0) {
			document.getElementById('SelectedRecipientsCertsList').innerHTML = 
				"Не обрано жодного сертифіката";
			return;
		}

		document.getElementById('SelectedRecipientsCertsList').innerHTML = "";

		var fileReader = new FileReader();
		fileReader.onloadend = euSignTest.recepientCertLoaded(
			files, 0, []);
		fileReader.readAsArrayBuffer(files[0]);
	},
	signDataPerformance: function(data, count) {
		var _signFunction = function(data, isRSA) {
			try {
				var t0 = performance.now();

				if (isRSA)
					euSign.SignDataRSA(data, true, true, true);
				else
					euSign.SignData(data, true);

				var t1 = performance.now();

				return t1 - t0;
			} catch (e) {
				console.log(e);
				throw e;
			}
		};

		var _appendResult = function(algoName, keyBits, useTsp, firstTime, avgTime) {
			var resultText = document.getElementById('TestSignText');
			resultText.value += "Тестування швидкодії підпису " + algoName + 
				"(" + (useTsp ? "з TSP" : "без TSP") + ", " + keyBits + " бітів)\r\n";
			resultText.value += "Перший:" + firstTime + "(мс)\r\n";
			resultText.value += "Середнє:" + avgTime + "(мс)\r\n";
		};

		var _setTSP = function(use) {
			var mode = euSign.CreateModeSettings();
			mode.SetOfflineMode(use);
		};

		var _testSign = function(ownCertInfo, isRSA, useTsp) {
			var mode = euSign.CreateModeSettings();
			mode.SetOfflineMode(!useTsp);
			euSign.SetModeSettings(mode);
			
			var firstTime = _signFunction(data, isRSA);
			var times = 0;
			for (var i = 0; i < count; i++)
				times += _signFunction(data, isRSA);
			
			_appendResult(isRSA ? "RSA" : "ДСТУ-4145", 
				ownCertInfo.GetPublicKeyBits(), 
				useTsp, firstTime, times / count);
			
			mode.SetOfflineMode(false);
			euSign.SetModeSettings(mode);
		}
		
		var resultText = document.getElementById('TestSignText');
		resultText.value += "Тестування швидкодії функцій підпису (" + 
			count + " тестів)...\r\n";
			
		var ownCertInfo = euSignTest.getOwnCertificateInfo(
			EU_CERT_KEY_TYPE_DSTU4145, EU_KEY_USAGE_DIGITAL_SIGNATURE);
		if (ownCertInfo) {
			_testSign(ownCertInfo, false, true);
			_testSign(ownCertInfo, false, false);
		}

		ownCertInfo = euSignTest.getOwnCertificateInfo(
			EU_CERT_KEY_TYPE_RSA, EU_KEY_USAGE_DIGITAL_SIGNATURE);
		if (ownCertInfo) {
			_testSign(ownCertInfo, true, true);
			_testSign(ownCertInfo, true, false);
		}
	},
	testSignature: function() {
		var string = "Data to sign, 1234567890";
		var array = new Uint8Array([0, 1, 2, 3, 4, 5, 6, 7, 8]);
		
		var sign, hash, info;
		
		var resultText = document.getElementById('TestSignText');
		resultText.value = "Тестування функцій підпису...\r\n";
		
		try {
			this.signDataPerformance(array, 100);
		
			resultText.value += 
				"Тестування функцій зовнішнього підпису даних...\r\n";
			sign = euSign.SignData(string, true);
			info = euSign.VerifyData(string, sign);
			info = euSign.VerifyDataOnTimeEx(string, 0, sign, 
				new Date(), true, true);

			sign = euSign.SignData(array, false);
			info = euSign.VerifyData(array, sign);
			info = euSign.VerifyDataOnTimeEx(array, 0, sign, 
				null, true, true);

			sign = euSign.SignData(array, true);
			info = euSign.VerifyData(array, sign);

			resultText.value += 
				"Тестування функцій внутрішнього підпису даних...\r\n";
			sign = euSign.SignDataInternal(true, string, true);
			info = euSign.VerifyDataInternal(sign);
			if (euSign.ArrayToString(info.GetData()) != string) {
				resultText.value += "Тестування функцій внутрішнього підпису " + 
					"завершилося з помилкою: " + 
					"Перевірені дані не співпадають з даними, що підписувалися";
				return false;
			}
			info = euSign.VerifyDataInternalOnTimeEx(0, sign, 
				new Date(), false, true);

			sign = euSign.SignDataInternal(false, string, false);
			info = euSign.VerifyDataInternal(sign);
			if (euSign.ArrayToString(info.GetData()) != string) {
				resultText.value += "Тестування функцій внутрішнього підпису " + 
					"завершилося з помилкою: " + 
					"Перевірені дані не співпадають з даними, що підписувалися";
				return false;
			}

			sign = euSign.SignDataInternal(false, array, false);
			info = euSign.VerifyDataInternal(sign);
			if (!utils.CompareArrays(info.GetData(), array)) {
				resultText.value += "Тестування функцій внутрішнього підпису " + 
					"завершилося з помилкою: " + 
					"Перевірені дані не співпадають з даними, що підписувалися";
				return false;
			}
			
			resultText.value += "Тестування функцій підпису геш...\r\n";
			hash = euSign.HashData(string, true);
			sign = euSign.SignHash(hash, true);
			info = euSign.VerifyHash(hash, sign);
			info = euSign.VerifyHashOnTimeEx(hash, 0, sign,
				new Date(), true, true);
			
			hash = euSign.HashData(string, false);
			sign = euSign.SignHash(hash, true);
			info = euSign.VerifyHash(hash, sign);
			info = euSign.VerifyHashOnTimeEx(hash, 0, sign,
				null, true, true);
			
			hash = euSign.HashData(array, false);
			sign = euSign.SignHash(hash, true);
			info = euSign.VerifyHash(hash, sign);
		} catch (e) {
			resultText.value += "Тестування функцій підпису " + 
				"завершилося з помилкою: " + e.toString();
			return false;
		}

		if (!euSignTest.testRemoteSign() ||
			!euSignTest.testRawSign()) {
			return false;
		}

		resultText.value += "Тестування функцій підпису " +
				"завершилося успішно";

		return true;
	},
	testRemoteSign: function() {
		var string = "Data to sign, 1234567890";
		var array = new Uint8Array([0, 1, 2, 3, 4, 5, 6, 7, 8]);

		var ownCert, hash;
		var emptySign, signer, sign;
		var info;
		
		var resultText = document.getElementById('TestSignText');
		
		resultText.value += "Тестування функцій додавання підпису...\r\n";
		try {
			ownCert = euSignTest.getOwnCertificate(
				EU_CERT_KEY_TYPE_DSTU4145, EU_KEY_USAGE_DIGITAL_SIGNATURE);
			if (ownCert == null) {
				resultText.value += "Тестування функцій додавання підпису " + 
					"завершилося з помилкою: " + 
					"Сертифікат користувача для підпису за " + 
					"алгоритмом ДСТУ-4145 не знайдено";
				return false;
			}
			
			hash = euSign.HashData(string);
			emptySign = euSign.CreateEmptySign(null, true);
			signer = euSign.CreateSigner(hash, true);
			sign = euSign.AppendSigner(signer, null, emptySign, true);
			info = euSign.VerifyHash(hash, sign);

			hash = euSign.HashData(string);
			emptySign = euSign.CreateEmptySign(string);
			signer = euSign.CreateSigner(hash);
			sign = euSign.AppendSigner(signer, ownCert, emptySign);
			info = euSign.VerifyDataInternal(sign);
			if (euSign.ArrayToString(info.GetData()) != string) {
				resultText.value += "Тестування функцій додавання підпису " + 
					"завершилося з помилкою: " +
					"Перевірені дані не співпадають з даними, " +
					"що підписувалися";
				return false;
			}

			hash = euSign.HashData(array);
			emptySign = euSign.CreateEmptySign(array);
			signer = euSign.CreateSigner(hash);
			sign = euSign.AppendSigner(signer, ownCert, emptySign);
			info = euSign.VerifyDataInternal(sign);
			if (!utils.CompareArrays(info.GetData(), array)) {
				resultText.value += "Тестування функцій додавання підпису " + 
					"завершилося з помилкою: " +
					"Перевірені дані не співпадають з даними, " +
					"що підписувалися";
				return false;
			}

		} catch(e) {
			resultText.value += "Тестування функцій додавання підпису " + 
				"завершилося з помилкою: " + e.toString();
			
			return false;
		}
		
		return true;
	},
	testRawSign: function() {
		var string = "Data to sign, 1234567890";
		var array = new Uint8Array([0, 1, 2, 3, 4, 5, 6, 7, 8]);

		var ownCert, hash;
		var sign;
		var info;
		
		var resultText = document.getElementById('TestSignText');
		
		resultText.value += "Тестування функцій спрощеного підпису...\r\n";
		try {
			ownCert = euSignTest.getOwnCertificate(
				EU_CERT_KEY_TYPE_DSTU4145, EU_KEY_USAGE_DIGITAL_SIGNATURE);
			if (ownCert == null) {
				resultText.value += "Тестування функцій спрощеного підпису " + 
					"завершилося з помилкою: " + 
					"Сертифікат користувача для підпису за " + 
					"алгоритмом ДСТУ-4145 не знайдено";
				return false;
			}
			
			hash = euSign.HashData(array);
			sign = euSign.RawSignHash(hash);
			info = euSign.RawVerifyHash(hash, sign);

			hash = euSign.HashData(string, true);
			sign = euSign.RawSignHash(hash, true);
			info = euSign.RawVerifyHash(hash, sign);

			sign = euSign.RawSignData(array);
			info = euSign.RawVerifyDataEx(null, array, sign);
			
			sign = euSign.RawSignData(string);
			info = euSign.RawVerifyDataEx(ownCert, string, sign);
		} catch(e) {
			resultText.value += "Тестування функцій спрощеного підпису " + 
				"завершилося з помилкою: " + e.toString();
			
			return false;
		}
		
		return true;
	},
	testEnvelop: function() {
		var string = "Data to envelop, 1234567890";
		var array = new Uint8Array([0, 1, 2, 3, 4, 5, 6, 7, 8]);
		
		var ownCertInfo;
		var envelopedData, developedData;
		var info;
		
		var resultText = document.getElementById('TestEnvelopText');
		resultText.value = "Тестування функцій шифрування даних...\r\n";
		
		try {
			ownCertInfo = euSignTest.getOwnCertificateInfo(
				EU_CERT_KEY_TYPE_DSTU4145, EU_KEY_USAGE_KEY_AGREEMENT);
			if (ownCertInfo == null) {
				resultText.value += "Тестування функцій шифрування даних " + 
					"завершилося з помилкою: " + 
					"Сертифікат користувача для направленого шифрування не знайдено";
				return false;
			}

			envelopedData = euSign.EnvelopDataEx(
				[ownCertInfo.issuer], [ownCertInfo.serial],
				false, string, true);
			info = euSign.DevelopData(envelopedData);
			if (euSign.ArrayToString(info.GetData()) != string) {
				resultText.value += "Тестування функцій шифрування даних " + 
					"завершилося з помилкою: " +
					"Розшифровані дані не співпадають з даними, що зашифровувалися";
				return false;
			}
			
			envelopedData = euSign.EnvelopDataEx(
				[ownCertInfo.issuer], [ownCertInfo.serial],
				true, array, false);
			info = euSign.DevelopData(envelopedData);
			if (!utils.CompareArrays(info.GetData(), array)) {
				resultText.value += "Тестування функцій шифрування даних " + 
					"завершилося з помилкою: " +
					"Розшифровані дані не співпадають з даними, що зашифровувалися";
				return false;
			}
			
			resultText.value += "Тестування функцій щифрування " + 
				"завершилося успішно\r\n";
		} catch (e) {
			resultText.value += "Тестування функцій щифрування " + 
				"завершилося з помилкою: " + e.toString();
			
			return false;
		}
		
		if (!this.testSession())
			return false;
		
		return true;
	},
	testSession: function() {
		var string = "Data to envelop, 1234567890";
		var array = new Uint8Array([0, 1, 2, 3, 4, 5, 6, 7, 8]);

		var ownCert, ownCertInfo;

		var userSession = null, serverSession = null;
		var userCert, serverCert;
		var savedUserSession, savedServerSession;

		var resultText = document.getElementById('TestEnvelopText');
		resultText.value += "Тестування функцій захищеної сесії...\r\n";

		try {
			ownCert = euSignTest.getOwnCertificate(
				EU_CERT_KEY_TYPE_DSTU4145, EU_KEY_USAGE_KEY_AGREEMENT);
			ownCertInfo = euSignTest.getOwnCertificateInfo(
				EU_CERT_KEY_TYPE_DSTU4145, EU_KEY_USAGE_KEY_AGREEMENT);
			if (ownCert == null || ownCertInfo == null) {
				resultText.value += "Тестування функцій захищеної сесії " + 
					"завершилося з помилкою: " + 
					"Сертифікат користувача для направленого шифрування не знайдено";
				return false;
			}
			
			userSession = euSign.ClientSessionCreateStep1(3600);
			serverSession = euSign.ServerSessionCreateStep1(
				3600, userSession.GetData());
			euSign.ClientSessionCreateStep2(userSession,
				serverSession.GetData());
			euSign.ServerSessionCreateStep2(serverSession,
				userSession.GetData());

			if (!euSign.SessionIsInitialized(userSession) ||
				!euSign.SessionIsInitialized(serverSession) ||
				!euSign.SessionCheckCertificates(userSession)) {
				resultText.value += "Тестування функцій захищеної сесії " + 
					"завершилося з помилкою: " + 
					"Сесію не ініціалізовано";
				return false;
			}

			serverCert = euSign.SessionGetPeerCertificateInfo(
				userSession);
			userCert = euSign.SessionGetPeerCertificateInfo(
				serverSession);
			if (serverCert.GetIssuer() != userCert.GetIssuer() ||
				serverCert.GetIssuer() != ownCertInfo.GetIssuer() ||
				serverCert.GetSerial() != ownCertInfo.GetSerial()) {
				resultText.value += "Тестування функцій захищеної сесії " + 
					"завершилося з помилкою: " + 
					"Сертифікати сервера та клієнта не співпадає";
				return false;
			}

			var _testEncryption = function(_ses1, _ses2, _testData) {
				var _isStr = ((typeof _testData) == 'string');
				var _envData, _devData;
				
				_envData = euSign.SessionEncrypt(
					_ses1, _testData, _isStr);
				_devData = euSign.SessionDecrypt(
					_ses2, _envData);
				if (_isStr) {
					if (_testData != euSign.ArrayToString(_devData))
						return false;
				} else {
					if (!utils.CompareArrays(_testData, _devData))
						return false;
				}

				_envData = euSign.SessionEncryptContinue(
					_ses1, _testData, _isStr);
				_devData = euSign.SessionDecryptContinue(
					_ses2, _envData);
				if (_isStr) {
					if (_testData != euSign.ArrayToString(_devData))
						return false;
				} else {
					if (!utils.CompareArrays(_testData, _devData))
						return false;
				}

				return true;
			}

			if (!_testEncryption(userSession, serverSession, string) ||
				!_testEncryption(userSession, serverSession, array)) {
				resultText.value += "Тестування функцій захищеної сесії " + 
					"завершилося з помилкою: " + 
					"Розшифровані дані не співпадають";
				return false;
			}

			savedUserSession = euSign.SessionSave(userSession);
			savedServerSession = euSign.SessionSave(serverSession);

			euSign.SessionClose(userSession);
			userSession = null;
			euSign.SessionClose(serverSession);
			serverSession = null;

			userSession = euSign.SessionLoad(savedUserSession);
			serverSession = euSign.SessionLoad(savedServerSession);

			if (!_testEncryption(userSession, serverSession, string) ||
				!_testEncryption(userSession, serverSession, array)) {
				resultText.value += "Тестування функцій захищеної сесії " + 
					"завершилося з помилкою: " + 
					"Розшифровані дані не співпадають";
				return false;
			}

			euSign.SessionClose(userSession);
			userSession = null;
			euSign.SessionClose(serverSession);
			serverSession = null;

			userSession = euSign.ClientDynamicKeySessionCreate(3600, 
				ownCertInfo.GetIssuer(), ownCertInfo.GetSerial());
			serverSession = euSign.ServerDynamicKeySessionCreate(
				3600, userSession.GetData());
				
			if (!_testEncryption(userSession, serverSession, string) ||
				!_testEncryption(userSession, serverSession, array)) {
				resultText.value += "Тестування функцій захищеної сесії " + 
					"завершилося з помилкою: " + 
					"Розшифровані дані не співпадають";
				return false;
			}
			
			euSign.SessionClose(userSession);
			userSession = null;
			euSign.SessionClose(serverSession);
			serverSession = null;

			userSession = euSign.ClientDynamicKeySessionCreate(3600, ownCert);
			serverSession = euSign.ServerDynamicKeySessionCreate(
				3600, userSession.GetData());
				
			if (!_testEncryption(userSession, serverSession, string) ||
				!_testEncryption(userSession, serverSession, array)) {
				resultText.value += "Тестування функцій захищеної сесії " + 
					"завершилося з помилкою: " + 
					"Розшифровані дані не співпадають";
				return false;
			}
			
			resultText.value += "Тестування функцій захищеної сесії " + 
				"завершилося успішно\r\n";
		} catch (e) {
			resultText.value += "Тестування функцій захищеної сесії " + 
				"завершилося з помилкою: " + e.toString();
			return false;
		} finally {
			try {
				if (userSession != null)
					euSign.SessionClose(userSession);
				if (serverSession != null)
					euSign.SessionClose(serverSession);
			} catch (e) {
			}
		}
		
		return true;
	},
//-----------------------------------------------------------------------------
	loadFilesFromLocalStorage: function(localStorageFolder, loadFunc) {
		if (!utils.IsStorageSupported())
			euSign.RaiseError(EU_ERROR_NOT_SUPPORTED);
	
		if (utils.IsFolderExists(localStorageFolder)) {
			var files = utils.GetFiles(localStorageFolder);
			for (var i = 0; i < files.length; i++) {
				var file = utils.ReadFile(
					localStorageFolder, files[i]);
				loadFunc(files[i], file);
			}
			return files;
		}
		else {
			utils.CreateFolder(localStorageFolder);
			return null;
		}
	},
	saveFileToModuleFileStorage: function (fileName, fileData) {
		var filesListName = null;
		try {
			var array = new Uint8Array(fileData);
			var folderName = null;
			
			if (fileName.indexOf(".cer") >= 0) {
				filesListName = 'SelectedCertsList';
				euSign.SaveCertificate(array);
				folderName = euSignTest.CertsLocalStorageName;
			} else if (fileName.indexOf(".p7b") >= 0) {
				euSign.SaveCertificates(array);
				folderName = euSignTest.CertsLocalStorageName;
			} else if (fileName.indexOf(".crl") >= 0) {
				filesListName = 'SelectedCRLsList';
				try {
					euSign.SaveCRL(true, array);
				} catch (e) {
					euSign.SaveCRL(false, array);
				}
				folderName = euSignTest.CRLsLocalStorageName;
			}

			if (folderName != null && utils.IsStorageSupported()) {
				utils.WriteFile(folderName, fileName, array);
			}
		} catch (e) {
			if (filesListName != null) {
				var filesList = document.getElementById(
					filesListName).getElementsByTagName("li");
				var filesNames = [];
				for (var i = 0; i < filesList.length; i++) {
					var fileNameInList = filesList[i].innerText;
					if (fileNameInList == fileName)
						fileNameInList += ' (Не завантажено)'
						
					filesNames.push(fileNameInList);
				}

				euSignTest.setItemsToList(
					filesListName, filesNames);
			}
			alert(e);
		}
		
		euSignTest.updateCertList();
	},
	isCertificateExtension: function(fileName) {
		if ((fileName.indexOf(".cer") >= 0) || 
				(fileName.indexOf(".p7b") >= 0))
			return true;
		return false;
	},
	isCRLExtension: function(fileName) {
		if ((fileName.indexOf(".crl") >= 0))
			return true;
		return false;
	},
//-----------------------------------------------------------------------------
	mainMenuItemClicked: function(tab, pageId) {
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
	},
	useInternalSignCheckBoxClick: function() {
		var intSignCheckbox = 
			document.getElementById("InternalSignCheckbox");
		var addCertToIntSignCheckbox = 
			document.getElementById("AddCertToInternalSignCheckbox"); 
		var signHashCheckbox =
			document.getElementById("SignHashCheckbox");
		var verifiedDataText = 
			document.getElementById("VerifiedDataText");
		var fileWithSignSelectFile = 
			document.getElementById("FileWithSign");
		
		if (intSignCheckbox.checked) {
			addCertToIntSignCheckbox.disabled = '';
			verifiedDataText.disabled = '';
			signHashCheckbox.disabled = 'disabled';
			fileWithSignSelectFile.disabled = 'disabled';
		} else {
			addCertToIntSignCheckbox.disabled = 'disabled';
			verifiedDataText.disabled = 'disabled';
			signHashCheckbox.disabled = '';
			fileWithSignSelectFile.disabled = '';
		}
	},
	signHashCheckBoxClick: function() {
		var intSignCheckbox = 
			document.getElementById("InternalSignCheckbox");
		var signHashCheckbox =
			document.getElementById("SignHashCheckbox");
		if (signHashCheckbox.checked) {
			intSignCheckbox.disabled = 'disabled';
		} else {
			intSignCheckbox.disabled = '';
		}
	},
	DSCAdESTypeChanged: function() {
		var signType = CAdESTypes[
			document.getElementById('DSCAdESTypeSelect').selectedIndex];
		try {
			euSign.SetRuntimeParameter(EU_SIGN_TYPE_PARAMETER, signType);
		} catch (e) {
			alert(e);
		}

		document.getElementById('SignAddCAsCertificatesCheckbox').disabled = 
			(signType == EU_SIGN_TYPE_CADES_X_LONG) ? '' : 'disabled';
	},
	signAddContentTimestampCheckBoxClick: function() {
		try {
			euSign.SetRuntimeParameter(EU_SIGN_INCLUDE_CONTENT_TIME_STAMP_PARAMETER, 
				document.getElementById('SignAddContentTimestampCheckbox').checked);
		} catch (e) {
			alert(e);
		}
	},
	signAddCAsCertificatesCheckBoxClick: function() {
		try {
			euSign.SetRuntimeParameter(EU_SIGN_INCLUDE_CA_CERTIFICATES_PARAMETER, 
				document.getElementById('SignAddCAsCertificatesCheckbox').checked);
		} catch (e) {
			alert(e);
		}
	},
	privateKeyReaded: function (isReaded) {
		var enabled = '';
		var disabled = 'disabled';
		
		if (!isReaded) {
			enabled = 'disabled';
			disabled = '';
		}

		setStatus('');

		document.getElementById('CAsServersSelect').disabled = disabled;
		setPointerEvents(document.getElementById('PKeySelectFileButton'), !isReaded);
		document.getElementById('PKeyFileName').disabled = disabled;
		document.getElementById('PKCertsSelectZone').hidden = 
				(!isReaded && euSignTest.loadPKCertsFromFile) ? '' : 'hidden';

		document.getElementById('PKeyReadButton').title = 
			isReaded ? 'Стерти' : 'Зчитати';
		document.getElementById('PKeyReadButton').innerHTML = 
			isReaded ? 'Стерти' : 'Зчитати';

		document.getElementById('KeyReadedImage').style.display = isReaded ? 
			"inline" : 'none';

		setPointerEvents(document.getElementById('PKeyShowOwnerInfoButton'), isReaded);
		setPointerEvents(document.getElementById('PKeyShowCertsInfoButton'), isReaded);
		setPointerEvents(document.getElementById('PKeySaveInfo'), isReaded);
		setPointerEvents(document.getElementById('PKeyBlockOwnCertButton'), isReaded);
		setPointerEvents(document.getElementById('PKeyRevokeOwnCertButton'), isReaded);
		document.getElementById('PKeyPassword').disabled = disabled;
		if (!isReaded) {
			document.getElementById('PKeyPassword').value = '';
			document.getElementById('PKeyPassword').disabled = 'disabled';
			document.getElementById('PKeyFileName').value = '';
			document.getElementById('PKeyFileInput').value = null;
			setPointerEvents(document.getElementById('PKeyReadButton'), false);
		}

		setPointerEvents(document.getElementById('SignDataButton'), isReaded);
		document.getElementById('FileToSign').disabled = enabled;
		setPointerEvents(document.getElementById('SignFileButton'), isReaded);
		setPointerEvents(document.getElementById('TestSignButton'), isReaded);
		document.getElementById('TestSignText').disabled = enabled;

		document.getElementById('RecipientsCertsFiles').disabled = enabled;
		document.getElementById('DataToEnvelopTextEdit').disabled = enabled;
		setPointerEvents(document.getElementById('EnvelopDataButton'), isReaded);
		document.getElementById('EnvelopedDataText').disabled = enabled;
		setPointerEvents(document.getElementById('DevelopedDataButton'), isReaded);
		document.getElementById('DevelopedDataText').disabled = enabled;
		setPointerEvents(document.getElementById('TestEnvelopButton'), isReaded);
		document.getElementById('TestEnvelopText').disabled = enabled;

		document.getElementById('EnvelopFiles').disabled = enabled;

		document.getElementById('RecipientsCertsFiles').value = [];
	},
	setSelectPKCertificatesEvents: function() {
		document.getElementById('ChoosePKCertsInput').addEventListener(
			'change',  function(evt) {
				if (evt.target.files.length <= 0) {
					euSignTest.clearPrivateKeyCertificatesList();
				} else {
					euSignTest.privateKeyCerts = evt.target.files;
					euSignTest.setFileItemsToList("SelectedPKCertsList", 
						evt.target.files);
				}
			}, false);
		
		document.getElementById('PKCertsDropZone').addEventListener(
			'dragover', function(evt) {
				evt.stopPropagation();
				evt.preventDefault();
				evt.dataTransfer.dropEffect = 'copy';
			}, false);

		document.getElementById('PKCertsDropZone').addEventListener(
			'drop', function(evt) {
				evt.stopPropagation();
				evt.preventDefault();

				if (evt.dataTransfer.files.length <= 0) {
					euSignTest.clearPrivateKeyCertificatesList();
				} else {
					euSignTest.privateKeyCerts = evt.dataTransfer.files;
					euSignTest.setFileItemsToList("SelectedPKCertsList", 
						evt.dataTransfer.files);
				}
			}, false);
	},
	clearPrivateKeyCertificatesList: function() {
		euSignTest.privateKeyCerts = null;
		document.getElementById('ChoosePKCertsInput').value = null;
		document.getElementById('SelectedPKCertsList').innerHTML = 
			"Сертифікати відкритого ключа не обрано" + '<br>';
	},
	setItemsToList: function(listId, items) {
		var output = [];
		for (var i = 0, item; item = items[i]; i++) {
			output.push('<li><strong>', item, '</strong></li>');
		}

		document.getElementById(listId).innerHTML = 
			'<ul>' + output.join('') + '</ul>';
	},
	setFileItemsToList: function(listId, items) {
		var output = [];
		for (var i = 0, item; item = items[i]; i++) {
			output.push('<li><strong>', item.name, '</strong></li>');
		}

		document.getElementById(listId).innerHTML = 
			'<ul>' + output.join('') + '</ul>';
	}
});

//=============================================================================

var euSignTest = EUSignCPTest();
var euSign = EUSignCP();
var utils = Utils(euSign);

//=============================================================================

function setPointerEvents(element, enable) {
	element.style.pointerEvents = enable ? "auto" : "none";
}

function setStatus(message) {
	if (message != '')
		message = '(' + message + '...)';
	document.getElementById('status').innerHTML = message;
}

function saveFile(fileName, array) {
	var blob = new Blob([array], {type:"application/octet-stream"});
	saveAs(blob, fileName);
}

function pageLoaded() {
	document.getElementById('CertsAndCRLsFiles').addEventListener(
		'change', euSignTest.chooseCertsAndCRLs, false);
	document.getElementById('PKeyFileInput').addEventListener(
		'change', euSignTest.selectPrivateKeyFile, false);
	document.getElementById('RecipientsCertsFiles').addEventListener(
		'change', euSignTest.chooseRecepientsCertificates, false);
	document.getElementById('FileToSign').addEventListener(
		'change', euSignTest.chooseFileToSign, false);
	document.getElementById('FileToVerify').addEventListener(
		'change', euSignTest.chooseFileToVerify, false);
	document.getElementById('FileWithSign').addEventListener(
		'change', euSignTest.chooseFileToVerify, false);
	document.getElementById('EnvelopFiles').addEventListener(
		'change', euSignTest.chooseEnvelopFile, false);

	var appendMaxFileSizeLimit = function(textLabelId) {
		var str = document.getElementById(textLabelId).innerHTML;
		str = str.substring(0, str.length - 1) + 
			" (не більше " + EU_MAX_DATA_SIZE_MB + " МБ):";
		document.getElementById(textLabelId).innerHTML = str;
	}

	appendMaxFileSizeLimit('ChooseFileForSignTextLabel');
	appendMaxFileSizeLimit('ChooseFileForVerifyTextLabel');
	appendMaxFileSizeLimit('ChooseFileForEnvelopTextLabel');
}

function EUSignCPModuleInitialized(isInitialized) {
	if (isInitialized)
		euSignTest.initialize();
	else 
		alert("Криптографічну бібліотеку не ініціалізовано");
}

//=============================================================================