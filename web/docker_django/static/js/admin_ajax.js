function js_admin_change(e){

 var tbody_id=$(e).parent().parent().parent().attr('id')

 if ($(e).val() != '') {
    var val_document = $(e).val();
 }

 $.ajax({
    "type"      : "GET",
    "url"       : "/client_api/load_field/"+val_document ,
    "dataType"  : "json",
    "cache"     : false,
    "success"   : function(json_metric) {


        $('#'+tbody_id).find('.doc_field').find('option').remove();

        for(var j = 0; j < json_metric['field_list'].length; j++){
            $('#'+tbody_id).find('.doc_field').append($('<option></option>').val(json_metric['field_list'][j][0]).html(json_metric['field_list'][j][1]));
        }


    }
})
}

function js_admin_change_field(e){
 var tbody_id=$(e).parent().parent().parent().parent().parent().parent().parent().parent().parent().parent().find('#eservice')

 if ($(e).val() != '') {
    var val_document = $(e).val();
 }
 if (tbody_id.val()){
         $.ajax({
    "type"      : "GET",
    "url"       : "/client_api/load_field/"+tbody_id.val() ,
    "dataType"  : "json",
    "cache"     : false,
    "success"   : function(json_metric) {


        $(e).find('option').remove();

        for(var j = 0; j < json_metric['field_list'].length; j++){
            $(e).append($('<option></option>').val(json_metric['field_list'][j][0]).html(json_metric['field_list'][j][1]));
        }


    }
    })
}

else{
     $(e).find('option').remove();
}

};