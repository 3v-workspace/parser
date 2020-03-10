$(document).ready(function() {
      $("#id_region").change(function () {
      var countryId = $(this).val();

      $("#city").find('select').attr('disabled', 'disabled');
      var city_block = document.getElementById('city');
      var show_block = city_block.getElementsByClassName('ajax_spinner')[0];
      show_block.style.visibility = 'visible';

      $.ajax({
        url: '/eservice0100043/city_load/',
        data: {
          'region': countryId
        },
        success: function (data) {
          $("#city").html(data);
        }
      }).done(function() {
//        innerDiv.style.visibility = 'hidden';
  });;

    });

    $(function(){
        'use strict';
        $('select').select2({


        });

      });


} );