<?php
$startPageURL = "http://js.sign.eu.iit.com.ua/";

$_SESSION["valid_lang_id"] = 0;
switch ($_SESSION["valid_lang_id"]){
	case '0':
		define("ERR404_STR1", "Помилка 404");
		define("ERR404_STR2", "Сторінку не&nbsp;знайдено<br>Сторінка, яку Ви шукаєте, була вилучена або тимчасово закрита.");
		define("ERR404_STR3", "Для того, щоб знайти необхідну Вам інформацію, будь ласка, відвідайте <a href=\"".$startPageURL."\">головну сторінку</a>");
		break;
	case '1':
		define("ERR404_STR1", "Ошибка 404");
		define("ERR404_STR2", "Страница не&nbsp;найдена<br>Страница, которую Вы ищете, была удалена или временно закрыта.");
		define("ERR404_STR3", "Для того, чтобы найти необходимую Вам информацию, пожалуйста, посетите <a href=\"".$startPageURL."\">главную страницу</a>");
		break;
	case '2':
		define("ERR404_STR1", "Error 404");
		define("ERR404_STR2", "The page is not&nbsp;found<br>The page you are looking for has been deleted or is temporarily closed.");
		define("ERR404_STR3", "To find the information you need, please visit <a href=\"".$startPageURL."\">main page</a>");
		break;
	default:
		define("ERR404_STR1", "Помилка 404");
		define("ERR404_STR2", "Сторінку не&nbsp;знайдено<br>Сторінка, яку Ви шукаєте, була вилучена або тимчасово закрита.");
		define("ERR404_STR3", "Для того, щоб знайти необхідну Вам інформацію, будь ласка, відвідайте <a href=\"".$startPageURL."\">головну сторінку</a>");
		break;
}
?>
<table border="0" cellspacing="0" cellpadding="0" align="center" width="100%">
<tr><td align="left" class="bigtext" style="font-size:20px;padding:20px 0px 40px 0px">
	<b><?php echo ERR404_STR1; ?></b>
</td></tr>
<tr><td align="left" class="textlnk" style="padding:20px 0px 20px 0px">
	<b><?php echo ERR404_STR2; ?></b>
</td></tr>
<tr><td align="left" class="textlnk" style="padding:20px 0px 20px 0px">
	<p><?php echo ERR404_STR3; ?></p>
</td></tr>
</table>