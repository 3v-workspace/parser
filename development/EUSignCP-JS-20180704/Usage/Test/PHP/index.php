﻿<?php
$token = "";
$token = date('His').rand(100,10000);
$cur_Date = date('Y-m-d');
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
	<title>ІІТ Користувач ЦСК-1. Бібліотека підпису (java-скрипт)</title>
	<meta name="AUTHOR" content="Copyright JSC IIT. All rights reserved.">
	<meta content="text/html; charset=utf-8" http-equiv="Content-Type">
	<meta name="KEYWORDS" content="<?php echo $sWebMetaK; ?>">
	<meta name="DESCRIPTION" content="<?php echo $sWebMetaD; ?>">
	<meta http-equiv="pragma" content="no-cache">
	<meta name="robots" content="index, follow">
	<meta name="viewport" content="width=device-width">
	<?php
    echo '<link rel="stylesheet" type="text/css" href="Styles.css?'.$token.'">';
	?>
	<script type="text/javascript" src="JS/common.js"></script>
	<script type="text/JavaScript" src="JS/euutils.js"></script>
	<script type="text/JavaScript" src="JS/euscpt.js"></script>
	<script type="text/JavaScript" src="JS/euscpm.js"></script>
	<script async type="text/javascript" src="JS/euscp.js"></script>
	<script type="text/JavaScript" src="JS/euscptest.js"></script>
	<script type="text/javascript" src="JS/qr/qrcodedecode.js"></script>
	<script type="text/javascript" src="JS/qr/reedsolomon.js"></script>
	<script type="text/javascript" src="JS/fs/Blob.min.js"></script>
	<script type="text/javascript" src="JS/fs/FileSaver.js"></script>
	<script type="text/JavaScript">
		function onBodyLoad() {
			MM_preloadImages('Images/ButtonHover.png', 'Images/ButtonHover.png');
			pageLoaded();
		}
	</script>
</head>
<body onload="onBodyLoad();">
<div id="iit">
<table border="0" cellspacing="0" cellpadding="0" align="center" width="100%">
<tr style="height:128px">
	<td valign="top" align="left" colspan="2">
	<table border="0" cellspacing="0" cellpadding="0" align="center" width="100%">
	<tr><td valign="top" align="left" width="104">
		<img src="Images/Keys.png" height="122px">
	</td>
	<td valign="top" align="left">
		<table border="0" cellspacing="0" cellpadding="0" align="center" width="100%">
		<tr><td width="100%" valign="top" align="left" style="padding:10px 0px 0px 0px;" class="header35">
			<b>ІІТ Користувач ЦСК-1. Бібліотека підпису (java-скрипт)</b>
		</td></tr>
		<tr><td width="100%" valign="top" align="left" class="header12"><br />
			За допомогою форми можна підписувати дані з форми (текстові дані),
			або файли, що знаходяться на файловій системі тощо<br /><br />
		</td></tr>
		</table>
	</td>
	</tr></table></td>
</tr>

<!--------------------------------------------------------------------------------------------------------------->

<tr style="height:100%">
	<td valign="top" align="center" style="padding:0px 0px 0px 0px" align="center">
	<div id="iit_line1">
		<table border="0" cellspacing="0" cellpadding="0" align="center">
		<tr>
			<td class="headerwhite1" colspan="2" valign="top">Основні функції
				<span id="status" style="font-weight: normal;">(завантаження...)</span>
				<progress value="0" max="100" id="progress" hidden=1></progress>
				<img src="Images/Key.png" id="KeyReadedImage" style="width:24px; height:24px;display:none" align="right"></img>
			</td>
		</tr>
		<tr>
			<td style="width:185px;padding:20px 0px 0px;" valign="top">
				<div id="mainMenu" class="MainPageMenuBlock">
				<ul id="MainPageMenu" class="MainPageMenuTabs">
					<li id="MainPageMenuPKey" class="MainPageMenuSelectedTab" onclick="euSignTest.mainMenuItemClicked(this, 'MainPageMenuPKeyPage'); return false;">
						<a href="#MainPageMenuPKey">Особистий ключ</a>
					</li>
					<li id="MainPageMenuGenPKey" class="MainPageMenuTab" onclick="euSignTest.mainMenuItemClicked(this, 'MainPageMenuGenPKeyPage'); return false;">
						<a href="#MainPageMenuGenPKey">Генерація ос. ключа</a>
					</li>
					<li id="MainPageMenuCertsAndCRLs" class="MainPageMenuTab" onclick="euSignTest.mainMenuItemClicked(this, 'MainPageMenuCertsAndCRLsPage'); return false;">
						<a href="#MainPageMenuCertsAndCRLs">Сертифікати та СВС</a>
					</li>
					<li id="MainPageMenuSign" class="MainPageMenuTab" onclick="euSignTest.mainMenuItemClicked(this, 'MainPageMenuSignPage'); return false;">
						<a href="#MainPageMenuSign">Підпис</a>
					</li>
					<li id="MainPageMenuEnvelop" class="MainPageMenuTab" onclick="euSignTest.mainMenuItemClicked(this, 'MainPageMenuEnvelopPage'); return false;">
						<a href="#MainPageMenuEnvelop">Шифрування</a>
					</li>
				</ul>
				</div>
			</td>
			<td style="padding:20px 0px 0px;" valign="top">
			<div class="MainPageMenuContent">
				<div id="MainPageMenuPKeyPage" class="MainPageMenuPanelSelected">
					<div class="TextHeaderH3">Встановлення особистого ключа</div>
					<div class="SeparatorLine"> </div>
					<div class="SmoothGradient"></div>
					<div id="PKeySelectPanel">
						<div class="TextImageContainer">
							<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
							<span class="TextInTextImageContainer">Оберіть ЦСК</span>
						</div>
						<div class="SubMenuContent">
							<div class="styled-select1" style="width: 100%">
								<select id="CAsServersSelect" style="width: 100%">

								</select>
							</div>
						</div>
						<div class="SeparatorLine"> </div>
						<div class="SmoothGradient"></div>
						<div class="TextImageContainer">
							<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
							<span class="TextInTextImageContainer" id="ChoosePKFileText">Оберіть файл з особистим ключем (зазвичай з ім'ям Key-6.dat) та вкажіть пароль захисту</span>
						</div>
						<div class="SubMenuContent">
							<div class="TextLabel">Особистий ключ:</div>
							<div>
								<input id="PKeyFileName" type="text" class="PKeyFileNameEdit" readonly="true" onclick="document.getElementById('PKeyFileInput').click();" style="width:200px;float:left;margin-top:3px">
								<div id="buttonitem" style="margin-left:0px;padding-left:10px">
									<a id="PKeySelectFileButton" style="cursor:pointer; pointer-events:auto;" href="javascript:void(0);" title="Обрати" onclick="document.getElementById('PKeyFileInput').click();">Обрати</a>
									<input id="PKeyFileInput" type="file" multiple="false"></input>
								</div>
							</div>
							<div class="TextLabel">Пароль захисту ключа:</div>
							<div>
								<input id="PKeyPassword" type="password" class="PasswordEdit" disabled="disabled" style="width:200px;float:left;margin-top:3px">
								<div id="buttonitem" style="margin-left:0px;padding-left:10px">
									<a id="PKeyReadButton" style="cursor:pointer;" href="javascript:void(0);" title="Зчитати" onclick="euSignTest.readPrivateKeyButtonClick()">Зчитати</a>
								</div>
							</div>
							<div id="PKCertsSelectZone" hidden=1>
								<div class="FileDropZone" id="PKCertsDropZone">
									<div class="FileDropZoneBorder">
										<div class="FileDropZoneMessage">
											<span>Перетягніть або </span><br><br>
											<div id="buttonitem" style="float:center; display:inline-block;" >
												<a id="ChoosePKCertsButton" style="cursor:pointer; pointer-events:auto;" href="javascript:void(0);" title="Оберіть" onclick="document.getElementById('ChoosePKCertsInput').click();">Оберіть</a>
												<input id="ChoosePKCertsInput" type="file" multiple="true"></input>
											</div>
											<br><br>
											<span>файл(и) з сертифікатом(ами)</span><br><br>
											<span>(зазвичай, з розширенням cer, crt)</span>
										</div>
									</div>
								</div>
								<br>
								<div class="TextLabel">Обрані сертифікати:</div>
								<output id="SelectedPKCertsList" style="padding-left:1em;"></output>
								<br><br>
							</div>
						</div>
						<div class="SeparatorLine"> </div>
						<div class="SmoothGradient"></div>
						<div class="TextImageContainer">
							<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
							<span class="TextInTextImageContainer">Інформація про особистий ключ</span>
						</div>
						<div class="SubMenuContent">
							<div id="buttonitem" style="width:208px">
								<a id="PKeyShowOwnerInfoButton" style="cursor:pointer;" href="javascript:void(0);" title="Переглянути про власника"onclick="euSignTest.showOwnerInfo()">Переглянути про власника</a>
							</div>
							<div id="buttonitem" style="width:208px">
								<a id="PKeyShowCertsInfoButton" style="cursor:pointer;" href="javascript:void(0);" title="Переглянути сертифікати"onclick="euSignTest.showOwnCertificates()">Переглянути сертифікати</a>
							</div>
							<div id="buttonitem" style="width:208px">
								<a id="PKeySaveInfo" style="cursor:pointer;" href="javascript:void(0);" title="Зберегти інф. про ключ"onclick="euSignTest.savePKeyInfo()">Зберегти інф. про ключ</a>
							</div>
						</div>
						<div class="SeparatorLine"> </div>
						<div class="SmoothGradient"></div>
						<div class="TextImageContainer">
							<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
							<span class="TextInTextImageContainer">Блокування сертифікатів ос. ключа</span>
						</div>
						<div class="SubMenuContent">
							<div id="buttonitem" style="width:208px">
								<a id="PKeyBlockOwnCertButton" style="cursor:pointer;" href="javascript:void(0);" title="Заблокувати власні сертифікати"onclick="euSignTest.blockOwnCertificates()">Заблокувати сертифікати</a>
							</div>
						</div>
						<div class="SeparatorLine"> </div>
						<div class="SmoothGradient"></div>
						<div class="TextImageContainer">
							<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
							<span class="TextInTextImageContainer">Скасування сертифікатів ос. ключа</span>
						</div>
						<div class="SubMenuContent">
							<div class="TextLabel">Причина скасування:</div><br>
							<div class="styled-select1">
								<select id="PKeyRevokationReasonSelect">
									<option value="0">Не визначена</option>
									<option value="1">Компрометація ос. ключа</option>
									<option value="2" selected>Формування нового</option>
								</select>
							</div>
							<br>
							<div id="buttonitem" style="width:208px">
								<a id="PKeyRevokeOwnCertButton" style="cursor:pointer;" href="javascript:void(0);" title="Скасувати власні сертифікати"onclick="euSignTest.revokeOwnCertificates()">Скасувати сертифікати</a>
							</div>
						</div>
					</div>
					<div class="SeparatorLine"> </div>
					<div class="SmoothGradient"></div>
				</div>
				<div id="MainPageMenuGenPKeyPage" class="MainPageMenuPanel">
					<div class="TextHeaderH3">Генерація особистого ключа</div>
					<div class="SeparatorLine"> </div>
					<div class="SmoothGradient"></div>
					<div id="PKeyGeneratePanel">
						<div class="TextImageContainer">
							<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
							<span class="TextInTextImageContainer">Оберіть параметри генерації ключової пари</span>
						</div>
						<div class="SubMenuContent" id="PrivKeyTypeParams">
							<input type="radio" name='KeysTypeRadioBtn' id='ChooseKeysUARadioBtn' checked onclick="euSignTest.changePrivKeyType()"> для державних алгоритмів і протоколів<br>
							<input type="radio" name='KeysTypeRadioBtn' id='ChooseKeysRSARadioBtn' onclick="euSignTest.changePrivKeyType()"> для міжнародних алгоритмів і протоколів<br>
							<input type="radio" name='KeysTypeRadioBtn' id='ChooseKeysUARSARadioBtn' onclick="euSignTest.changePrivKeyType()"> для державних та міжнародних алгоритмів і протоколів<br><br>
							<input type="checkbox" id="PKPFXContainerCheckbox" class="Checkbox" />Використовувати контейнер особистих ключів та сертифікатів<br>
						</div>
						<div id="UAPrivKeyParams">
							<div class="SeparatorLine"></div>
							<div class="SmoothGradient"></div>
							<div class="TextImageContainer">
								<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
								<span class="TextInTextImageContainer">Параметри ос. ключа для державних алгоритмів та протоколів</span>
							</div>
							<div class="SubMenuContent">
								<div class="TextLabel">Параметри ключа підпису (ДСТУ 4145-2002)</div><br>
								<div class="styled-select1">
									<select id="UAKeySpecSelect">
										<option value="1">мінімальна (191 біт)</option>
										<option value="2" selected>базова (257 біт)</option>
										<option value="3">велика (307 біт)</option>
									</select>
								</div>
								<br>
								<div class="TextLabel">Параметри ключа протоколу розподілу (Д-Г в гр. точок ЕК)</div><br>
								<div class="styled-select1">
									<select id="UAKEPKeySpecSelect">
										<option value="1">базова (257 біт)</option>
										<option value="2" selected>велика (431 біт)</option>
										<option value="3">максимальна (571 біт)</option>
									</select>
								</div>
							</div>
						</div>
						<div  id="InternationalPrivKeyParams" style="display: none">
							<div class="SeparatorLine"> </div>
							<div class="SmoothGradient"></div>
							<div class="TextImageContainer">
								<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
								<span class="TextInTextImageContainer">Параметри ос. ключа для міжнародних алгоритмів та протоколів</span>
							</div>
							<div class="SubMenuContent">
								<div class="TextLabel">Параметри ключа (RSA та SHA)</div><br>
								<div class="styled-select1">
									<select id="InternationalKeySpecSelect">
										<option value="1">мінімальна (1024 біта з SHA-1)</option>
										<option value="2" selected>базова (2048 біт з SHA-256)</option>
										<option value="3">велика (3072 біта з SHA-256)</option>
										<option value="4">максимальна (4096 біт з SHA-256)</option>
									</select>
								</div>
							</div>
						</div>
						<div class="SeparatorLine"> </div>
						<div class="SmoothGradient"></div>
						<div class="TextImageContainer">
							<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
							<span class="TextInTextImageContainer">Пароль захисту особистого ключа</span>
						</div>
						<div class="SubMenuContent">
							<div>
								<input id="PGenKeyPassword" type="password" class="PasswordEdit" style="width:200px;float:left;margin-top:3px">
								<div id="buttonitem" style="margin-left:0px;padding-left:10px">
									<a id="PGenKeyButton" style="cursor:pointer;" href="javascript:void(0);" title="Згенерувати" onclick="euSignTest.generatePK()">Згенерувати</a>
								</div>
							</div>
						</div>
					<div class="SeparatorLine"> </div>
					<div class="SmoothGradient"></div>
					</div>
				</div>
				<div id="MainPageMenuCertsAndCRLsPage" class="MainPageMenuPanel">
					<div class="TextHeaderH3">Встановлення сертифікатів та СВС</div>
					<div class="SeparatorLine"> </div>
					<div class="SmoothGradient"></div>
					<div class="TextImageContainer">
						<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
						<span class="TextInTextImageContainer">Оберіть сертифікати та СВС</span>
					</div>
					<div class="SubMenuContent">
						<input id="CertsAndCRLsFiles" type="file" class="SelectFile" name="files[]" multiple />
					</div>
					<div class="SeparatorLine"> </div>
					<div class="SmoothGradient"></div>
					<div class="TextImageContainer">
						<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
						<span class="TextInTextImageContainer">Обрані сертифікати</span>
					</div>
					<div class="SubMenuContent">
						<output id="SelectedCertsList"></output>
					</div>
					<div class="SeparatorLine"> </div>
					<div class="SmoothGradient"></div>
					<div class="TextImageContainer">
						<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
						<span class="TextInTextImageContainer">Обрані СВС</span>
					</div>
					<div class="SubMenuContent">
						<output id="SelectedCRLsList"></output>
					</div>
					<div class="SeparatorLine"> </div>
					<div class="SmoothGradient"></div>
					<div class="TextImageContainer">
						<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
						<span class="TextInTextImageContainer">Перегляд сертифікатів в сховищі</span>
					</div>
					<div class="SubMenuContent">
						<div class="TextLabel">Тип власників:</div><br>
						<div class="styled-select1">
							<select id="CertTypeSelect" onchange="euSignTest.updateCertList();">
								<option value="0">Всі сертифікати</option>
								<option value="1">Центри сертифікації ключів</option>
								<option value="2">Сервери ЦСК</option>
								<option value="3">CMP-сервери</option>
								<option value="4">OCSP-сервери</option>
								<option value="5">TSP-сервери</option>
								<option value="6" selected>Користувачі ЦСК</option>
								<option value="7">Адміністратори реєстрації</option>
							</select>
						</div>
						<br>
						<div class="TextLabel">Тип сертифіката:</div><br>
						<div class="styled-select1">
							<select id="CertKeyTypeSelect" onchange="euSignTest.updateCertList();">
								<option value="0" selected>Не визначено</option>
								<option value="1">ДСТУ-4145</option>
								<option value="2">RSA</option>
							</select>
						</div>
						<br>
						<div class="TextLabel">Призначення ключів:</div><br>
						<div class="styled-select1">
							<select id="KeyUsageSelect" onchange="euSignTest.updateCertList();">
								<option value="0" selected>Не визначено</option>
								<option value="1">ЕЦП</option>
								<option value="2">Протоколу розподілу</option>
							</select>
						</div>
						<br>
						<output id="StorageCertList"></output>
					</div>
					<div class="SeparatorLine"> </div>
					<div class="SmoothGradient"></div>
				</div>
				<div id="MainPageMenuSignPage" class="MainPageMenuPanel">
					<div class="TextHeaderH3">Підпис/перевірка підпису даних</div>
					<div class="SeparatorLine"> </div>
					<div class="SmoothGradient"></div>
					<div class="TextImageContainer">
						<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
						<span class="TextInTextImageContainer">Параметри підпису</span>
					</div>
					<div class="SubMenuContent">
						<input type="checkbox" id="InternalSignCheckbox" class="Checkbox" onclick="euSignTest.useInternalSignCheckBoxClick()" />Використовувати внутрішній підпис<br> 
						<input type="checkbox" id="AddCertToInternalSignCheckbox" class="Checkbox" disabled="disabled" />Додавати сертифікат до внутрішнього підпису<br> 
						<input type="checkbox" id="SignHashCheckbox" class="Checkbox" onclick="euSignTest.signHashCheckBoxClick()"/>Підписувати геш<br>
						<input type="checkbox" id="GetSignInfoCheckbox" class="Checkbox" checked="true" />Отримувати інформацію про підпис<br><br>
						<div class="TextLabel">Алгоритм підпису:</div><br>
						<div class="styled-select1">
							<select id="DSAlgTypeSelect">
								<option value="1" selected>ДСТУ-4145</option>
								<option value="2">RSA</option>
							</select>
						</div>
						<br>
						<div class="TextLabel">Формат підпису:</div><br>
						<div class="styled-select1">
							<select id="DSCAdESTypeSelect" onchange="euSignTest.DSCAdESTypeChanged()">
								<option value="0" selected>базовий</option>
								<option value="1">з позначкою часу від ЕЦП</option>
								<option value="2">з посиланням на повні дані для перевірки</option>
								<option value="3">з повними даними для перевірки</option>
							</select>
						</div>
						<br>
						<input type="checkbox" id="SignAddContentTimestampCheckbox" class="Checkbox" checked="true" onclick="euSignTest.signAddContentTimestampCheckBoxClick()"/>Додавати позначку часу від даних<br>
						<input type="checkbox" id="SignAddCAsCertificatesCheckbox" class="Checkbox" checked="true" onclick="euSignTest.signAddCAsCertificatesCheckBoxClick()" disabled="disabled"/>Додавати повні дані для перевірки<br>
					</div>
					<div class="SeparatorLine"> </div>
					<div class="SmoothGradient"></div>
					<div class="TextImageContainer">
						<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
						<span class="TextInTextImageContainer">Підпис текстових даних</span>
					</div>
					<div class="SubMenuContent">
						<div class="TextLabel">Текстові дані:</div>
						<input id="DataToSignTextEdit" type="edit" class="TextEdit"><br>
						<div id="buttonitem" style="float:left;">
							<a id="SignDataButton" style="cursor:pointer;" href="javascript:void(0);" title="Підписати" onclick="euSignTest.signData()">Підписати</a>
						</div>
						<div id="buttonitem" style="padding-left:10px;">
							<a id="VerifyDataButton" style="cursor:pointer;" href="javascript:void(0);" title="Перевірити" onclick="euSignTest.verifyData()">Перевірити</a>
						</div>
						<br>
						<div class="TextLabel">Підпис/Підписані дані:</div>
						<textarea id="SignedDataText" class="TextArea"></textarea><br>
						<br>
						<div class="TextLabel">Перевірені дані:</div>
						<textarea id="VerifiedDataText" class="TextArea" disabled="disabled"></textarea>
					</div>
					<div class="SeparatorLine"> </div>
					<div class="SmoothGradient"></div>
					<div class="TextImageContainer">
						<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
						<span class="TextInTextImageContainer">Підпис файлів</span>
					</div>
					<div class="SubMenuContent">
						<div class="TextLabel" id="ChooseFileForSignTextLabel">Оберіть файл для підпису:</div><br>
						<input id="FileToSign" type="file" class="SelectFile" name="files[]" disabled="disabled" style="margin-bottom:1em;"/><br>
					</div>
					<div class="SubMenuContent">
						<div id="buttonitem">
							<a id="SignFileButton" style="cursor:pointer;" href="javascript:void(0);" title="Підписати" onclick="euSignTest.signFile()">Підписати</a>
						</div>
					</div>

					<div class="SeparatorLine"> </div>
					<div class="SmoothGradient"></div>
					<div class="TextImageContainer">
						<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
						<span class="TextInTextImageContainer">Перевірка підпису файлів</span>
					</div>
					<div class="SubMenuContent">
						<div class="TextLabel" id="ChooseFileForVerifyTextLabel">Оберіть файл для перевірки:</div><br>
						<input id="FileToVerify" type="file" class="SelectFile" name="files[]" style="margin-bottom:1em;"/><br>
						<div class="TextLabel" id="ChooseFileWithSignTextLabel">Оберіть файл з підписом:</div><br>
						<input id="FileWithSign" type="file" class="SelectFile" name="files[]" style="margin-bottom:1em;"/><br>
					</div>
					<div class="SubMenuContent">
						<div id="buttonitem">
							<a id="VerifyFileButton" style="cursor:pointer;" href="javascript:void(0);" title="Перевірити" onclick="euSignTest.verifyFile()">Перевірити</a>
						</div>
					</div>
					<div class="SeparatorLine"> </div>
					<div class="SmoothGradient"></div>
					<div class="TextImageContainer">
						<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
						<span class="TextInTextImageContainer">Тестування функцій підпису</span>
					</div>
					<div class="SubMenuContent">
						<div id="buttonitem">
							<a id="TestSignButton" style="cursor:pointer;" href="javascript:void(0);" title="Тест" onclick="euSignTest.testSignature()">Тест</a>
						</div>
						<br>
						<textarea id="TestSignText" class="TextArea" disabled="disabled"></textarea>
					</div>
					<div class="SeparatorLine"> </div>
					<div class="SmoothGradient"></div>
				</div>
				<div id="MainPageMenuEnvelopPage" class="MainPageMenuPanel">
					<div class="TextHeaderH3">Зашифрування/розшифрування даних</div>
					<div class="SeparatorLine"> </div>
					<div class="SmoothGradient"></div>
					<div class="TextImageContainer">
						<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
						<span class="TextInTextImageContainer">Параметри шифрування</span>
					</div>
					<div class="SubMenuContent">
						<input type="checkbox" id="AddSignCheckbox" class="Checkbox" />Додавати підпис<br><br>
						<div class="TextLabel">Алгоритм протоколу розподілу ключів:</div><br>
						<div class="styled-select1">
							<select id="KEPAlgTypeSelect">
								<option value="1" selected>ДСТУ-4145</option>
								<option value="4">RSA (TDEA)</option>
								<option value="7">RSA (AES)</option>
							</select>
						</div>	
					</div>
					<div class="SeparatorLine"> </div>
					<div class="SmoothGradient"></div>
					<div class="TextImageContainer">
						<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
						<span class="TextInTextImageContainer">Оберіть сертифікати користувачів отримувачів</span>
					</div>
					<div class="SubMenuContent">
						<input id="RecipientsCertsFiles" type="file" class="SelectFile" name="files[]" multiple disabled="disabled" style="margin-bottom:1em;"/><br>
					</div>
					<div class="TextImageContainer">
						<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
						<span class="TextInTextImageContainer">Обрані сертифікати</span>
					</div>
					<div class="SubMenuContent">
						<output id="SelectedRecipientsCertsList">Не обрано жодного сертифіката</output>
					</div>
					<div class="SeparatorLine"> </div>
					<div class="SmoothGradient"></div>
					<div class="TextImageContainer">
						<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
						<span class="TextInTextImageContainer">Шифрування текстових даних</span>
					</div>
					<div class="SubMenuContent">
						<div class="TextLabel">Текстові дані:</div>
						<input id="DataToEnvelopTextEdit" type="edit" class="TextEdit">
						<div id="buttonitem">
							<a id="EnvelopDataButton" style="cursor:pointer;" href="javascript:void(0);" title="Зашифрувати" onclick="euSignTest.envelopData()">Зашифрувати</a>
						</div>
						<br>
						<div class="TextLabel">Зашифровані дані:</div>
						<textarea id="EnvelopedDataText" class="TextArea"></textarea><br>
						<br>
						<div id="buttonitem">
							<a id="DevelopedDataButton" style="cursor:pointer;" href="javascript:void(0);" title="Розшифрувати" onclick="euSignTest.developData()">Розшифрувати</a>
						</div>
						<br>
						<div class="TextLabel">Розшифровані дані:</div>
						<textarea id="DevelopedDataText" class="TextArea" type="button"></textarea>
					</div>
					<div class="SeparatorLine"> </div>
					<div class="SmoothGradient"></div>
					<div class="TextImageContainer">
						<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
						<span class="TextInTextImageContainer">Шифрування файлів</span>
					</div>
					<div class="SubMenuContent">
						<div class="TextLabel" id="ChooseFileForEnvelopTextLabel">Оберіть файл для зашифрування/розшифрування:</div><br>
						<input id="EnvelopFiles" type="file" class="SelectFile" name="files[]" multiple disabled="disabled" style="margin-bottom:1em;"/><br>
					</div>
					<div class="SubMenuContent">
						<div id="buttonitem" style="float:left;">
							<a id="EnvelopFileButton" style="cursor:pointer;" href="javascript:void(0);" title="Зашифрувати" onclick="euSignTest.envelopFile()">Зашифрувати</a>
						</div>
						<div id="buttonitem" style="padding-left:10px;">
							<a id="DevelopedFileButton" style="cursor:pointer;" href="javascript:void(0);" title="Розшифрувати" onclick="euSignTest.developFile()">Розшифрувати</a>
						</div>
					</div>
					<div class="SeparatorLine"> </div>
					<div class="SmoothGradient"></div>
					<div class="TextImageContainer">
						<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
						<span class="TextInTextImageContainer">Тестування функцій шифрування</span>
					</div>
					<div class="SubMenuContent">
						<div id="buttonitem">
							<a id="TestEnvelopButton" style="cursor:pointer;" href="javascript:void(0);" title="Тест" onclick="euSignTest.testEnvelop()">Тест</a>
						</div>
						<br>
						<textarea id="TestEnvelopText" class="TextArea" disabled="disabled"></textarea>
					</div>
					<div class="SeparatorLine"> </div>
					<div class="SmoothGradient"></div>
				</div>
			</td>
		</tr>
		</table>
	</div>
	</td>
</tr>
</table>
</div>

<!--------------------------------------------------------------------------------------------------------------->

<div id="iit_background">
	<div id="iit_gradient_line1"></div>
	<div id="iit_gradient_shadow_line1"></div>
</div>

<!--------------------------------------------------------------------------------------------------------------->

</body>
</html>