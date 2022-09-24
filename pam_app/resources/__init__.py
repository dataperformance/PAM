# from error_handler import *
from flask import abort
from exception import InputError


def request_handler(request_obj, *keys):
    """
    input: response from client, and required key name/s
    output: error or dict of request
    """
    data = request_obj.get_json()
    result_dict = {}
    for key in keys:
        try:
            result_dict[key] = data[key]
        except KeyError as KE:
            raise InputError(f"Missing or incorrect key name: {key}", status_code=404)
    return result_dict
