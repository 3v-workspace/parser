# from django.core.management.base import BaseCommand, CommandError
# from django.contrib.contenttypes.models import ContentType
# from django.contrib.auth.models import Permission, Group
#
#
# class Command(BaseCommand):
#     args = '<group_name app_label>'
#     help = 'Syncs permissions of group with given name with permissions of all models of app with giver app_label '
#
#     def add_arguments(self, parser):
#         parser.add_argument('--group_name', action='append', type=str)
#         parser.add_argument('--app_label', action='append', type=str)
#
#     def handle(self, *args, **options):
#         group_name = options['group_name']
#         app_label = options['app_label']
#         group = Group.objects.get(name=group_name[0])
#
#         cts = ContentType.objects.get_or_create(app_label=app_label[0])
#         perms = Permission.objects.filter(content_type__in=cts)
#         group.permissions.add(*perms)