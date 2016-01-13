# Import sessions for session handling
import webapp2
from google.appengine.ext.webapp import blobstore_handlers
from webapp2_extras import sessions

# Import users database access
import database


class SessionKeyManager:
    def __init__(self):
        pass

    @staticmethod
    def get():
        f = open("key/sessionSeed.key")
        return f.read()


# This is needed to configure the session secret key
# Runs first in the whole application
myconfig_dict = {'webapp2_extras.sessions': {
    'secret_key': SessionKeyManager.get(),
}}


# Session Handling class, gets the store, dispatches the request
class BaseSessionHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()
        # End of BaseSessionHandler Class


# Session Handling class for blob uploading content
class BlobUploadSessionHandler(blobstore_handlers.BlobstoreUploadHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()
        # End of BaseSessionHandler Class


# Session Handling class for blob downloading content
class BlobDownloadSessionHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()
        # End of BaseSessionHandler Class


# Handler for retrieving session info
class SessionManager:
    def __init__(self, http):
        # If user is logged in, retrieve user info
        if http.session.get('userid') is not None:
            self.retrieve_user_data(http.session.get('userid'))
        else:
            self.user = None

    def get_user_key(self):
        if self.user is not None:
            return self.user.key
        return None

    def get_id(self):
        if self.user is not None:
            return self.user.key.id()
        return None

    def get_username(self):
        if self.user is not None:
            return self.user.name
        return None

    def get_role_level(self):
        if self.user is not None:
            return self.user.role_level
        return None

    def get_user_email(self):
        if self.user is not None:
            return self.user.email
        return None

    def get_user_background(self):
        if self.user is not None:
            return self.user.background
        return None

    def set(self, http, user_id):
        http.session['userid'] = user_id
        self.retrieve_user_data(user_id)

    def retrieve_user_data(self, user_id):
        # If user is logged in, retrieve user info
        if user_id is not None:
            self.user = database.UserManager.select_by_id(user_id)
        else:
            self.user = None


    def logout(self, http):
        if (http.session.has_key('userid')):
            del http.session['userid']
        self.user = None
