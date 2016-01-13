# Libraries
import logging

from google.appengine.ext import ndb
import hashlib
from google.appengine.api.blobstore import blobstore

user_key = ndb.Key('User', 'default_user')
photo_key = ndb.Key('Photo', 'default_photo')
install_key = ndb.Key('Install', 'default_installation')
token_key = ndb.Key('Token', 'default_token')
photo_view_key = ndb.Key('PhotoView', 'default_photo_view')
photo_user_permission_key = ndb.Key('PhotoUserPermission', 'default_photo_user_permission')


# Data model

# User model
class User(ndb.Model):
    name = ndb.TextProperty(indexed=True)
    password = ndb.TextProperty()
    email = ndb.TextProperty(indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    photo = ndb.IntegerProperty()  # Profile photo id
    background = ndb.IntegerProperty()  # Web page background photo id
    role_level = ndb.IntegerProperty()  # 0 not activated, 1 activated by user, 2 activated by admin, 3 admin account
    attempts = ndb.IntegerProperty()  # Number of attempts before blocking the account


# Token model
class Token(ndb.Model):
    user = ndb.KeyProperty(kind=User, indexed=True)
    date = ndb.DateTimeProperty(auto_now_add=True)
    used = ndb.BooleanProperty(default=False)


# Photo model
class Photo(ndb.Model):
    owner = ndb.KeyProperty(kind=User, indexed=True)
    privacy = ndb.IntegerProperty(indexed=True) # 0 public, 1 selectedUsers, 2 private
    date = ndb.DateTimeProperty(auto_now_add=True)
    name = ndb.TextProperty()
    image = ndb.BlobKeyProperty()


# Album model
class Album(ndb.Model):
    owner = ndb.KeyProperty(kind=User, repeated=True)
    name = ndb.TextProperty(indexed=True)


# Relation between Album and Photo
class AlbumPhoto(ndb.Model):
    album = ndb.KeyProperty(kind=Album, repeated=True)
    photo = ndb.KeyProperty(kind=Photo, repeated=True)

# Relation between User and Photo, a entity refers to a User has permission to watch a Photo
class PhotoUserPermission(ndb.Model):
    photo = ndb.KeyProperty(kind=Photo, indexed=True)
    user = ndb.KeyProperty(kind=User, indexed=True)

# Relation between User and Photo, a entity refers to a User has seen a Photo
class PhotoView(ndb.Model):
    user = ndb.KeyProperty(kind=User, indexed=True)
    photo = ndb.KeyProperty(kind=Photo, indexed=True)

# Save if service is correctly installed (admin account is created)
class Install(ndb.Model):
    installed = ndb.BooleanProperty()


# Installation management
class InstallManager:
    def __init__(self):
        pass

    @staticmethod
    def install():
        install = Install(parent=install_key)
        install.installed = True

        key = install.put()
        return key.id()

    @staticmethod
    def is_installed():
        installed = ndb.gql(
                'SELECT * '
                'FROM Install '
                'WHERE installed = True '
        )
        return installed.get() is not None


# Manages users: create, delete, select, modify
class UserManager:
    def __init__(self):
        pass

    @staticmethod
    def create(username, password, email):
        return UserManager.create_user(username, password, email, role_level=0)

    @staticmethod
    def create_admin(username, password, email):
        return UserManager.create_user(username, password, email, role_level=3)

    @staticmethod
    def create_user(username, password, email, role_level):
        user = User(parent=user_key)

        user.name = username
        user.password = hashlib.sha1(password).hexdigest()
        user.email = email
        user.role_level = role_level
        user.attempts = 0  # First time user has not any login attempt

        key = user.put()
        return key

    @staticmethod
    def modify_user(key,
                    username=None,
                    password=None,
                    email=None,
                    role_level=None,
                    photo=None,
                    background=None,
                    attempts=None):

        user = key.get()

        if username is not None:
            user.name = username
        if password is not None:
            user.password = hashlib.sha1(password).hexdigest()
        if email is not None:
            user.email = email
        if role_level is not None:
            user.role_level = role_level
        if photo is not None:
            user.photo = photo
        if background is not None:
            user.background = background
        if attempts is not None:
            user.attempts = attempts

        user.put()

    @staticmethod
    def remove_user(key):
        key.remove()

    @staticmethod
    def select():
        users = ndb.gql(
                'SELECT * '
                'FROM User '
                'WHERE ANCESTOR IS :1 '
                'ORDER BY date DESC',
                user_key
        )

        return users

    @staticmethod
    def select_by_username(username):
        user = ndb.gql(
                'SELECT * '
                'FROM User '
                'WHERE name = :1 '
                'ORDER BY date DESC',
                username
        )
        return user.get()

    @staticmethod
    def select_by_email(email):
        user = ndb.gql(
                'SELECT * '
                'FROM User '
                'WHERE email = :1 '
                'ORDER BY date DESC',
                email
        )
        return user.get()

    @staticmethod
    def select_by_id(id):
        return User.get_by_id(id, parent=user_key)


class TokenManager:
    def __init__(self):
        pass

    @staticmethod
    def create_token(user):
        token = Token(parent=token_key)
        token.user = user

        key = token.put()
        return key

    @staticmethod
    def select_token_by_id(token_id):
        return Token.get_by_id(token_id, parent=token_key)

    @staticmethod
    def set_used_token(key):
        token = key.get()
        token.used = True
        token.put()
        return token.key


class PhotosManager:
    def __init__(self):
        pass

    @staticmethod
    def createPhoto(name, owner, privacy, image_key):
        photo = Photo(parent=photo_key)

        photo.name = name
        photo.owner = owner
        photo.privacy = privacy
        photo.image = image_key

        key = photo.put()

        return key.id()

    @staticmethod
    def retrieveAllPhotos():
        photos = ndb.gql(
                'SELECT *'
                'FROM Photo '
                'WHERE ANCESTOR IS :1 '
                'ORDER BY date ASC',
                photo_key
        )
        return photos

    @staticmethod
    def modify_photo(key, name=None, privacy=None):
        # Retrieve object to modify
        photo = key.get()
        # Modify setted values
        if name is not None:
            photo.name = name
        if privacy is not None:
            photo.privacy = privacy
        # Apply changes
        photo.put()

    @staticmethod
    def get_photo_by_id(photo_id):
        return Photo.get_by_id(photo_id, parent=photo_key)

    @staticmethod
    def delete_photo(photo_id):
        # Retrieve photo
        photo = PhotosManager.get_photo_by_id(photo_id)
        # Remove blob
        blobstore.delete(photo.image)
        # Remove photo
        photo.key.delete()


class PhotoViewManager:
    def __init__(self):
        pass

    @staticmethod
    def newView(photo, user=None):
        photo_view = PhotoView(parent=photo_view_key)

        photo_view.photo = photo.key
        if user is None:
            photo_view.user = None
        else:
            photo_view.user = user.key

        photo_view.put()

    @staticmethod
    def select_users_by_photo(photo):
        users = ndb.gql(
                'SELECT user '
                'FROM PhotoView '
                'WHERE photo = :1 '
                'ORDER BY user ASC',
                photo.key
        )
        return users


class PhotoUserPermissionManager:
    def __init__(self):
        pass

    @staticmethod
    def give_permission(photo, user):

        # Check if permission already exists
        permission = PhotoUserPermissionManager.get_user_photo_pair(photo, user)
        if permission is not None:
            return None  # Do anything if permission is already set

        # Create new permission
        photo_user_permission = PhotoUserPermission(parent=photo_user_permission_key)
        photo_user_permission.photo = photo.key
        photo_user_permission.user = user.key

        key = photo_user_permission.put()

        return key

    @staticmethod
    def restrict_permission(photo, user):
        permission = PhotoUserPermissionManager.get_user_photo_pair(photo, user)
        # Remove permission if exists
        if permission is not None:
            permission.key.delete()
            return True
        return False

    @staticmethod
    def get_user_photo_pair(photo, user):
        user_photo_permission = ndb.gql(
                'SELECT * '
                'FROM PhotoUserPermission '
                'WHERE photo = :1 AND user = :2',
                photo.key, user.key
        )
        return user_photo_permission.get()

    @staticmethod
    def get_allowed_users_by_photo(photo):
        photokey = photo.key

        users = ndb.gql(
                'SELECT * '
                'FROM PhotoUserPermission '
                'WHERE photo = :1 '
                'ORDER BY user ASC',
                photokey
        )
        return users