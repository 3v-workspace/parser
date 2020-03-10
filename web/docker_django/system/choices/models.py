import time
import asyncio

from django.db.models import IntegerField

from .exceptions import (
    ChoiceExistsError,
    InvalidTypeError,
    ExpectationFailedError,
)
from .loader import LoaderThread


class Field(object):
    id:int
    key:str
    title:str

    def __init__(self, id, key, title):
        self.id = id
        self.key = key
        self.title = title

    def __repr__(self):
        return repr((self.id, self.title))

    def __str__(self):
        return str(self.id)


class Choices(object):
    _Loader = LoaderThread()
    _Loader.daemon = True
    _Loader.start()

    def __init__(self, **kwargs):
        '''
        :param kwargs: {KEY: TITLE}
        '''

        self.fields = []
        for key, title in kwargs.items():
            if not isinstance(key, str) or \
                    not isinstance(title, str):
                raise InvalidTypeError("Error creating Choices: "
                                       "\"key\" and \"title\" must be \"str\" instances!")

            if not len(key) or not len(title):
                raise ExpectationFailedError("Error creating Choices: "
                                             "\"key\" and \"title\" must contain at least 1 symbol!")

            if key[0] == "_":
                # защита от перезаписи внутренних динамических методов и переменных
                raise ExpectationFailedError("Error creating Choices: "
                                             "\"key\" must not have \"_\" at the beginning!")

            if not hasattr(self, key): # защита существующих методов/переменных
                field = Field(self._next_id, key, title)
                setattr(self, key, field)
                self.fields.append(field)
            else:
                raise ChoiceExistsError()

        CHOICES_LIST.append(self)
        self.instances = [] # [(model, field_name), ...]

    def __del__(self):
        CHOICES_LIST.pop(CHOICES_LIST.index(self))

    @property
    def ids(self):
        keys = list(map(lambda field: field.id, self.fields))
        return keys

    def register(self, default_key, *args, **kwargs):
        if not hasattr(self, default_key):
            raise ExpectationFailedError(f"Error registering Choices field: there is no key=\"{default_key}\"!")

        field = IntegerField(
            choices=self,
            default=getattr(self, default_key).id
        )

        # ищем модель и название поля
        self._Loader.add_task(self, field)

        return field

    def get_field_by_id(self, id):
        return self.fields[id-1]

    def __repr__(self):
        fields = list(map(lambda field: repr(field), self.fields))
        return "Choices({fields})".format(
            fields=", ".join(fields)
        )

    def __iter__(self):
        return iter(self._get_items())

    def _get_items(self):
        return tuple(map(
            lambda field: (field.id, field.title),
            self.fields
        ))

    def __getitem__(self, item):
        return self._get_items()[item]

    @property
    def _current_id(self):
        if not getattr(self, "_id_generator", None):
            self._id_generator = 0
        return self._id_generator

    @property
    def _next_id(self):
        if not getattr(self, "_id_generator", None):
            self._id_generator = 0
        self._id_generator+=1
        return self._id_generator

CHOICES_LIST = []