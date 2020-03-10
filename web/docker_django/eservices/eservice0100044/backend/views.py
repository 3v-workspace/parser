from django.shortcuts import render, get_object_or_404, redirect, HttpResponse, get_list_or_404
from django.contrib.auth import get_user_model
from pure_pagination import Paginator, PageNotAnInteger

from document.models import EServiceType, EServiceLog, EService
from document.models import EServiceOnApproving
from document.models import Log
from document_66666666666.backend.forms import DocumentBackendForm66666666666
from document_66666666666.models import Document_66666666666

User = get_user_model()


def create(request, created_by_ip):
    if True:
        if request.method == 'POST':
            form = DocumentBackendForm66666666666(request.POST, request.FILES)
            # fill a model from a POST
            if form.is_valid():
                document = form.save(commit=False)
                document.created_by_id = request.user.id
                document.created_by_ip = created_by_ip
                document.type = EServiceType.objects.get(pk=1)
                if EService.objects.all():
                    last_element = EService.objects.latest('id').id
                else:
                    last_element = 0
                document.internal_id = "{}-СЗ".format(last_element + 1)
                document.save()

                Log(document_id=document.id, action="Послугу було створено"+request.user.first_name,
                    user=request.user).write()

                return redirect('/backend/eservice/update/'+str(last_element+1)+'/2')
            else:
                return render(request, 'eservice0100043/backend/create.html', {'form': form})
        else:
            form = DocumentBackendForm66666666666()
            return render(request, 'eservice0100043/backend/create.html', {'form': form})
    else:
        redirect('accounts/signup')


def view(request, document_id, helper):
    document = get_object_or_404(Document_66666666666, pk=document_id)
    logs = EServiceLog.objects.filter(document=document_id).order_by('-id')
    operations = [] # Відправити на доопрацювання, Видалити, Редагувати

    bosses = User.objects.filter(groups__name='Погоджувачі')
    try:
        page = request.GET.get('page', 1)
    except PageNotAnInteger:
        page = 1

    # p = Paginator(logs, 5, request=request)
    # logs = p.page(page)

    approvers = EServiceOnApproving.objects.filter(document=document)
    return render(request, 'eservice0100043/backend/view.html', {
        'eservice': document,
        'approvers': approvers,
        'bosses': bosses,
        'logs': logs,
        'operations': operations,
        'helper': helper
    })


def update(request, document_id, created_by_ip, step, helper):
    document = get_object_or_404(Document_66666666666, pk=document_id)
    if step == 1:
        if request.method == 'POST':
            form = DocumentBackendForm66666666666(request.POST, request.FILES, instance=document)
            # fill a model from a POST
            if form.is_valid():
                document = form.save(commit=False)
                document.created_by_id = request.user.id
                document.created_by_ip = created_by_ip
                document.type = EServiceType.objects.get(pk=1)
                document.save()

                return redirect('/backend/eservice/update/'+str(document.id)+'/3')
            else:
                return render(request, 'eservice0100043//backend/update_step1.html', {'form': form})
        else:
            form = DocumentBackendForm66666666666(instance=document)
            return render(request, 'eservice0100043/backend/update_step1.html', {'form': form, 'eservice': document, 'document_object': document})
    elif step == 2:
        bosses = User.objects.filter(groups__name='Погоджувачі')
        return render(request, 'eservice0100043/backend/update_step2.html', {'bosses':bosses, 'eservice': document, 'helper': helper, 'redirect_url_step3': '/eservice/update/{}/2'.format(document.id)})

    elif step == 4:
        return render(request, 'eservice0100043/backend/update_step4.html', {'eservice': document, 'helper': helper, 'redirect_url_step4':'/eservice/update/{}/4'.format(document.id)})

    else:
        return redirect("/")
