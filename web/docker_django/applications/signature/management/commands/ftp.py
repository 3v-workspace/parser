import ftplib
from os.path import abspath, exists, dirname


from django.core.management.base import BaseCommand
from signature.models import ServiceRequest


def ftp_send_files(session):
    print("Sending files ...")
    session.cwd('/in')

    for item in ServiceRequest.objects.filter(status=ServiceRequest.NEW):
        f_path_xml = abspath("media/out/{}.xml".format(item.id))
        f_path_hash = abspath("media/out/{}.hash".format(item.id))
        # print(f_path_xml)
        # print(f_path_hash)
        if exists(f_path_xml) and exists(f_path_hash):
            with open(f_path_xml, 'rb') as f_xml:
                print('Exist ' + f_path_xml)
                session.storbinary('STOR {}.xml'.format(item.id), f_xml)
            with open(f_path_hash, 'rb') as f_hash:
                print('Exist ' + f_path_hash)
                session.storbinary('STOR {}.hash'.format(item.id), f_hash)

            item.status = ServiceRequest.IS_PROCESSED
            item.save()


def ftp_receive_files(session):
    print("Receiving files ...")
    session.cwd('/out')

    list_id_send_xml_requests = []
    files = session.nlst()
    try:
        files.remove('..')
        files.remove('.')
    except ValueError:
        pass
    for file_name in files:
        try:
            list_id_send_xml_requests.append(int(file_name.split('.')[0]))
        except Exception:
            pass
        else:
            f_path_xml = abspath("media/in/{}".format(file_name))
            print(f_path_xml)
            with open(f_path_xml, 'wb') as f_xml:
                session.retrbinary('RETR {}'.format(file_name), f_xml.write)
            session.delete(file_name)

    for item in ServiceRequest.objects.filter(status=ServiceRequest.IS_PROCESSED).filter(id__in=list_id_send_xml_requests):
        item.status = ServiceRequest.PROCESSED
        item.save()


def ftp_interation():
    print("FTP command start")
    session = ftplib.FTP("rk304501.ftp.tools", "rk304501_ecab", "forever")

    ftp_send_files(session)
    ftp_receive_files(session)

    session.quit()
    print("FTP command finish")


class Command(BaseCommand):
    help = 'Sending .xml & .hash to ftp and getting earlier sent ones'

    def handle(self, *args, **options):
        ftp_interation()
