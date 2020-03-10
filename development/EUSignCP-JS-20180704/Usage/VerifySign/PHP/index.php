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
		echo '<link rel="stylesheet" type="text/css" href="jquery.dataTables.css?'.$token.'">';
		echo '<link rel="stylesheet" type="text/css" href="Styles.css?'.$token.'">';
	?>
	<script type="text/javascript" src="JS/common.js"></script>
	<script type="text/JavaScript" src="JS/jquery/jquery.js"></script>
	<script type="text/JavaScript" src="JS/jquery/jquery.blockUI.js"></script>
	<script type="text/JavaScript" src="JS/jquery/jquery.dataTables.min.js"></script>
	<script type="text/javascript" src="JS/fs/Blob.min.js"></script>
	<script type="text/javascript" src="JS/fs/FileSaver.js"></script>
	<script type="text/JavaScript" src="JS/euverifysign/euverifysign.types.js"></script>
	<script type="text/JavaScript" src="JS/euverifysign/euscpt.js"></script>
	<script type="text/JavaScript" src="JS/euverifysign/euverifysign.js"></script>
	<script type="text/JavaScript" src="JS/main.gui.js"></script>
	<script type="text/JavaScript">
		function onBodyLoad() {
			MM_preloadImages('Images/ButtonHover.png', 'Images/ButtonHover.png', 
				'Images/CertificateProcess.png', 'Images/CertificateWarning.png', 
				'Images/CertificateError.png', 'Images/CertificateCheck.png');
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
		<tr><td width="100%" valign="top" align="left" class="header12"><br/>
			За допомогою форми можна перевіряти підписані файли,
			що знаходяться на файловій системі<br/><br/>
		</td></tr>
		</table>
	</td>
	</tr>
	</table>
	</td>
</tr>

<!--------------------------------------------------------------------------------------------------------------->

<tr style="height:100%">
	<td valign="top" align="center" style="padding:0px 0px 0px 0px" align="center">
	<div id="iit_line1">
		<table border="0" cellspacing="0" cellpadding="0" align="center">
		<tr>
			<td class="headerwhite1" valign="top">Перевірка підпису
				<progress value="0" max="100" id="progress" hidden=1></progress>
			</td>
			<td>
				<img id="LoadingImage" src="Images/LoadingBars.gif">
			</td>
		</tr>
		<tr>
			<td colspan="2" valign="top" style="padding:20px 0px 0px 0px;">
			<div class="MainPageContent" id="MainPageContent">
				<div class="TextHeaderH3">Перевірка підпису файлів</div>
				<div class="SeparatorLine"> </div>
				<div class="SmoothGradient"></div>
				<div class="SubMenuContent" id="ResultMenu">
					<div class="FileDropZone" id="FilesDropZone">
							<div class="FileDropZoneBorder" id="FileDropZoneBorder">
								<div class="FileDropZoneMessage" id="FileDropZoneMessage">
									<span>Перетягніть або </span><br><br>
									<div id="buttonitem" style="float:center; display:inline-block;" >
										<a id="ChooseFilesButton" style="cursor:pointer; pointer-events:auto;" href="javascript:void(0);" title="Оберіть" onclick="$('#ChooseFilesInput').click();">Оберіть</a>
										<input id="ChooseFilesInput" type="file" multiple="true"></input>
									</div>
									<br><br>
									<span>підписані файли для перевірки</span><br><br>
									<span>(зазвичай, з розширенням p7s)</span>
								</div>
							</div>
							<div id="TableContainer" style="display:none;">
								<table id="ResultsTable" class="display" width="100%" cellspacing="0" style="table-layout:fixed;">
									<thead>
										<tr>
											<th> </th>
											<th>Ім'я файлу</th>
											<th>Стан</th>
											<th>Інформація</th>
											<th>Перевірений файл</th>
										</tr>
									</thead>
									<tbody>
									</tbody>
								</table>
							</div>
					</div>
					<br>
					<div align="right" id="BackButtonArea" style="display:none;">
						<div id="buttonitem" style="margin-left:0px;padding-left:10px">
							<a id="BackButton" style="cursor:pointer;pointer-events: auto;" href="javascript:void(0);"  title="Назад">Назад</a>
						</div>
					<div>
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