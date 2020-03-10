import uuid, os
from django.core.exceptions import ValidationError


def file_name(instance, filename):
    from django.contrib.contenttypes.models import ContentType
    content_type = ContentType.objects.get_for_model(instance).model
    ext = filename.split('.')[-1]
    filename = '{0}/{1}.{2}'.format(content_type, uuid.uuid4(), ext)


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf', '.doc', '.docx', '.odt', '.rtf', '.jpg', '.jpeg', '.png', '.tif', '.tiff', '.xls', '.xlsx']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Недоступне розширення файлу')