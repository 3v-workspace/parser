function check_element(element) {
//        $("div.error").hide();
        var is_valid = $(element).valid();
        if ( !is_valid ) {
          $("div.error").show();
          $(element).css("border", "1px solid red");
          $(element).parent().find('.control-label').css("color", "red");
          $(element).find(".has-error").show();
        } else{
          $("div.error").hide();
          $(element).css("border", "1px solid #ced4da");
          $(element).parent().find('.control-label').css("color", "black");
          $(element).parent().find(".has-error").hide();
        }
//        alert($( "#send-data-to-police-form" ).find(".has-error").length > 1);
        if ( $( "#send-data-to-police-form" ).find("input.has-error").length > 0 ) {
            $("div.error").show();
        } else {
            $("div.error").hide();
        }
}
function validation_form_send_request() {
    jQuery.validator.addMethod("custom_cyrilic_latin", function(value, element, param) {
      return value.match(new RegExp("^" + param + "$")) && !value.match(new RegExp("^" + "[ ]+" + "$"));
    });
    jQuery.validator.addMethod("date_valid", function(value, element, param) {
        return value.match(new RegExp("^\\d{2}/\\d{2}/\\d{4}$"));
    });
    jQuery.validator.addMethod("phone_valid", function(value, element, param) {
        return value.match(new RegExp("^\\(\\d{3}\\) \\d{3}\\-\\d{4}$"));
    });
    var custom_cyrilic_latin_regex = "[a-zA-Zа-яіїґєёА-ЯІЇҐЄЁ' \\-]+";
    $("div.error").hide();

    jQuery.validator.setDefaults({
      debug: false,
      success: "valid"
    });
    var form = $( "#send-data-to-police-form" );
    var validator = form.validate({
      onfocusout: function(element, e) {
//        console.log("onkeyup ", e["keyCode"]);
        if ( e["keyCode"] != 9 && e["keyCode"] != 16 ) {
          check_element(element);
        }
      },
      onclick: true,
      onkeyup : false,
      rules: {
        first_name: {
          custom_cyrilic_latin: custom_cyrilic_latin_regex,
          required: true,
          maxlength: 256
        },
        last_name: {
          custom_cyrilic_latin: custom_cyrilic_latin_regex,
          required: true,
          maxlength: 256
        },
        birthday: {
            date_valid: true
        },
        phone: {
            phone_valid: true
        }
      },
      messages:{
        first_name: {
          custom_cyrilic_latin: "Ім'я може містити лише літери, апостроф, дифіс і пробіл. Не може містити виключно пробіли",
          required: "Введіть Ваше прізвище!",
          maxlength: "Ім'я не може перевищувати 256 символів!"
        },
        last_name: {
          custom_cyrilic_latin: "Прізвище може містити лише літери, апостроф, дифіс і пробіл. Не може містити виключно пробіли",
          required: "Введіть Ваше прізвище!",
          maxlength: "Прізвище не може перевищевати 256 символів!"
        },
        birthday: {
            date_valid: "Введіть коректну дату народження!",
            required: "Введіть Вашу дату народження!",
        },
        phone: {
            phone_valid: "Введіть коректний номер!",
            required: "Введіть Ваш номер телефону!",
        }
      },
      errorClass: "invalid has-error",
      invalidHandler: function(event, validator) {
    // 'this' refers to the form
//        console.log(validator);
        var errors = validator.numberOfInvalids();
        if (errors) {
//          var message = errors == 1
//            ? 'Помилка при валідації. Вона підсвічена'
//            : 'У Вас ' + errors + ' поля не пройшли перевірку. Вони підсвічені!';
//          $("div.error span").html(message);
          $("div.error").show();


//          <!--$(this).find(".form-group").addClass("has-error");-->
//          $(this).find('input.invalid').each(function() {
//            $(this).parent().addClass("has-error");
//          });
//          $(this).find('input.valid').each(function() {
//            $(this).parent().removeClass("has-error");
//          });
            for (var i=0;i<validator.errorList.length;i++){
//                check_element(validator.errorList[i].element);
                var element = validator.errorList[i].element;
//                console.log(validator.errorList[i].element);
                $(element).css("border", "1px solid red");
                $(element).parent().find('.control-label').css("color", "red");
            }

            //validator.errorMap is an object mapping input names -> error messages
//            for (var i in validator.errorMap) {
//              console.log(i, ":", validator.errorMap[i]);
//            }
//    $( "#send-data-to-police-form" ).formValidation(function(element, result) {
//      console.log(['validation ran for form:', element, 'and the result was:', result]);
//    });
        } else {
          $("div.error").hide();
        }
      },
      submitHandler: function(form) {
//        euSignTest.signHashCustom();
//        if ( !form.valid() ) {
        $("div.error").hide();
//            form.formValidation(function(element, result) {
//              console.log(['validation ran for form:', element, 'and the result was:', result]);
//            });
//        }
        form.submit();
      }
    });
}

function validation_form_service_request() {
    $('#id_first_name, #id_last_name').keypress(function() {
       alert(this.val());
    });
}

$(document).ready(function(){
    validation_form_send_request();
    $(":input").inputmask();
//    $('#id_first_name, #id_last_name').keypress(function() {
//        var $this = $(this);
//        var id = $this.attr('id');
//
//        var is_error = $this.parent().find('label.has-error');
//        alert(is_error);
//    });
});
