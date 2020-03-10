import threading
import asyncio
import datetime as dt

class LoaderThread(threading.Thread):
    '''
    Подгрузка модели, к которой было добавлено поле.

    В результате работы заполняет choices_instance.instances
    кортежами типа (model:models.Model, field_name:str)
    '''
    loop = asyncio.new_event_loop()

    def __init__(self):
        super(LoaderThread, self).__init__()

        self.queue = asyncio.Queue()
        self.last_activity = dt.datetime.now()

    def run(self):
        self.loop.run_until_complete(self.run_tasks())

    def add_task(self, choices_instance, field):
        self.queue.put_nowait((choices_instance, field))

    async def run_tasks(self):
        while True:
            # если не было активности уже 10 секунд - всё инициализировалось
            # останавливаем эту шайтан-машину
            if (dt.datetime.now() - self.last_activity).total_seconds() >= 10:
                self.loop.stop()
                break

            while not self.queue.empty():
                self.last_activity = dt.datetime.now()
                choices_instance, field = self.queue.get_nowait()
                self.loop.create_task(self.load_field(choices_instance, field))
            await asyncio.sleep(0.1)

    async def load_field(self, choices_instance, field):
        # django.db.models.options:152
        try:
            model = field.model
            if model:
                choices_instance.instances.append(
                    (model, getattr(field, "name", None))
                )
            else:
                self.queue.put_nowait(field)

            await asyncio.sleep(0.07)
        except Exception:
            pass