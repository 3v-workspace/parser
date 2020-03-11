from eservice.models import GeoCity


class DBRouter(object):

    def db_for_read(self, model, user_id=None, **hints):
        if model == GeoCity:
            return 'directories'

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to auth_db.
        """
        if model == GeoCity:
            return 'directories'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        if obj1._meta.model == GeoCity:
            return True

    def allow_migrate(self, db, app_label, model=None, **hints):
        """
        Make sure the auth app only appears in the 'auth_db'
        database.
        """
        if model == GeoCity:
            return 'directories'
