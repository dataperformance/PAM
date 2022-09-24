"""Exceptions"""


class AuthError(Exception):
    """error for authentication error"""
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['msg'] = self.message
        return rv


class InputError(Exception):
    status_code = 409

    def __init__(self, message, status_code=None, payload=None):
        super().__init__()
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['msg'] = self.message
        return rv


class UserValidationError(Exception):
    """error for user not found in db"""
    status_code = 404

    def __init__(self, message="please login first",status_code=404):
        super().__init__()
        self.message = message
        self.status_code = status_code

    def to_dict(self):
        rv = dict()
        rv['msg'] = self.message
        return rv
