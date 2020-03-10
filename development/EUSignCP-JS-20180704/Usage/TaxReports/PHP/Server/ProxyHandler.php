<?php

@define (HttpRequestParameterAddress, "address");
@define (HttpRequestParameterContentType, "content_type");
@define (HttpContentTypeMultipart, "multipart/form-data");
@define (HttpContentTypeBase64, "X-user/base64-data");

$sKnownHosts = array(
	"czo.gov.ua",
	"acskidd.gov.ua",
	"ca.informjust.ua",
	"csk.uz.gov.ua",
	"masterkey.ua",
	"ocsp.masterkey.ua",
	"tsp.masterkey.ua",
	"ca.ksystems.com.ua",
	"csk.uss.gov.ua",
	"csk.ukrsibbank.com",
	"acsk.privatbank.ua",
	"ca.mil.gov.ua",
	"acsk.dpsu.gov.ua",
	"acsk.er.gov.ua",
	"ca.mvs.gov.ua",
	"canbu.bank.gov.ua",
	"uakey.com.ua",
	"altersign.com.ua",
	"ca.altersign.com.ua",
	"ocsp.altersign.com.ua",
	"acsk.uipv.org",
	"ocsp.acsk.uipv.org",
	"ca.iit.com.ua");

function is_known_host($value) {
	$sHost = parse_url($value, PHP_URL_HOST);
	if (is_null($sHost) or !$sHost) {
		$sHost = $value;
	}

	foreach ($GLOBALS["sKnownHosts"] as $sKnownHost) {
		if ($sHost == $sKnownHost)
			return true;
	}

	return false;
}

function convert_bytes($value) {
    if (is_numeric($value)) {
        return $value;
    } else {
        $value_length = strlen($value);
        $qty = substr($value, 0, $value_length - 1);
        $unit = strtolower(substr($value, $value_length - 1 ));
        switch ($unit) {
            case 'k':
                $qty *= 1024;
                break;
            case 'm':
                $qty *= 1024 * 1024;
                break;
            case 'g':
                $qty *= 1024* 1024 * 1024;
                break;
        }
        return $qty;
    }
}

function handle_request($requestMethod) {
	$sAddress = NULL;
	$sContent = NULL;
	$sServerRequest = NULL;
	$sResponse = NULL;
	$sError;

	if ($requestMethod == 'POST') {
		$postMaxSize = convert_bytes(ini_get('post_max_size'));
		if ($_SERVER['CONTENT_LENGTH'] > $postMaxSize) {
			return 'HTTP/1.0 413 Request Entity Too Large';
		}

		parse_str($_SERVER['QUERY_STRING'], $sPostParams);
		$sAddress = $sPostParams[HttpRequestParameterAddress];

		$sContent = file_get_contents('php://input');
		$sServerRequest = base64_decode($sContent);
	} else {
		$sAddress = $_GET[HttpRequestParameterAddress];
	}

	if (!is_known_host($sAddress)) {
		return 'HTTP/1.0 403 Forbidden';
	}

	$sError = caocspr_redirect_to($sServerRequest, $sAddress, $sResponse);
	if ($sError != 0) {
		return 'HTTP/1.0 500 Internal Server Error';
	}

	header("Content-type: " . HttpContentTypeBase64 . "; charset=utf-8");
	header("Cache-Control: no-store, no-cache, must-revalidate");
	header("Cache-Control: post-check=0, pre-check=0", false);
	echo base64_encode($sResponse);

	return '';
}

$sStatus = NULL;

try {
	$sRequestMethod = $_SERVER['REQUEST_METHOD'];
	if ($sRequestMethod == 'GET' || $sRequestMethod == 'POST') {
		$sStatus = handle_request($sRequestMethod);
	} else {
		$sStatus = 'HTTP/1.0 400 Bad Request';
	}
} catch (Exception $e) {
	$sStatus = 'HTTP/1.0 500 Internal Server Error';
	echo $e;
}

if ($sStatus != '') {
	header('Content-Type: text/html; charset=utf-8');
	header($sStatus);
	echo 'Виникла помилка при обробці запиту';
	exit;
}

?>
