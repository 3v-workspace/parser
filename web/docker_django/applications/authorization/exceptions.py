class DecryptionException(Exception):
    """Власне виключення. Наразі не використовується.
    """
    code = None

    def __init__(self, error_code, *args, **kwargs):
        super(DecryptionException, self).__init__(*args, **kwargs)
        self.code = error_code