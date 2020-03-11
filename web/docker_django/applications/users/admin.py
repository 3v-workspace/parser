import uuid
from django.contrib import admin
from django.contrib.auth.admin import GroupAdmin
from . import models


@admin.register(models.Department)
class DepartmentAdmin(admin.ModelAdmin):
    icon = "<i class=\"material-icons\">account_balance</i>"
    list_display = ("dept_name","dept_no")


@admin.register(models.DeptEmp)
class DeptEmpAdmin(admin.ModelAdmin):
    icon = "<i class=\"material-icons\">people_outline</i>"
    list_display = ("user", "department", "is_active", "from_date", "to_date")
    search_fields = ["user__last_name", "department__dept_name"]
    list_select_related = True
    raw_id_fields = ("user", )
    list_filter = ("department", )


@admin.register(models.DeptManager)
class DeptManagerAdmin(admin.ModelAdmin):
    icon = "<i class=\"material-icons\">assignment_ind</i>"
    list_display = ("user", "department", "is_active", "from_date", "to_date")
    raw_id_fields = ("user", )
    list_filter = ("department", )


class UserAdmin(admin.ModelAdmin):
    fields = ["last_name", "first_name", "middle_name", "phone", "email", "groups", "birthday", "is_active"]

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if not obj.password:
            obj.set_password("111111")
        obj.username = str(uuid.uuid1())[:16]
        obj.save()


@admin.register(models.ProxyGroup)
class ProxyGroupAdmin(GroupAdmin):
    pass


admin.site.register(models.User, UserAdmin)