from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from support.forms import MessageForm
from support.models import *
from django.shortcuts import render, render_to_response

#Сторінка з чатами операторського дашборду
def dialogs(request):
    """
    Отримуємо список діалогів
    """
    dialog_list = Dialog.objects.all()
    form = MessageForm
    if dialog_list.count() > 0:
        try:
            active_dialog = dialog_list.get(id=int(request.GET.get('chat')))
        except:
            active_dialog = dialog_list.first()
        if active_dialog.opponent != None:
            pass
        else:
            active_dialog.opponent = request.user
            active_dialog.save()
        # прочитуємо всі непрочитані повідомлення
        unreaded_messages = active_dialog.messages.filter(read=False).exclude(sender=request.user)
        for m in unreaded_messages:
            m.read = True
            m.save()
        #розбиваємо діалоги на сторінки для плагіна підвантаження
        page = request.GET.get('page', 1)
        paginator = Paginator(dialog_list, 6)
        try:
            dialogs = paginator.page(page)
        except PageNotAnInteger:
            dialogs = paginator.page(1)
        except EmptyPage:
            dialogs = paginator.page(paginator.num_pages)
        context = {
            'dialog_list':dialog_list,
            'active_dialog':active_dialog,
            'dialogs':dialogs,
            'form':form
        }
        return render(request, 'backend/dialogs_main.html', context)
    else:
        context = {
            'form': form
        }
        return render(request, 'backend/dialogs_main.html', context)

def reloadchatajax(request):
    """
    AJAX модуль, який оновлює список повідомлень для користувача
    """
    dialog_list = Dialog.objects.all()
    if dialog_list.count() > 0:
        try:
            #змінну, яка ідентифікує чат, який необхідно оновити отримуємо з url
            active_dialog = dialog_list.get(id=int(request.GET.get('chat')))
        except:
            #якщо змінної немає, значить це перший по списку чат
            active_dialog = dialog_list.first()
        if active_dialog.opponent != None:
            pass
        else:
            active_dialog.opponent = request.user
            active_dialog.save()
        # прочитуємо всі непрочитані повідомлення
        unreaded_messages = active_dialog.messages.filter(read=False).exclude(sender=request.user)
        for m in unreaded_messages:
            m.read = True
            m.save()
        context = {
            'active_dialog':active_dialog
        }
    return render_to_response('backend/messages_body.html', context)



