try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse
from support.forms import MessageForm
from support.models import *
from django.shortcuts import render, redirect, render_to_response


#Сторінка підтримки для кожного користувача
def dialogs_users(request):
    form = MessageForm
    try:
        active_dialog = Dialog.objects.filter(owner=request.user).last()
        unreaded_messages = active_dialog.messages.filter(read=False).exclude(sender=request.user)
        for m in unreaded_messages:
            m.read = True
            m.save()
    except:
        active_dialog = Dialog.objects.create(owner=request.user).save()
    #прочитуємо всі непрочитані повідомлення
    # active_dialog = dialog_list.first()
    context = {
        'active_dialog':active_dialog,
        'form':form,
    }
    return render(request, 'frontend/dialogs_users.html', context)

def reloaduserchatajax(request):
    """
        AJAX модуль, який оновлює список повідомлень для користувача
    """
    try:
        active_dialog = Dialog.objects.filter(owner=request.user).last()
    except:
        active_dialog = Dialog.objects.create(owner=request.user).save()
    #прочитуємо всі непрочитані повідомлення
    unreaded_messages = active_dialog.messages.filter(read=False).exclude(sender=request.user)
    for m in unreaded_messages:
        m.read = True
        m.save()
    context = {
        'active_dialog':active_dialog,
    }
    return render_to_response('frontend/messages_user_body.html', context)

#СПІЛЬНЕ!!! отримуємо повідомлення з чату та зберігаємо в БД
def get_message(request):
    # message = request.POST.get('message')
    dialog_list = Dialog.objects.all()
    #якщо юзер є оператором
    if request.user.is_operator():
        try:
            #змінна, отримана з url
            chat_id = int(request.POST.get('chat'))
            active_dialog = dialog_list.get(id=chat_id)
        except:
            active_dialog = dialog_list.first()
        if request.method == 'POST':
            #використовуємо форму для збереження повідомлення в БД
            form = MessageForm(request.POST, request.FILES)
            if form.is_valid():
                update = form.save(commit=False)
                update.dialog = active_dialog
                try:
                    update.filename = request.FILES['file'].name
                except:
                    pass
                update.sender = request.user
                update.save()
                #редіректимо на сторінку того ж чату
                return redirect('/backend/dialogs-main/?chat=' + str(active_dialog.id))
        else:
            form = MessageForm()
        # Message.objects.create(sender=request.user, text=message, dialog=active_dialog).save()
        return redirect('/backend/dialogs-main/?chat='+str(active_dialog.id))
    #Якщо мова йде не про оператора
    else:
        #якщо стався якийсь збій - отримуємо останній діалог, який належить даному користувачу
        dialog = Dialog.objects.filter(owner=request.user).last()
        if request.method == 'POST':
            form = MessageForm(request.POST, request.FILES)
            if form.is_valid():
                update = form.save(commit=False)
                update.dialog = dialog
                try:
                    update.filename = request.FILES['file'].name
                except:
                    pass
                update.sender = request.user
                update.save()
                return redirect('/dialogs-users/')
        else:
            form = MessageForm()
        return redirect('/dialogs-users/')
