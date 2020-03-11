import json
from django.http import HttpResponse
from users.models import Department, DeptEmp
from . import models, forms


# @login_required
# def change_manager(request, department_pk):
#     department = get_object_or_404(models.Department, pk=department_pk)
#     form = forms.ChangeManagerForm(department=department, data=request.POST or None)
#
#     if form.is_valid():
#         form.save()
#
#     return render(request, 'users/change_manager.html', {
#         'form': form,
#         'department': department,
#         'model': models.Department
#     })
#
#
# @login_required
# def change_title(request, employee_pk):
#     employee = get_object_or_404(models.User, pk=employee_pk)
#     form = forms.ChangeTitleForm(employee=employee, data=request.POST or None)
#
#     if form.is_valid():
#         form.save()
#
#     return render(request, 'users/change_title.html', {
#         'form': form,
#         'employee': employee,
#         'model': models.User
#     })
#
#
# class DepartmentEmployesListView(ListModelView):
#     model = models.User
#     list_display = ('emp_no', 'first_name', 'last_name', 'current_salary')
#     template_name = 'users/department_users.html'
#
#     def get_queryset(self):
#         today = timezone.now().date()
#         department = get_object_or_404(models.Department, pk=self.kwargs['department_pk'])
#         queryset = super(DepartmentEmployesListView, self).get_queryset()
#
#         return queryset.filter(
#             deptemp__department=department,
#             deptemp__is_activate=True,
#             deptemp__from_date__lte = today,
#             deptemp__to_date__gt = today
#         )
#
#     def get_context_data(self, **kwargs):
#         department = get_object_or_404(models.Department, pk=self.kwargs['department_pk'])
#         return super(DepartmentEmployesListView, self).get_context_data(
#             department=department, **kwargs)
#
#
# class EmployeeViewSet(ModelViewSet):
#     model = models.User
#     list_display = ('emp_no', 'first_name', 'last_name', 'birth_date', )
#
#     change_title_view = [
#         r'^(?P<employee_pk>.+)/change_title/$',
#         change_title,
#         '{model_name}_change_title'
#     ]
#
#     def current_salary(self, obj):
#         salary = obj.salary_set.current()
#         return salary.salary if salary is not None else 0
#     current_salary.short_description = _('current salary')
#
#
# class DepartmentViewSet(ModelViewSet):
#     model = models.Department
#     list_display = ('dept_no', 'dept_name', 'manager', 'users')
#
#     change_manager_view = [
#         r'^(?P<department_pk>.+)/change_manager/$',
#         change_manager,
#         '{model_name}_change_manager'
#     ]
#
#     users_list_view = [
#         r'^(?P<department_pk>.+)/users/$',
#         DepartmentEmployesListView.as_view(viewset=EmployeeViewSet()),
#         '{model_name}_users'
#     ]
#
#     def manager(self, obj, today=None):
#         if today is None:
#             today = timezone.now().date()
#         manager = obj.deptmanager_set.filter(
#             is_active=True, from_date__lte=today,
#             to_date__gt=today).first()
#         return manager.employee if manager is not None else ''
#
#     def users(self, obj):
#         return obj.deptemp_set.count()
#     users.short_description = _('users')


# Формуємо дерево відділів та персоналу для вибору у модальному вікні
def user_list(request):
    department_tree = Department.objects.get(level=0)
    departments = [
        {
            'id': str(s.dept_no),
            'text': s.dept_name,
            'icon': 'ti-briefcase',
            'children': [
                {
                    'text': '{}'.format(c.dept_name),
                    'icon': 'ti-briefcase',
                    'children': [{
                        'id': 'employee_' + str(u.user.id),
                        'text': "<b>{} {} {}</b> ({})".format(u.user.last_name, u.user.first_name,
                                                              u.user.middle_name,
                                                              u.user.position),
                        'icon': 'ti-user'
                    }for u in DeptEmp.objects.filter(department=c.dept_no).order_by("priority")]
                }for c in s.get_children()]
            # if False else {'id': 'employee_' + 'sfds', 'text': 'dfdf','icon': 'ti-briefcase','children': [{
            #         'text': 'fdgdfg',
            #         'icon': 'ti-briefcase', }]}
            if s.get_children() else

            [
                {
                    'id': 'employee_' + str(u.user.id),
                    'text': "<b>{} {} {}</b> ".format(u.user.last_name, u.user.first_name,
                                                          u.user.middle_name,
                                                          ),
                    'icon': 'ti-user'
                } for u in DeptEmp.objects.filter(department=s.dept_no).order_by("priority")
            ]
        } for s in Department.objects.get(level=0).get_children().order_by("priority")]

    for s in Department.objects.get(level=0).get_children().order_by("priority"):
        if s.get_children():
            for u in DeptEmp.objects.filter(department=s.dept_no):

                for item in departments:
                    if item['id'] == s.dept_no:
                        item['children'].append({'id':'employee_' + str(u.user.id), 'text': "<b>{} {} {}</b>".format(u.employee.last_name, u.employee.first_name,
                                                              u.user.middle_name,
                                                              ), 'icon': 'ti-user'})

    response = json.dumps(departments)
    return HttpResponse(response)
