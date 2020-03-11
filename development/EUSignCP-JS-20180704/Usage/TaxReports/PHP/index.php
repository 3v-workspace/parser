<?php
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
	<script type="text/JavaScript" src="JS/FileSaver.js"></script>
	<script type="text/JavaScript" src="JS/eusign/eusign.types.js"></script>
	<script type="text/JavaScript" src="JS/eusign/euscpt.js"></script>
	<script type="text/JavaScript" src="JS/eusign/eusign.js"></script>
	<script type="text/JavaScript" src="JS/main.gui.js"></script>
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
			За допомогою форми можна захищати звіти та переглядати квитанції отримані з ДФС<br /><br />
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
					<li id="MainPageMenuPKeys" class="MainPageMenuSelectedTab" onclick="mainMenuItemClicked(this, 'MainPageMenuPKeysPage'); return false;">
						<a href="#MainPageMenuPKeys">Особисті ключі</a>
					</li>
					<li id="MainPageMenuProtectReports" class="MainPageMenuTab" onclick="mainMenuItemClicked(this, 'MainPageMenuProtectReportsPage'); return false;">
						<a href="#MainPageMenuProtectReports">Захист звітів</a>
					</li>
					<li id="MainPageMenuUnprotectReceipts" class="MainPageMenuTab" onclick="mainMenuItemClicked(this, 'MainPageMenuUnprotectReceiptsPage'); return false;">
						<a href="#MainPageMenuUnprotectReceipts">Відкриття квитанцій</a>
					</li>
				</ul>
				</div>
			</td>
			<td style="padding:20px 0px 0px;" valign="top">
			<div class="MainPageMenuContent">
				<div id="MainPageMenuPKeysPage" class="MainPageMenuPanelSelected">
					<div class="TextHeaderH3">Особисті ключі</div>
					<div class="SeparatorLine"> </div>
					<div class="SmoothGradient"></div>
					<div id="ProtectReportPanel">
						<div class="TextImageContainer">
							<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
							<span class="TextInTextImageContainer">Оберіть ЦСК</span>
						</div>
						<div class="SubMenuContent">
							<div class="styled-select1" style="width: 100%">
								<select id="CAsServersSelect" style="width: 100%" onchange="changeCAServer(this)">

								</select>
							</div>
						</div>
						<div class="SeparatorLine"> </div>
						<div class="SmoothGradient"></div>
						<div class="TextImageContainer">
							<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
							<span class="TextInTextImageContainer" id="ChoosePKFileText">Встановіть необхідні файли з особистими ключами бухгалтера, директора та печатки (зазвичай з ім'ям Key-6.dat)</span>
						</div>
						<div class="SubMenuContent">
							<input type="checkbox" id="UseAccountantCheckbox" class="Checkbox" onclick="usePKeyCheckboxClicked(this)" />Бухгалтер<br> 
							<div id="AccountantPKeyPanel" style="padding-left: 18px;" hidden="hidden">
								<br>
								<div class="TextLabel">Особистий ключ:</div>
								<div>
									<input id="AccountantPKeyFileName" type="text" class="FileNameEdit" readonly="true" onclick="document.getElementById('AccountantPKeyFileInput').click();">
									<div id="buttonitem" style="margin-left:0px;padding-left:10px">
										<a id="AccountantPKeySelectFileButton" style="cursor:pointer; pointer-events:auto;" href="javascript:void(0);" title="Обрати" onclick="document.getElementById('AccountantPKeyFileInput').click();">Обрати</a>
										<input id="AccountantPKeyFileInput" type="file" multiple="false" onchange="selectPKeyFile(this, event)"></input>
									</div>
								</div>
								<div class="TextLabel">Пароль захисту ключа:</div>
								<input id="AccountantPKeyPassword" type="password" class="PasswordEdit" disabled="disabled" style="width:200px;margin-top:3px">
								<br><br>
							</div>
							<input type="checkbox" id="UseDirectorCheckbox" class="Checkbox" onclick="usePKeyCheckboxClicked(this)" />Директор<br> 
							<div id="DirectorPKeyPanel" style="padding-left: 18px;" hidden="hidden">
								<br>
								<div class="TextLabel">Особистий ключ:</div>
								<div>
									<input id="DirectorPKeyFileName" type="text" class="FileNameEdit" readonly="true" onclick="document.getElementById('DirectorPKeyFileInput').click();">
									<div id="buttonitem" style="margin-left:0px;padding-left:10px">
										<a id="DirectorPKeySelectFileButton" style="cursor:pointer; pointer-events:auto;" href="javascript:void(0);" title="Обрати" onclick="document.getElementById('DirectorPKeyFileInput').click();">Обрати</a>
										<input id="DirectorPKeyFileInput" type="file" multiple="false" onchange="selectPKeyFile(this, event)"></input>
									</div>
								</div>
								<div class="TextLabel">Пароль захисту ключа:</div>
								<input id="DirectorPKeyPassword" type="password" class="PasswordEdit" disabled="disabled" style="width:200px;margin-top:3px">
								<br><br>
							</div>
							<input type="checkbox" id="UseStampCheckbox" class="Checkbox" onclick="usePKeyCheckboxClicked(this)" />Печатка<br> 
							<div id="StampPKeyPanel" style="padding-left: 18px;" hidden="hidden">
								<br>
								<div class="TextLabel">Особистий ключ:</div>
								<div>
									<input id="StampPKeyFileName" type="text" class="FileNameEdit" readonly="true" onclick="document.getElementById('StampPKeyFileInput').click();">
									<div id="buttonitem" style="margin-left:0px;padding-left:10px">
										<a id="StampPKeySelectFileButton" style="cursor:pointer; pointer-events:auto;" href="javascript:void(0);" title="Обрати" onclick="document.getElementById('StampPKeyFileInput').click();">Обрати</a>
										<input id="StampPKeyFileInput" type="file" multiple="false" onchange="selectPKeyFile(this, event)"></input>
									</div>
								</div>
								<div class="TextLabel">Пароль захисту ключа:</div>
								<input id="StampPKeyPassword" type="password" class="PasswordEdit" disabled="disabled" style="width:200px;margin-top:3px">
								<br><br>
							</div>
							<div id="CertsSelectZone" hidden=1>
								<div class="FileDropZone" id="CertsDropZone">
									<div class="FileDropZoneBorder">
										<div class="FileDropZoneMessage">
											<span>Перетягніть або </span><br><br>
											<div id="buttonitem" style="float:center; display:inline-block;" >
												<a id="ChoooseCertsButton" style="cursor:pointer; pointer-events:auto;" href="javascript:void(0);" title="Оберіть" onclick="document.getElementById('ChooseCertsInput').click();">Оберіть</a>
												<input id="ChooseCertsInput" type="file" multiple="true"></input>
											</div>
											<br><br>
											<span>файл(и) з сертифікатом(ами)</span><br><br>
											<span>(зазвичай, з розширенням cer, crt)</span>
										</div>
									</div>
								</div>
								<br>
								<div class="TextLabel">Обрані сертифікати:</div>
								<output id="SelectedCertsList" style="padding-left:1em;"></output>
								<br><br>
							</div>
						</div>
						<div class="SeparatorLine"> </div>
						<div class="SmoothGradient"></div>
					</div>
				</div>
				<div id="MainPageMenuProtectReportsPage" class="MainPageMenuPanel">
					<div class="TextHeaderH3">Захист звітів</div>
					<div class="SeparatorLine"> </div>
					<div class="SmoothGradient"></div>
					<div id="ProtectReportPanel">
						<div class="TextImageContainer">
							<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
							<span class="TextInTextImageContainer">Вкажіть параметри захисту звітів</span>
						</div>
						<div class="SubMenuContent">
							<div class="TextLabel">Електронна адреса відправника:</div>
							<input id="SenderEMailTextEdit" type="edit" class="TextEdit"><br>
							<div class="TextLabel">Сертифікат одержувача (шлюзу):</div>
							<div>
								<input id="RecipientCertFileName" type="text" class="FileNameEdit" readonly="true" onclick="document.getElementById('RecipientCertFileInput').click();" style="width:218px;">
								<div id="buttonitem" style="margin-left:0px;padding-left:10px">
									<a id="RecipientCertSelectFileButton" style="cursor:pointer; pointer-events:auto;" href="javascript:void(0);" title="Обрати" onclick="document.getElementById('RecipientCertFileInput').click();">Обрати</a>
									<input id="RecipientCertFileInput" type="file" multiple="false" onchange="selectRecipientCertFile(this, event)"></input>
								</div>
							</div>
						</div>
						<div class="SeparatorLine"> </div>
						<div class="SmoothGradient"></div>
						<div class="TextImageContainer">
							<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
							<span class="TextInTextImageContainer">Захист текстових даних</span>
						</div>
						<div class="SubMenuContent">
							<div class="TextLabel">Назва звіту:</div>
							<input id="ReportNameTextEdit" type="edit" class="TextEdit">
							<div class="TextLabel">Текстові дані:</div>
							<div>
								<textarea id="ReportDataText" class="TextArea"></textarea>
							</div>
							<div id="buttonitem" style="margin-top:6px">
								<a id="ProtectReportDataButton" style="cursor:pointer; pointer-events:auto;" href="javascript:void(0);" title="Обробити" onclick="protectReportData()">Обробити</a>
							</div>
							<br>
							<div class="TextLabel">Захищені дані (в форматі BASE64):</div>
							<div>
								<textarea id="ProtectedReportDataText" class="TextArea"></textarea>
							</div>
						</div>
						<div class="SeparatorLine"> </div>
						<div class="SmoothGradient"></div>
						<div class="TextImageContainer">
							<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
							<span class="TextInTextImageContainer">Захист файлів</span>
						</div>
						<div class="SubMenuContent">
							<div class="TextLabel">Вхідний файл:</div>
							<div>
								<input id="ReportFileName" type="text" class="FileNameEdit" readonly="true" onclick="document.getElementById('ReportFileInput').click();" style="width:218px;">
								<div id="buttonitem" style="margin-left:0px;padding-left:10px">
									<a id="ReportSelectFileButton" style="cursor:pointer; pointer-events:auto;" href="javascript:void(0);" title="Обрати" onclick="document.getElementById('ReportFileInput').click();">Обрати</a>
									<input id="ReportFileInput" type="file" multiple="false" onchange="selectReportFile(this, event)"></input>
								</div>
							</div>
							<div class="TextLabel">Вихідний файл:</div>
							<div>
								<input id="ProtectedReportFileName" type="text" class="FileNameEdit" style="width:218px; float:none;">
							</div>
							<div id="buttonitem" style="margin-top:6px;">
								<a id="ProtectReportFileButton" style="cursor:pointer; pointer-events:auto;" href="javascript:void(0);" title="Обробити" onclick="protectReportFile()">Обробити</a>
							</div>
						</div>
						<div class="SeparatorLine"> </div>
						<div class="SmoothGradient"></div>
					</div>
				</div>
				<div id="MainPageMenuUnprotectReceiptsPage" class="MainPageMenuPanel">
					<div class="TextHeaderH3">Відкриття квитанцій</div>
					<div class="SeparatorLine"> </div>
					<div class="SmoothGradient"></div>
					<div id="UnprotectReportPanel">
						<div class="TextImageContainer">
							<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
							<span class="TextInTextImageContainer">Відкриття текстових даних</span>
						</div>
						<div class="SubMenuContent">
							<div class="TextLabel">Захищені дані (в форматі BASE64):</div>
							<div>
								<textarea id="ReceiptDataText" class="TextArea"></textarea>
							</div>
							<div id="buttonitem" style="margin-top:6px">
								<a id="UnprotectReceiptDataButton" style="cursor:pointer; pointer-events:auto;" href="javascript:void(0);" title="Обробити" onclick="unprotectReceiptData()">Обробити</a>
							</div>
							<br>
							<div class="TextLabel">Вихідні дані (в форматі BASE64):</div>
							<div>
								<textarea id="UnprotectedReceiptDataText" class="TextArea"></textarea>
							</div>
						</div>
						<div class="SeparatorLine"> </div>
						<div class="SmoothGradient"></div>
						<div class="TextImageContainer">
							<img class="ImageInTextImageContainer" src="Images/Arrow.png" border="0">
							<span class="TextInTextImageContainer">Відкриття файлів</span>
						</div>
						<div class="SubMenuContent">
							<div class="TextLabel">Вхідний файл:</div>
							<div>
								<input id="ReceiptFileName" type="text" class="FileNameEdit" readonly="true" onclick="document.getElementById('ReceiptFileInput').click();" style="width:218px;">
								<div id="buttonitem" style="margin-left:0px;padding-left:10px">
									<a id="ReceiptSelectFileButton" style="cursor:pointer; pointer-events:auto;" href="javascript:void(0);" title="Обрати" onclick="document.getElementById('ReceiptFileInput').click();">Обрати</a>
									<input id="ReceiptFileInput" type="file" multiple="false" onchange="selectReceiptFile(this, event)"></input>
								</div>
							</div>
							<div class="TextLabel">Вихідний файл:</div>
							<div>
								<input id="UnprotectedReceiptFileName" type="text" class="FileNameEdit" style="width:218px; float:none;">
							</div>
							<div id="buttonitem" style="margin-top:6px">
								<a id="UnprotectReceiptFileButton" style="cursor:pointer; pointer-events:auto;" href="javascript:void(0);" title="Обробити" onclick="unprotectReceiptFile()">Обробити</a>
							</div>
						</div>
						<div class="SeparatorLine"> </div>
						<div class="SmoothGradient"></div>
					</div>
				</div>
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