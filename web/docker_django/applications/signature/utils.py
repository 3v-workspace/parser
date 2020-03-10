from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def index_in_general_qs(qs, index, root_id):
    """
    function help in pagination ServerRequest queryset
    :param qs: queryset
    :param index: index in queryset
    :param root_id: id if ServerRequest object that will first added to page via ajax
    :return: index of `root_id`
    """
    while qs[index].id != root_id:
        index += 1
    return index


def paginator(objects, size, request, context, var_name='objects_list'):
    """
    Paginate objects provided by view.
    :param objects: queryset of elements;
    :param size: number of objects per page;
    :param request: request object to get url parameters from;
    :param context: context to set new variables into;
    :param var_name: variable name for list of objects in template
    :return: updated context object
    """

    # apply pagination
    paginator = Paginator(objects, size)

    # try to get `page` number from request
    page = request.GET.get('page', '1')
    try:
        object_list = paginator.page(page)
    except PageNotAnInteger:
        # if page is not an integer, deliver first page
        object_list = paginator.page(1)
    except EmptyPage:
        # if page is out of range (e.g. 9999), deliver last page of results
        object_list = paginator.page(paginator.num_pages)


    bottom_root_id = object_list[0].id

    all_service_requests = objects
    # i, j - indexes in general queryset ServiceRequest.objects.all()

    i = index_in_general_qs(all_service_requests,0,bottom_root_id)

    j = i
    if object_list.has_next():
        next_object_list = paginator.page(object_list.next_page_number())
        top_root_id = next_object_list[0].id

        j = index_in_general_qs(all_service_requests,j,top_root_id)
    else:
        j = len(all_service_requests)
    custom_obj_list = all_service_requests[i:j]


    # set variable into context
    context[var_name] = custom_obj_list
    context['num_current'] = object_list.number  # required for ajax pagination
    context['num_pages'] = paginator.num_pages  # required for ajax pagination

    return context
