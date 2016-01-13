# Jinja templates
import os
import jinja2
# Database access
import database
# Remote services
import urllib
# JSON library
import json
# Session handler
import session
from session import SessionManager as Session
# Email handler
import email_handler

import security

# Blobstore
from google.appengine.api.blobstore import blobstore
from google.appengine.ext import blobstore as blobstore_2

JINJA_ENVIRONMENT = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
        extensions=['jinja2.ext.autoescape'],
        autoescape=True)


class ApiRegister(session.BaseSessionHandler):
    def get(self, option):
        # Load response template
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')
        self.response.headers['Content-Type'] = 'application/json'
        if option == "emailExists":
            email = self.request.get("q")
            user = database.UserManager.select_by_email(email)
            if user is not None:
                data = '{"email": "' + email + '", "exists": true}'
            else:
                data = '{"email": "' + email + '", "exists": false}'
            result = "OK"
        elif option == "userExists":
            username = self.request.get("q")
            user = database.UserManager.select_by_username(username)
            if user is not None:
                data = '{"username": "' + username + '", "exists": true}'
            else:
                data = '{"username": "' + username + '", "exists": false}'
            result = "OK"
        else:
            data = '{"error": "Method not allowed"}'
            result = "FAIL"
        self.response.write(template.render(feature="register",
                                            data=data,
                                            query=self.request.url,
                                            result=result))


class ApiMap(session.BaseSessionHandler):
    def get(self, option):
        # Load response template
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')
        self.response.headers['Content-Type'] = 'application/json'
        if option == "searchSite":
            # Ask google maps API for location
            service_url = 'http://maps.googleapis.com/maps/api/geocode/json?'
            address = self.request.get('q')
            url = service_url + urllib.urlencode({'address': address})
            uh = urllib.urlopen(url)
            data = uh.read()
            js = json.loads(data)
            # Purge result and prepare response
            query_result = js['status']
            if query_result == "OK":
                address = js['results'][0]['formatted_address']
                lat = js['results'][0]['geometry']["location"]["lat"]
                lng = js['results'][0]['geometry']["location"]["lng"]
                data = '{"site":"' + address + '", "lat": ' + str(lat) + ', "lng": ' + str(lng) + '}'
                result = "OK"
            elif query_result == "ZERO_RESULTS":
                data = '{"error": "Site not found"}'
                result = "FAIL"
            else:
                data = '{"error": "Unknown error"}'
                result = "FAIL"
            # Write response
            self.response.write(template.render(feature="map",
                                                data=data,
                                                query=self.request.url,
                                                result=result))


class ApiPhotosUpload(session.BlobUploadSessionHandler):
    def post(self):
        # Load response template
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')
        self.response.headers['Content-Type'] = 'application/json'
        # Session request handler
        current_session = Session(self)

        # Retrieve uploaded info
        upload_files = self.get_uploads("file")
        blob_info = upload_files[0]

        # Check if user can upload the photo
        if current_session.get_role_level() < 2:
            self.response.headers['Content-Type'] = 'application/json'
            data = '{"error": "Permission denied"}'
            result = "FAIL"
            self.response.write(template.render(feature="photo",
                                                data=data,
                                                query=self.request.url,
                                                result=result))
            # Remove photo from blob store
            blobstore.delete(blob_info.key)
            return None

        # Save photo to database
        photo_id = database.PhotosManager.createPhoto("", current_session.get_user_key(), 2, blob_info.key())
        # Prompt response to user
        data = '{"photo_id": ' + str(photo_id) + '}'
        result = "OK"
        self.response.write(template.render(feature="photo", data=data, query=self.request.url, result=result))


class ApiPhotosUploadPath(session.BlobUploadSessionHandler):
    def get(self):
        # Load response template
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')
        self.response.headers['Content-Type'] = 'application/json'
        # Retrieve a new session path to upload
        upload_url = blobstore.create_upload_url('/api/photos/upload')
        data = '{"url": "' + upload_url + '"}'
        self.response.write(template.render(feature="photo", data=data, query=self.request.url, result="OK"))


class ApiPhotoDownload(session.BlobDownloadSessionHandler):
    def get(self, photo_id):
        # Session
        current_session = Session(self)
        # Load response template
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')

        # Retrieve photo url for photo_id
        photo = database.PhotosManager.get_photo_by_id(int(photo_id))
        if current_session.get_id() is None:
            user = None
        else:
            user = database.UserManager.select_by_id(current_session.get_id())

        if not photo:
            self.response.write("No photo")
        elif not blobstore_2.get(photo.image):
            self.response.write("No blob")
        else:
            # Check visualization permissions to current user
            if security.PhotoSecurity.user_is_allowed_to_watch_photo(photo, user):
                self.send_blob(photo.image)
            else:
                self.error(404)


class ApiUserManagement(session.BaseSessionHandler):
    def post(self, user_id, option):
        # Session
        current_session = Session(self)
        # Load response template
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')
        self.response.headers['Content-Type'] = 'application/json'
        # Check if request is done by admin or himself
        user_id = int(user_id)
        if current_session.get_role_level() < 3 and current_session.get_id() != user_id:
            role_level = str(current_session.get_role_level())
            data = '{"error": "Permission denied"}'
            result = "FAIL"
            self.response.write(template.render(feature="user",
                                                data=data,
                                                query=self.request.url,
                                                result=result))
            return None
        # Check if user exists
        user = database.UserManager.select_by_id(int(user_id))
        # If user not exists
        if user is None:
            data = '{"error": "User not exists."}'
            result = "FAIL"
            self.response.write(template.render(feature="user",
                                                data=data,
                                                query=self.request.url,
                                                result=result))
            return None

        # Options
        if option == "changeUserData":  # update email and user
            email = self.request.get("email", None)
            username = self.request.get("username", None)
            background = self.request.get("background", None)
            photo_id = self.request.get("photo", None)

            if email is not None:
                userbyemail = database.UserManager.select_by_email(email)
                if userbyemail is None:
                    database.UserManager.modify_user(user.key, email=email)
                else:
                    data = '{"error": "Field exists", "field": "email"}'
                    result = "FAIL"
                    self.response.write(template.render(feature="user", data=data, query=self.request.url, result=result))

            if username is not None:
                userbyname = database.UserManager.select_by_username(username)
                if userbyname is None:
                    database.UserManager.modify_user(user.key, username=username)
                else:
                    data = '{"error": "Field exists", "field": "username"}'
                    result = "FAIL"
                    self.response.write(template.render(feature="user", data=data, query=self.request.url, result=result))
            if background is not None:
                # Check if photo exists
                background_photo = database.PhotosManager.get_photo_by_id(int(background))
                if background_photo is not None:
                    # Change user background image
                    database.UserManager.modify_user(user.key, background=background_photo.key.id())
                else:
                    data = '{"error": "Field not exists", "field": "background"}'
                    result = "FAIL"
                    self.response.write(template.render(feature="user", data=data, query=self.request.url, result=result))
            if photo_id is not None:
                # Check if photo exists
                photo = database.PhotosManager.get_photo_by_id(int(photo_id))
                if photo is not None:
                    # Change user background image
                    database.UserManager.modify_user(user.key, photo=photo.key.id())
                else:
                    data = '{"error": "Field not exists", "field": "background"}'
                    result = "FAIL"
                    self.response.write(template.render(feature="user", data=data, query=self.request.url, result=result))
            data = '{"message": "User updated"}'
            result = "OK"
            self.response.write(template.render(feature="user", data=data, query=self.request.url, result=result))

    def get(self, user_id, option):
        # Session
        current_session = Session(self)
        # Load response template
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')
        self.response.headers['Content-Type'] = 'application/json'
        user_id = int(user_id)
        # If user is not admin and not himself, not allow to query anything
        if current_session.get_role_level() < 3 and current_session.get_id() != user_id:
            role_level = str(current_session.get_role_level())
            data = '{"error": "Permission denied' + role_level + '"}'
            result = "FAIL"
            self.response.write(template.render(feature="user",
                                                data=data,
                                                query=self.request.url,
                                                result=result))
            return None
        # Check if user exists
        user = database.UserManager.select_by_id(int(user_id))
        # If user not exists
        if user is None:
            data = '{"error": "User not exists."}'
            result = "FAIL"
            self.response.write(template.render(feature="user",
                                                data=data,
                                                query=self.request.url,
                                                result=result))
            return None

        # Options
        if option == "activateAccountByAdmin":
            # Only admin is allowed to change permissions
            if current_session.get_role_level() < 3:
                data = '{"error": "You cannot change your permission level."}'
                result = "FAIL"
                self.response.write(template.render(feature="user",
                                                    data=data,
                                                    query=self.request.url,
                                                    result=result))
                return None
            # If user has not his account activated, admin cannot active it
            if user.role_level != 1:
                data = '{"error": "User has not his account activated yet."}'
                result = "FAIL"
                self.response.write(template.render(feature="user",
                                                    data=data,
                                                    query=self.request.url,
                                                    result=result))
                return None
            # Activate account by admin
            database.UserManager.modify_user(user.key, role_level=2)
            data = '{"message": "Account activated by admin."}'
            result = "OK"
        elif option == "deactivateAccountByAdmin":
            # Only admin is allowed to change permissions
            if current_session.get_role_level() < 3:
                data = '{"error": "You cannot change your permission level."}'
                result = "FAIL"
                self.response.write(template.render(feature="user",
                                                    data=data,
                                                    query=self.request.url,
                                                    result=result))
                return None
            # If user has not his account activated, admin cannot active it
            if user.role_level != 2:
                data = '{"error": "User account can not deactivated."}'
                result = "FAIL"
                self.response.write(template.render(feature="user",
                                                    data=data,
                                                    query=self.request.url,
                                                    result=result))
                return None
            # Activate account by admin
            database.UserManager.modify_user(user.key, role_level=1)
            data = '{"message": "Account deactivated by admin."}'
            result = "OK"
        elif option == "blockAccount":
            # Only admin is allowed to block account
            if current_session.get_role_level() < 3:
                data = '{"error": "You cannot change your block status."}'
                result = "FAIL"
                self.response.write(template.render(feature="user",
                                                data=data,
                                                query=self.request.url,
                                                result=result))
                return None
            # No anyone is allowed to block an admin
            if user.role_level == 3:
                data = '{"error": "You cannot block an admin account."}'
                result = "FAIL"
                self.response.write(template.render(feature="user",
                                                    data=data,
                                                    query=self.request.url,
                                                    result=result))
                return None
            database.UserManager.modify_user(user.key, attempts=3)  # Account is blocked with 3 attempts
            data = '{"message": "Account blocked by admin."}'
            result = "OK"
        elif option == "unblockAccount":
            # Only admin is allowed to unblock account
            if current_session.get_role_level() < 3:
                data = '{"error": "You cannot change your permission level."}'
                result = "FAIL"
                self.response.write(template.render(feature="user",
                                                    data=data,
                                                    query=self.request.url,
                                                    result=result))
                return None
            database.UserManager.modify_user(user.key, attempts=0)  # Account is unblocked with 0 attempts
            data = '{"message": "Account unblock by admin."}'
            result = "OK"
        elif option == "profileChangeRequest":
            # Only user himself is allowed to change profile
            if current_session.get_id() == user_id:
                token = database.TokenManager.create_token(user.key)
                email_handler.Email.send_change_profile(user.name, token.id(), user.email)
                data = '{"message": "Change profile email send"}'
                result = "OK"
        else:
            data = '{"error": "Method not allowed"}'
            result = "FAIL"
        self.response.write(template.render(feature="user", data=data, query=self.request.url, result=result))


class ApiUserRecover(session.BaseSessionHandler):
    def get(self, username):
        # Load response template
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')
        self.response.headers['Content-Type'] = 'application/json'

        user = database.UserManager.select_by_username(username)
        if user is not None:
            token = database.TokenManager.create_token(user.key)
            email_handler.Email.send_change_profile(user.name, token.id(), user.email)
            data = '{"message": "Change profile email send"}'
            result = "OK"
        else:
            data = '{"error": "User not exists"}'
            result = "ERROR"
        self.response.write(template.render(feature="user", data=data, query=self.request.url, result=result))

class ApiPhotosManager(session.BaseSessionHandler):
    def get(self, option):
        # Session
        current_session = Session(self)
        # Load response template
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')
        self.response.headers['Content-Type'] = 'application/json'

        if option == "list":
            # List all accesible photos
            photos = database.PhotosManager.retrieveAllPhotos()
            if current_session.get_id() is None:
                user = None
            else:
                user = database.UserManager.select_by_id(current_session.get_id())
            data = '{"photos":['
            isAnyPhotoAllowed = False
            for photo in photos:
                if security.PhotoSecurity.user_is_allowed_to_watch_photo(photo, user):  # Check user has permission to retrieve
                    isAnyPhotoAllowed = True
                    id = photo.key.id()
                    username = photo.owner.get().name
                    date = photo.date
                    name = photo.name
                    data += '{"photo_id": ' + str(id) + ', "username": "' + username + '", "date": "' + str(
                        date) + '", "name": "' + name + '"},'
            if isAnyPhotoAllowed:
                data = data[:-1]
            data += ']}'
            result = "OK"
        else:
            # Print method not allowed
            data = '{"error": "Method not allowed"}'
            result = "FAIL"
        self.response.write(template.render(feature="user", data=data, query=self.request.url, result=result))


class ApiPhotoModify(session.BaseSessionHandler):
    def post(self, photo_id):
        # Session
        current_session = Session(self)
        # Load response template
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')
        self.response.headers['Content-Type'] = 'application/json'

        photo = database.PhotosManager.get_photo_by_id(int(photo_id))

        if photo is None:
            data = '{"error": "Photo does not exist."}'
            result = "FAIL"
        else:
            # Check permission for this petition (only owner or admin can modify)
            if(photo.owner == current_session.get_user_key()) or (current_session.get_role_level() > 2):
                name = self.request.get('name')
                privacy = int(self.request.get('privacy'))
                database.PhotosManager.modify_photo(photo.key, name, privacy)
                data = '{"message": "Changes done"}'
                result = "OK"
            else:
                data = '{"error": "No permission to change."}'
                result = "FAIL"
        # Response result json
        self.response.write(template.render(feature="user", data=data, query=self.request.url, result=result))


class ApiPhotoDelete(session.BaseSessionHandler):
    def get(self, photo_id):
        # Session
        current_session = Session(self)
        # Load response template
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')
        self.response.headers['Content-Type'] = 'application/json'

        photo = database.PhotosManager.get_photo_by_id(int(photo_id))

        if photo is None:
            data = '{"error": "Photo does not exist."}'
            result = "FAIL"
        else:
            # Check permission for this petition (only owner or admin can modify)
            if(photo.owner == current_session.get_user_key()) or (current_session.get_role_level() > 2):
                database.PhotosManager.delete_photo(int(photo_id))
                data = '{"message": "Foto deleted."}'
                result = "OK"
            else:
                data = '{"error": "No permission to change."}'
                result = "FAIL"

        # Response result json
        self.response.write(template.render(feature="user", data=data, query=self.request.url, result=result))


class ApiPhotoUserPermission(session.BaseSessionHandler):
    def get(self, user_id, photo_id, option):
        # Session
        current_session = Session(self)
        # Load response template
        template = JINJA_ENVIRONMENT.get_template('static/templates/api.json')
        self.response.headers['Content-Type'] = 'application/json'

        # Check if user and photo exists
        photo = database.PhotosManager.get_photo_by_id(int(photo_id))
        user = database.UserManager.select_by_id(int(user_id))

        if photo is None:
            data = '{"error": "Photo does not exist."}'
            result = "FAIL"
        elif user is None:
            data = '{"error": "User does not exist."}'
            result = "FAIL"
        else:
            # Check permission for this petition (only owner or admin can modify)
            if(photo.owner == current_session.get_user_key()) or (current_session.get_role_level() > 2):
                if option == "give":
                    result = database.PhotoUserPermissionManager.give_permission(photo, user)
                    if result is None:
                        data = '{"error": "Permission already set."}'
                        result = "FAIL"
                    else:
                        data = '{"message": "Permission allowed."}'
                        result = "OK"
                elif option == "restrict":
                    result = database.PhotoUserPermissionManager.restrict_permission(photo, user)
                    if result is True:
                        data = '{"message": "Permission restricted."}'
                        result = "OK"
                    else:
                        data = '{"error": "Permission is not set. Cannot restrict"}'
                        result = "FAIL"
            else:
                data = '{"error": "Permission denied. Operation cannot do."}'
                result = "FAIL"

        # Response result json
        self.response.write(template.render(feature="user", data=data, query=self.request.url, result=result))
