from app import db
from app import app
# from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
import client



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), unique = True)
    pw_hash = db.Column(db.String())
    email = db.Column(db.String(), unique = True)
    email_token = db.Column(db.String())
    email_notifications = db.Column(db.Boolean(), default = True)
    authenticated = db.Column(db.Boolean(), default = False)
    joined = db.Column(db.DateTime())
    collections = db.relationship('Collection', backref = "creator", lazy='dynamic')

    def __init__(self, username):
        self.username = username

    def __repr__(self):
        return '<User %r>' % (self.username)

    def get_id(self):
        try:
            return unicode(self.id) #python 2
        except NameError:
            return str(self.id) #python 3

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

class Collection(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    unique_id = db.Column(db.String(), index = True)
    author = db.Column(db.Integer, db.ForeignKey('user.id'), index = True)
    title = db.Column(db.String())
    timestamp = db.Column(db.DateTime())
    is_public = db.Column(db.Boolean(), default = True) #Public, Hidden, Private, Password
    has_password = db.Column(db.Boolean(), default = False)
    pw_hash = db.Column(db.String())
    background_color = db.Column(db.String(), default = "#fff")
    font_family = db.Column(db.String(), default ="")
    font_color = db.Column(db.String(), default = "#333333")
    collection_layout = db.Column(db.String(), default = "col-sm-4")
    collection_items = db.relationship("CollectionItem", backref = 'parent', lazy = 'dynamic', cascade="all, delete-orphan")

    def __init__(self):
        self.unique_id = self.create_unique_id()

    def __repr__(self):
        '<Collection %r>' % (str(self.id))

    def create_unique_id(self, size=9):
        chars = string.ascii_lowercase + string.digits
        uid = ''.join(random.SystemRandom().choice(chars) for i in xrange(size))
        return uid

    # def publish_collection(self):
    #     if not self.title:
    #         return False
    #     else:
    #         self.is_published = True
    #         db.session.add(self)
    #         db.session.commit()
    #         return self

    def append_child(self, item):
        self.collection_items.append(item)
        return self

    def fmt_timestamp(self):
        ts = self.timestamp
        return ts.strftime("%d %B %Y")

class CollectionItem(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    parent_collection_id = db.Column(db.Integer, db.ForeignKey('collection.id'))
    content = db.Column(db.String())

    def __init__(self, parent, content):
        self.parent = parent
        self.content = content

    def __repr__(self):
        '<CollectionItem %r>' % (self.title)

    def render(self):
        rv = client.get_content(self.content)
        return rv
