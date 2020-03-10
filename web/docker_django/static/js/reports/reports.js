$(document).ready(function () {

    $('#datepicker_from').datepicker({
        dateFormat: 'dd-mm-yyyy',
        language: 'uk',
        autoclose: true
    });
    $('#datepicker_to').datepicker({
        dateFormat: 'dd-mm-yyyy',
        language: 'uk',
        autoclose: true
    });
});
    $('#filter').click(function () {
    var from = $('#datepicker_from').val();
    var to = $('#datepicker_to').val();
    var page = '{{ page_obj.number }}';
    window.location.href = "/backend/reports/service_status/?&from=" + from + "&to=" + to;
    })