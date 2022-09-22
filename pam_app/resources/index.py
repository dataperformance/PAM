from flask import Blueprint, request, jsonify,render_template

index = Blueprint('index', __name__,template_folder="pam_app/templates")




@index.route('/',methods = ['GET'])
def index_page():
    """the default page"""
    return render_template('home_page.html')
