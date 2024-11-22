from flask import Blueprint, Response, abort, redirect, render_template, request, url_for
from models import *
from daily import train

views = Blueprint("views", __name__)

@views.route("/")
def default():
    return redirect(url_for("views.base", page='index'))

@views.route('/&page=<page>')
def base(page: str):
    match page:
        case 'index':
            return index()
        case _:
            return abort(404)

def index():
    models = ModelJSON.query.all()
    if not models:
        train_model = train()
        return Response(train_model, content_type='text/plain')
    return render_template("index.html")
