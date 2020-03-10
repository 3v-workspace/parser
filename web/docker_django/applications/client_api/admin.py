from django.contrib import admin
from client_api.models import ClientApi, ClientApiEService
import nested_admin

# @admin.register(ClientApieserviceField)
# class ClientApieserviceFieldAdmin(admin.ModelAdmin):
#     # exclude = ['created_at']
#     pass
from client_api.forms import ClientApiEServiceFieldForm, ClientApiEServiceForm
from client_api.models import ClientApiEServiceField


class ClientApieserviceFieldInlineAdmin(nested_admin.NestedTabularInline):
    model = ClientApiEServiceField
    form = ClientApiEServiceFieldForm
    extra = 0

    def change_view(self, request, object_id, extra_context=None):
        self.exclude = ('field',)
        return super(ClientApieserviceFieldInlineAdmin, self).change_view(request, object_id, extra_context)

    # def get_formsets_with_inlines(self, request, obj=None):
    #         print('sdfdsfdsf')
    #         print(self.get_inline_instances(request, obj))
    #         for inline in self.get_inline_instances(request, obj):
    #             if obj and obj.has_amazon_fba_vacation:
    #                 yield inline.get_formset(request, obj), inline
    #
    #
    # def formfield_for_dbfield(self, field, **kwargs):
    #
    #     # print(self.get_object(kwargs['request'], ClientApieservice))
    #     # print(field.client_api_eservice)
    #     if field.name == 'field':
    #         parent_business = self.get_object(kwargs['request'], ClientApieservice)
    #         if parent_business == None:
    #             related_descriptiontype = EServiceType.objects.all()
    #         else:
    #             related_descriptiontype = EServiceType.objects.filter(category=parent_business.category_id)
    #         return forms.ModelChoiceField(queryset=related_descriptiontype)
    #     return super(ClientApieserviceFieldInline, self).formfield_for_dbfield(field, **kwargs)
    #
    # def get_object(self, request, model):
    #     object_id = request.META['PATH_INFO'].strip('/').split('/')[-1]
    #
    #     try:
    #         object_id = int(object_id)
    #     except ValueError:
    #         return None
    #     return model.objects.get(pk=object_id)
    #


class ClientApieserviceInline(nested_admin.NestedTabularInline):
    model = ClientApiEService
    inlines = [ClientApieserviceFieldInlineAdmin]
    extra = 0
    form = ClientApiEServiceForm

    def get_inline_instances(self, request, obj=None):
        # print(obj)
        # print(self.inlines)
        for inline in self.inlines:
            # print(inline)
            pass
        return [inline(self.model, self.admin_site) for inline in self.inlines]


class ClientApiAdmin(nested_admin.NestedModelAdmin):
    inlines = [ClientApieserviceInline]


admin.site.register(ClientApi, ClientApiAdmin)
# admin.site.register(ClientApieserviceField, ClientApieserviceFieldInlineAdmin)


# class ClientApieserviceAdmin(admin.ModelAdmin):
#     pass
#
#
# admin.site.register(ClientApieservice, ClientApieserviceAdmin)
