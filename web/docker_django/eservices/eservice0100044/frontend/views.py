from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from document.models import EServiceType, EServiceLog, EService

from document.models import Log

from eservice0100043.frontend.forms import DocumentFrontendForm65756745643_546
from document_66666666666.frontend.forms import DocumentFrontendForm66666666666
from document_66666666666.models import Document_66666666666
from system.libs import validate_file_extension
from document.models import DocumentFile


def create(request, created_by_ip):
    if True:
        if request.method == 'POST':
            form = DocumentFrontendForm66666666666(request.POST, request.FILES)
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

                Log(document_id=document.id, action="Послугу було створено" + request.user.first_name,
                    user=request.user).write()

                messages.success(request, "Послугу було успішно створено")
                if request.FILES:
                    for file in request.FILES.getlist('file'):
                        validate_file_extension(file)
                        filename = file.name
                        ext = filename.split('.')[-1]
                        filename = "{}__{}__{:%d-%m-%Y}__ID-{}.{}".format(
                                document.type.title,
                                document.internal_id.replace("/", "."),
                                document.created_at,
                                document.id, ext)

                        mime = file.content_type
                        size = file.size

                        document_file = DocumentFile.objects.create(document=document, file=file, author=request.user,\
                                                                    mime=mime, size=size, filename = filename)
                        document_file.save()

                return redirect('/eservice/' + str(document.id))
            else:
                return render(request, 'eservice0100043/frontend/create.html', {'form': form})

        else:
            form = DocumentFrontendForm65756745643_546()
            return render(request, 'eservice0100043/frontend/create.html', {'form': form})
    else:
        redirect('accounts/signup')


def view(request, document_id, helper):
    document = get_object_or_404(Document_66666666666, pk=document_id)
    logs = DocumentLog.objects.filter(document=document_id).order_by('-id')
    operations = [] # Відправити на доопрацювання, Видалити, Редагувати

    return render(request, 'eservice0100043/frontend/view.html', {
        'eservice': document,
        'logs': logs,
        'operations': operations,
        'helper': helper
    })


