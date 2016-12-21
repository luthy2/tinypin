import os

from flask import request, g, render_template, session, url_for, redirect, flash, jsonify, abort
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db, lm, google, cli
from client import cache_request, get_content
from forms import EditUserForm
from models import User, Collection, CollectionItem
from datetime import datetime
import urllib
import time


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@lm.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.before_request
def before_request():
    g.user = None
    print g.user
    if "user_id" in session:
        g.user = User.query.get(session["user_id"])

    #TODO i think this needs to be removed
    elif 'google_token' in session:
        user_data = google.get("userinfo")
        username = user_data.data.get("email")
        if username:
            username = username.split('@')[0]
            user = User.query.filter(User.username == username).first()
            if user:
                user_id = user.id
                g.user = User.query.get(user_id)
    # else:
    #
    #     g.user = anon

@app.after_request
def after_request(response):
	db.session.remove()
	return response


@app.route('/api/1/boards/create', methods = ["POST"])
def api_create_collection():
    data = request.get_json()
    print data
    if data.get('unique_id'):
        collection = Collection.query.filter_by(unique_id = data.get("unique_id")).first()
        collection.title = data.get('title', None)
        collection.is_public = data.get('is_public')
        collection.timestamp = datetime.utcnow()
        layout = data.get('layout')
        if layout == 'one':
            collection.collection_layout = 'col-sm-6 col-sm-offset-3'
        elif layout == 'two':
            collection.collection_layout = 'col-sm-6'
        elif layout == 'three':
            collection.collection_layout = 'col-sm-4'
        if g.user == collection.creator:
            collection.collection_items.delete()
            if data.get('items'):
                for item in data.get('items'):
                    collection.append_child(CollectionItem(parent=collection, content=str(item)))
                cache_request(data.get('items'))
            db.session.add(collection)
            db.session.commit()

    else:
        collection = Collection()
        user = g.user
        if user:
            collection.creator = user
        collection.title = data.get('title', None)
        collection.is_public = data.get('is_public')
        layout = data.get('layout')
        if layout == 'one':
            collection.collection_layout = 'col-sm-6 col-sm-offset-3'
        elif layout == 'two':
            collection.collection_layout == 'col-sm-6'
        elif layout == 'three':
            collection.collection_layout = 'col-sm-4'
        for item in data["items"]:
            collection.append_child(CollectionItem(parent=collection, content=str(item)))
        db.session.add(collection)
        db.session.commit()
    return jsonify(ok=True, uri=str(url_for('board', unique_id = collection.unique_id)))

# @app.route('/api/1/boards/items/next', methods = ["GET"])
# def api_load_next():
#     offset = request.args.get('offest')
#     collection = Collection.query.filter_by(unique_id= unique_id).first()
#     items = collection.collection_items.limit(20).offset(offset)
#     html =  render_template('collection_items.html', items = items)


@app.route('/api/1/boards/items', methods = ["POST", "GET"])
def api_get_items():
    data = request.get_json()
    # offset = data.get("offset") or request.args.get("offset") or 0
    # limit = data.get("limit") or request.args.get("limit") or None
    unique_id = data.get("unique_id")
    collection = Collection.query.filter_by(unique_id = unique_id).first()
    items = []
    title = None
    if collection:
        coll_items = collection.collection_items.all()
        # coll_items = coll_items.from_self().offset(offset).limit(limit)
        for item in coll_items:
            #possibly change this to a named tuple
            i = {"url":str(item.content), "html":get_content(item.content)}
            items.append(i)
        title = collection.title
        # TODO layout = collection.laout
    return jsonify(ok=True, items = items, title = title )

@app.route('/api/1/embed', methods = ["POST"])
def api_embed_service():
    data = request.get_json()
    url = data.get("url")
    html = get_content(url)
    return jsonify(ok=True, html=html)


@app.route("/<username>/boards/<unique_id>/delete")
def delete_collection(username, unique_id):
    collection = Collection.query.filter_by(unique_id = unique_id).first()
    if collection:
        if g.user == collection.creator:
            db.session.delete(collection)
            db.session.commit()
            flash('Board Deleted')
            return redirect(url_for('user', username=username))
        else:
            flash('You dont have permission to delete this board!')
            return redirect(url_for('user', username=username))
    else:
        flash('That collection doesnt seem to exist!')
        return redirect(url_for('user', username=username))



@app.route('/signup')
def sign_up():
    return render_template('signup.html')

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))


@app.route('/logout')
def logout():
    session.pop('google_token', None)
    session.pop('user_id', None)
    g.user = None
    return redirect(url_for('index'))


@app.route('/login/authorized')
def authorized():
    resp = google.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['google_token'] = (resp['access_token'], '')
    user_info = google.get('userinfo')
    user_data = user_info.data
    email = user_data.get('email')
    username = email.split('@')[0]
    user = User.query.filter(User.username == str(username)).first()
    if user:
        session["user_id"] = user.id
        return redirect(url_for('user', username = user.username))
    else:
        user = User(username = username)
        user.email = email
        db.session.add(user)
        db.session.commit()
        g.user = user
        return redirect(url_for('user', username = user.username))
    return render_template('index.html')


@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route("/")
def index():
    return render_template("index.html", title = "Home", desc="A simple collection creator. Create and share collections of links.")

@app.route("/create")
def create():
    return render_template('create.html', title="Create", desc="Add links and customize your collection.")

@app.route("/edit/<unique_id>")
def edit(unique_id):
    if unique_id:
        collection = Collection.query.filter_by(unique_id= unique_id).first()
        print collection.id, g.user.id, collection.author
        if g.user and collection.creator == g.user:
            print g.user
            return render_template('create.html')
        else:
            return abort(404)
    else:
        return redirect(url_for('create'))

@app.route("/<username>")
@app.route("/<username>/boards")
def user(username):
  user = User.query.filter(User.username.ilike(username)).first()
  if user:
      return render_template("user.html", user = user, title="%s" % str(user.username), desc="%s's collections" % str(user.username))
  else:
      abort(404)

@app.route("/<username>/edit")
def edit_user(username):
    user = User.query.filter(User.username.ilike(username)).first()
    form = EditUserForm()
    if user == g.user:
        if form.validate_on_submit():
            if form.data.username:
                user.username = form.data.username
            if form.data.email:
                user.email = form.data.email
            db.session.add(user)
            db.sesion.commit()
        return render_template('edit_user.html', user = user, form = form)
    else:
        abort(403)

@app.route("/<username>/boards/<unique_id>")
def user_board(username, unique_id):
    user = User.query.filter(User.username.ilike(username)).first()
    unique_id = unique_id.lower()
    collection = user.collections.filter(Collection.unique_id == unique_id)
    if collection and collection.is_public or user == g.user:
        return render_template("collection.html", collection = collection, title = collection.title, desc = 'A collection created by %s tinypin' % str(user.username) )
    else:
        abort(404)

@app.route("/b/<unique_id>")
def board(unique_id):
    unique_id = unique_id.lower()
    collection = Collection.query.filter(Collection.unique_id == unique_id).first()
    if collection and collection.author and collection.is_public:
        return redirect(url_for("user_board",username = collection.creator.username, unique_id = unique_id))
    elif collection:
        return render_template("collection.html", collection = collection, title=collection.title, desc="A collection on tinypin")
    else:
        return abort(404)
