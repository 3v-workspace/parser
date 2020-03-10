
function infinityScroll() {
	var sign_end = false;
	var $l_m = $('#load_more');
	var ajax_call_running = false;
	var num_page = parseInt($l_m.data('num-pages'), 10);
    var num_current = parseInt($l_m.data('num_current'), 10);
    var url_to_go;

//    alert( "num_page " + num_page );
//    alert( "num_current " + num_current );
    if ( num_page > 1 ) {
        $(window).endlessScroll({
            callback: function() {
                if ( ajax_call_running ) {
                    return;
                }

                ajax_call_running = true;

                // if it is not all objects
                if ( sign_end == false ) {
                    url_to_go = ("/sign/service_requests?page=").concat(num_current + 1);

                    $.ajax({
                        url: url_to_go,
                        dataType: 'html',
                        beforeSend: function() {
                            $('#loading').show();
                        },
                        success: function(html) {
                            var html = $(html);
                            var rows = html.find('#service-request-list').children();

                            num_current = html.find('#load_more').data('num_current');

                            $l_m.data("page", num_current);
                            $('#service-request-list').append(rows);
                            $('#loading').hide();
                            if ( num_current >= num_page ) {
                                sign_end = true;
                            }

                            ajax_call_running = false;
                        },
                        error: function() {
                            alert('Error durin scrolling ...');
                            ajax_call_running = false;
                            $('#loading').hide();
                        }
                    });
                }
            }
        });
    }
}

$(document).ready(function(){
    infinityScroll();
});
