#!/bin/bash

echo "Copying static files into /app/docker_django/allstatic/...";
python /app/manage.py collectstatic --noinput;
#    -i admin \
#    -i colorful \
#    -i admin \
#    -i debug_toolbar \
#    -i django_extensions \
#    -i django_private_chat \
#    -i django_select2 \
#    -i mptt \
#    -i nested_admin \
#    -i rest_framework;