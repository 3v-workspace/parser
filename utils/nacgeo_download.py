import re
import sys
import os
import datetime as dt
import psycopg2
from collections import deque
from getpass import getpass

print('Python %s on %s' % (sys.version, sys.platform))
basedir = "/app/docker_django"
sys.path.insert(0, basedir)
sys.path.append(os.path.join(basedir, "modules"))
sys.path.append(os.path.join(basedir, "applications"))
sys.path.append(os.path.join(basedir, "eservices"))
sys.path.append(os.path.join(basedir, "system"))
print(sys.path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "system.settings.base")
os.environ.setdefault("PYTHONUNBUFFERED", "1")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'system.settings.base')
import django
print('Django %s' % django.get_version())
if 'setup' in dir(django): django.setup()

from django.contrib.auth import get_user_model

from eservice.models import Decree, Permission, EServiceOnApproving, EService, EServiceType
from nadra.models import NadraModel, Areas, NadraResource
from eservice.models import EService
from dictionaries.models import (
    DictStreetType,
    DictSourceUseType,
    DictReasonRequestAgreement,
    DictRequestDocument,
    DictMineralResource,
)

User = get_user_model()

try:
    conn = psycopg2.connect(
        host="51.15.117.18",
        dbname="nacgeo",
        user="postgres",
        password="postgresuserTempPASS"  # getpass("Database password: "),
    )
    c = conn.cursor()
except psycopg2.OperationalError as e:
    print("Error connecting to database!")
    print(e)
    sys.exit(1)

c.execute(
    "SELECT ogc_fid, ST_AsEWKT(ST_GeomFromWKB(wkb_geometry)), link_spec, kopal, galuz, nazva, vydana, end_dii, termin, vlasnik, regnom, stan "
    "FROM ollpolilicenz"
)

try:
    user = User.objects.all().first()
except Exception:
    user = None

if not user:
    raise Exception("You must create user first!")


EService.objects.all().delete()
NadraModel.objects.all().delete()
Permission.objects.all().delete()
# DictMineralResource.objects\
#     .filter(parent_id=385)\
#     .delete()

using_type_dict = {
    "Геологічне вивчення": 1,
    "Геол.вив.,ДПР,видоб.": 4,
    "Геол.вивчення з ДПР": 2,
    "Видобування": 3,
    "Будівництво,експл.": 5,
    "Створ. геол.терит.": 6,
    "Угода про розподіл": 7,
}

print("Starting...")
nadra_resources = deque()
permissions = deque()
# resources_set = set()
for result in c.fetchall():

    ogc_fid, geometry, link_spec, kopal, galuz, nazva, vydana, end_dii, termin, vlasnik, regnom, stan = result
    using_type = stan
    # print(geometry)
    print(".", end="", flush=True)
    # print(result[3:])
    link = re.search(r"href\s*?=\s*?(['\"]{1})(.+)\1", link_spec, flags=re.IGNORECASE).group(2)
    # print(f"Link: {link}")

    try:
        resources = [i.strip() for i in kopal.split(", ")]
    except Exception:
        resources = []

    try:
        last_element = EService.objects.latest('id').id
    except Exception:
        last_element = 0

    polygon = []
    for i in re.findall(r"\d{2}\.\d+ \d{2}\.\d+", geometry):
        try:
            a, b = i.split()
            polygon.append(
                (float(b), float(a))
            )
        except Exception:
            pass

    nadr = NadraModel(
        person_type=NadraModel.LE,
        internal_id="{}-СЗ".format(last_element + 1),
        type_id=3,
        name=nazva,
        created_by_id=user.pk,
        le_full_name=vlasnik, # vlasnik
        created_by_ip="127.0.0.1",
        resolutioner_viewed=True,
        status_id=14,
        le_street_type_id=None,
        resource_terms=f"{termin} р.",
        resource_use_type_id=using_type_dict[using_type],
        registration_date=dt.datetime.strptime(vydana, "%d-%m-%Y"),
        is_hidden=True,
    )
    nadr.save()

    area = Areas(
        nadra_id=nadr.pk,
        poly=polygon,
        name=nazva,
    )
    area.save()

    for resource_ in resources:
        resource = resource_\
            .replace("`", "'")
        defaults = {
            "parent_id": 385,
            "resource_location_type": 2,
            # "resource_type": 2,
            "attr": [],
        }
        try:
            r = DictMineralResource.objects.filter(
                title=resource
            )[0]
        except (IndexError, Exception) as e:
            # resources_set.add(resource_)
            category_index = DictMineralResource.objects.latest("id").id+1

            r = DictMineralResource.objects.create(
                title=resource,
                category_index=category_index,
                **defaults,
            )
        res = NadraResource(
            nadra_id=nadr.pk,
            resource_area_id=r.pk,
            resource_type=2,
            resource_location_type=2,
        )
        nadra_resources.append(res)

    perm = Permission(
        eservice_id=nadr.pk,
        number=regnom,
        get_date=dt.datetime.strptime(vydana, "%d-%m-%Y"),
        end_date=dt.datetime.strptime(end_dii, "%d-%m-%Y"),
        reason="",
        type="", ####
        goal="",
        created_at=dt.datetime.strptime(vydana, "%d-%m-%Y"),
        created_by_id=user.pk,
    )
    permissions.append(perm)

print("\nSaving Permission and NadraResource objects...")
Permission.objects.bulk_create(permissions)
NadraResource.objects.bulk_create(nadra_resources)
print("DONE!")

# for i in resources_set:
#     print(i)