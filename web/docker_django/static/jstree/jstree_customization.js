$(document).ready(function () {
        $('#pickListResolution').select2({
             allowClear: true,
             placeholder: "Виберіть стандартну резолюцію"

        });
        $('#pickListResolution2').select2({
             allowClear: true,
             placeholder: "Виберіть стандартну резолюцію"

        });
        $('#pickListResolution3').select2({
             allowClear: true,
             placeholder: "Виберіть стандартну резолюцію"

        });
    });

    var modalUsersType = '';

    function generatePickList(inputData) {
        var $pickListDiv = $("#pickList");
        var selectedList = [];
        var to = false;

        var data = JSON.parse(inputData);
        $pickListDiv.jstree({
            "core": {
                'data': {
                    'id': 'jstreeRootNode',
                    'text': 'Електронний кабінет державного органу',
                    'state': {
                        'opened': true
                    },
                    'icon': 'ti-home',
                    'children': data
                }
            },
            "plugins": ["wholerow", "checkbox", "search"]
        });
        $pickListDiv.on("changed.jstree", function (e, data) {
            selectedList = data.selected;
        });

        $('#pickListSearch').keyup(function () {
            if (to) {
                clearTimeout(to);
            }

            to = setTimeout(function () {
                var v = $('#pickListSearch').val();
                $pickListDiv.jstree(true).search(v);

                //hide/show grid values for nodes affected by searching
                var hidden = $('ul li:hidden');
                var visible = $('ul li:visible');

                $.each(hidden, function (i) {
                    $('div[id*=' + hidden[i].id + ']').hide();
                });

                $.each(visible, function (i) {
                    $('div[id*=' + visible[i].id + ']').show();
                });

            }, 500);

        });

        $('#formSubmit').click(function (event) {
            if (selectedList.length !== 0) {
                $('#modalForm').append(
                    $('<input/>', {type: "hidden", name: "selectedList", value: JSON.stringify(selectedList)})
                ).append(
                    $('<input/>', {type: "hidden", name: "userType", value: modalUsersType})
                ).submit();
            } else {
                document.getElementById('errorBlock').innerHTML = "Нічого не вибрано!"
            }
        });
    }

    function updatePickList(search) {
        search = search || '';
        $.ajax({
            url: "/users/json/list/?search=" + search,
            context: document.body,
            success: function (data) {
                generatePickList(data);
            }
        })
    }

    $(document).ready(function () {
        updatePickList('');


    });