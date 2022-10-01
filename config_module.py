class Config(object):
    DEBUG = True


class Local(Config):
    """local config"""
    JWT_SECRET_KEY = b'\x0b\x8e\xae\x1d\x97\x1f\xea\x1fB\xc3?\xb3<\x02\xfb\xc3'
    MONGODB_SETTINGS = {
        "db": "local-test-databse",
        "host": "localhost",
        "port": 27017,
        "alias": "default",
    }


class QA(Config):
    """QA config"""
    JWT_SECRET_KEY = None
    MONGODB_SETTINGS = None

    def __init__(self):
        print("Initializing secret manager")
        from secret_manager import JWT_SECRET_KEY, MONGODB_SETTINGS
        self.JWT_SECRET_KEY = JWT_SECRET_KEY
        self.MONGODB_SETTINGS = MONGODB_SETTINGS


# production config
class Production(Config):
    """production config"""
    JWT_SECRET_KEY = None
    MONGODB_SETTINGS = None

    def __init__(self):
        print("Initializing secret manager")
        from secret_manager import JWT_SECRET_KEY, MONGODB_SETTINGS
        self.JWT_SECRET_KEY = JWT_SECRET_KEY
        self.MONGODB_SETTINGS = MONGODB_SETTINGS
