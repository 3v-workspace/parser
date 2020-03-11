from django.contrib import admin

# Register your models here.
from mailer.admin import MessageAdmin, DontSendEntryAdmin, MessageLogAdmin
from mailer.models import Message, DontSendEntry, MessageLog

admin.site.unregister(Message)
admin.site.unregister(DontSendEntry)
admin.site.unregister(MessageLog)
