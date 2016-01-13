import webapp2

# Jinja templates
import os
import jinja2

# Server url
from google.appengine.api import app_identity

from google.appengine.api.blobstore import blobstore
from google.appengine.ext import vendor

# Add language compatibility
vendor.add('lib')
from webapp2_extras import i18n
from webapp2_extras.i18n import gettext as _

# Email send library
from google.appengine.api import mail



JINJA_ENVIRONMENT = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
        extensions=['jinja2.ext.autoescape', 'jinja2.ext.i18n'],
        autoescape=True)

JINJA_ENVIRONMENT.install_gettext_translations(i18n)


import logging


class Email:
    def __init__(self):
        pass

    @staticmethod
    def send_activation(username, token, receiver_email):
        mail.is_email_valid(receiver_email)
        sender_address = "HaritzMedina-KaixoMundua <haritzmedina-kaixomundua@appspot.gserviceaccount.com>"
        subject = _("ConfirmRegistration")
        template = JINJA_ENVIRONMENT.get_template('static/templates/activationEmail.txt')
        link = "http://" + app_identity.get_default_version_hostname() + "/activate/" + str(token)
        body = template.render(link=link)

        # TODO Remove logging
        logging.info(body)

        mail.send_mail(sender_address,
                       receiver_email,
                       subject,
                       body)
    @staticmethod
    def send_change_profile(username, token, receiver_email):
        mail.is_email_valid(receiver_email)
        sender_address = "HaritzMedina-KaixoMundua <haritzmedina-kaixomundua@appspot.gserviceaccount.com>"
        subject = _("ChangeProfile")
        template = JINJA_ENVIRONMENT.get_template('static/templates/changeProfile.txt')
        link = "http://" + app_identity.get_default_version_hostname() + "/profile/change/" + str(token)

        body = template.render(link=link)

        # TODO Remove logging
        logging.info(body)

        mail.send_mail(sender_address,
                       receiver_email,
                       subject,
                       body)
