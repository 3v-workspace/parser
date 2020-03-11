from datetime import datetime

from django.shortcuts import render
from eservice.models import EService


def service_status(request):
    this_month = datetime.now().month

    if request.GET.get('from') is None:
        from_date = ''
        to = ''

        e_services_in_rejected = EService.objects.filter(status=6).count()
        e_services_in_work = EService.objects.filter(status=7).count()
        e_services_on_approval = EService.objects.filter(status=8).count()
        e_services_done = EService.objects.filter(status=9).count()
        e_services_on_refinement = EService.objects.filter(status=10).count()
    else:
        from_date = request.GET.get('from')
        to = request.GET.get('to')

        e_services_in_rejected = EService.objects.filter(status=6).count()
        e_services_in_work = EService.objects.filter(status=7).count()
        e_services_on_approval = EService.objects.filter(status=8).count()
        e_services_done = EService.objects.filter(status=9).count()
        e_services_on_refinement = EService.objects.filter(status=10).count()

    if not request.GET.get('from') and request.GET.get('to'):

        e_services_in_rejected = EService.objects.filter(status=6,
                                                         created_at__lte=datetime.strptime(request.GET.get('to'),
                                                                                           "%d-%m-%Y")).count()
        e_services_in_work = EService.objects.filter(status=7, created_at__lte=datetime.strptime(request.GET.get('to'),
                                                                                                 "%d-%m-%Y")).count()
        e_services_on_approval = EService.objects.filter(status=8,
                                                         created_at__lte=datetime.strptime(request.GET.get('to'),
                                                                                           "%d-%m-%Y")).count()
        e_services_done = EService.objects.filter(status=9, created_at__lte=datetime.strptime(request.GET.get('to'),
                                                                                              "%d-%m-%Y")).count()
        e_services_on_refinement = EService.objects.filter(status=10,
                                                           created_at__lte=datetime.strptime(request.GET.get('to'),
                                                                                             "%d-%m-%Y")).count()

    elif not request.GET.get('to') and request.GET.get('from'):

        e_services_in_rejected = EService.objects.filter(status=6,
                                                         created_at__gte=datetime.strptime(request.GET.get('from'),
                                                                                           "%d-%m-%Y")).count()
        e_services_in_work = EService.objects.filter(status=7,
                                                     created_at__gte=datetime.strptime(request.GET.get('from'),
                                                                                       "%d-%m-%Y")).count()
        e_services_on_approval = EService.objects.filter(status=8,
                                                         created_at__gte=datetime.strptime(request.GET.get('from'),
                                                                                           "%d-%m-%Y")).count()
        e_services_done = EService.objects.filter(status=9, created_at__gte=datetime.strptime(request.GET.get('from'),
                                                                                              "%d-%m-%Y")).count()
        e_services_on_refinement = EService.objects.filter(status=10,
                                                           created_at__gte=datetime.strptime(request.GET.get('from'),
                                                                                             "%d-%m-%Y")).count()
    elif request.GET.get('to') and request.GET.get('from'):

        e_services_in_rejected = EService.objects.filter(status=6,
                                                         created_at__date__range=[
                                                             datetime.strptime(request.GET.get('from'),
                                                                               "%d-%m-%Y").date(),
                                                             datetime.strptime(request.GET.get('to'),
                                                                               "%d-%m-%Y").date()]).count()
        e_services_in_work = EService.objects.filter(status=7, created_at__date__range=[
            datetime.strptime(request.GET.get('from'), "%d-%m-%Y").date(),
            datetime.strptime(request.GET.get('to'), "%d-%m-%Y").date()]).count()
        e_services_on_approval = EService.objects.filter(status=8,
                                                         created_at__date__range=[
                                                             datetime.strptime(request.GET.get('from'),
                                                                               "%d-%m-%Y").date(),
                                                             datetime.strptime(request.GET.get('to'),
                                                                               "%d-%m-%Y").date()]).count()
        e_services_done = EService.objects.filter(status=9, created_at__date__range=[
            datetime.strptime(request.GET.get('from'), "%d-%m-%Y").date(),
            datetime.strptime(request.GET.get('to'), "%d-%m-%Y").date()]).count()
        e_services_on_refinement = EService.objects.filter(status=10,
                                                           created_at__date__range=[
                                                               datetime.strptime(request.GET.get('from'),
                                                                                 "%d-%m-%Y").date(),
                                                               datetime.strptime(request.GET.get('to'),
                                                                                 "%d-%m-%Y").date()]).count()
    return render(request, 'reports/service_status.html',
                  {'e_services_in_work': e_services_in_work, 'e_services_in_rejected': e_services_in_rejected,
                   'e_services_on_approval': e_services_on_approval, 'e_services_done': e_services_done,
                   'e_services_on_refinement': e_services_on_refinement,
                   'from_date': from_date, 'to': to})


def reports_list(request):

    return render(request, 'reports/reports_list.html', )