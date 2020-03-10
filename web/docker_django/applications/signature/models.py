from django.db import models


class ServiceRequest(models.Model):
    """
    The model designed for sroring data from form of sending xml to POLICE
    """

    NEW = 1
    IS_PROCESSED = 2
    PROCESSED = 3
    CANCELED = 4

    SERVICE_TEST_BP = 1

    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256)
    birthday = models.DateField(default=None, null=True)
    phone = models.CharField(max_length=15, null=True, default=None)

    status = models.IntegerField(
        choices=((NEW, 'Новий'),
                 (IS_PROCESSED, 'У роботі'),
                 (PROCESSED, 'Опрацьовано'),
                 (CANCELED, ' Відхилено')),
        default=NEW
    )

    service_title = models.IntegerField(
        choices=((SERVICE_TEST_BP, 'Тестовий бізнес-процес'),),
        default=SERVICE_TEST_BP
    )
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name

    @property
    def full_name(self):
        return self.first_name + ' ' + self.last_name

    @property
    def status_str(self):
        if self.status == self.NEW:
            return 'Новий'
        elif self.status == self.IS_PROCESSED:
            return 'У роботі'
        elif self.status == self.PROCESSED:
            return 'Опрацьовано'
        else:
            return 'У роботі'

    @property
    def service_title_str(self):
        # if self.service_title == self.SERVICE_TEST_BP:
        return 'Тестовий бізнес-процес'
