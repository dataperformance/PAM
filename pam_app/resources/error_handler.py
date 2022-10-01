from flask import jsonify, Blueprint, abort, Response
from .exception import AuthError, InputError, UserValidationError

error_bp = Blueprint('error_handler', __name__)


@error_bp.app_errorhandler(AuthError)
def auth_error(e):
    """auth exception"""
    return jsonify(e.to_dict()), e.status_code


@error_bp.app_errorhandler(InputError)
def input_error(e):
    """Input exception"""
    return jsonify(e.to_dict()), e.status_code


@error_bp.app_errorhandler(UserValidationError)
def user_validation_error(e):
    return jsonify(e.to_dict()), e.status_code


# missing keys
def missing_key_error(missing_key, ke):
    """raise error for missing key"""
    abort(409, Response({'msg': f'missing {missing_key} key'}))
