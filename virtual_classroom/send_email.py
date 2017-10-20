from __future__ import print_function
from getpass import getpass
from smtplib import SMTP, SMTP_SSL
from datetime import datetime
from email.encoders import encode_base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from sys import exit
from os import path

# Local imports
from .parameters import get_parameters

try:
  from docutils import core
except ImportError:
  print('docutils is required, exiting.\n\n sudo pip install docutils')
  exit(1)

try:
    import jinja2
except ImportError:
    print("jinja2 is required, exiting.\n\n sudo pip install jinja2")
    exit(1)

# Python3 and 2 compatible
try: input = raw_input
except NameError: pass


def connect_to_email_server(smtp=None):
    """Connects to an email server. Prompting for login information.
    
    Parameters
    ----------
    smtp : str, optional
        Name of the smtp server (uio or google).
        If not specified it will use "smtp" in default parameters.

    Returns
    -------
    EmailServer
        An instance that holds the email server connection.

    """
    parameters = get_parameters()
    smtp = parameters["smtp"] if smtp is None else smtp
    # Set up e-mail server
    if smtp == 'google':
        server = SMTPGoogle()
    elif smtp == 'uio':
        server = SMTPUiO()
    return server


class EmailServer(object):
  """
  Class holds a connection to an email server to avoid closing and opening
  connections for each mail.
  """
  def __init__(self, smtp_server, port):
    self.smtp_server, self.port = smtp_server, port

    tries = 0
    while tries < 3:
        # Get username and password from user
        self.username = input("\nFor %s\nUsername: " % smtp_server)
        self.password = getpass("Password:")
        if self.login():
            return
        tries += 1
    print("Too many tries. Exiting...")
    exit(1)

  def login(self):
    raise NotImplementedError("Only use subclasses of EmailServer.")

  def logout(self):
    """
    Closes connection to the smtp server.
    """
    self.server.quit()


class SMTPGoogle(EmailServer):
  """
  Contains a google smtp server connection.
  """
  def __init__(self):
    super(SMTPGoogle, self).__init__('smtp.gmail.com', 587)
    self.email = self.username

  def login(self):
    try:
      self.server = SMTP(self.smtp_server, self.port)
      self.server.starttls()
      self.server.login(self.username, self.password)
      return True
    except Exception as e:
      print('Username or password is wrong for %s, please try again!'\
          % self.username)
      print(e)
      print("")
      print("Maybe you need activate less secure apps on gmail? See https://www.google.com/settings/u/1/security/lesssecureapps")
      return False


class SMTPUiO(EmailServer):
  """
  Class holds a connection to a UiO SMTP server.
  """
  def __init__(self):
    smtp_address = 'smtp.uio.no'
    super(SMTPUiO, self).__init__(smtp_address, 465)
    self.email = input('Email address (%s): ' % smtp_address)

  def login(self):
    try:
      self.server = SMTP_SSL(self.smtp_server, self.port)
      self.server.login(self.username, self.password)
      return True
    except:
      print('Username or password is wrong for %s, please try again!'\
          % self.smtp_server)
      return False


class Email(object):
    def __init__(self, server_connection, email_body, subject=""):
        self.server_connection = server_connection
        self.email_body = email_body
        self.subject = subject

    def send(self, recipients, subject=None, msg=None):
        """Send email

        This method may raise the following exceptions:

         SMTPHeloError          The server didn't reply properly to
                                the helo greeting.
         SMTPRecipientsRefused  The server rejected ALL recipients
                                (no mail was sent).
         SMTPSenderRefused      The server didn't accept the from_addr.
         SMTPDataError          The server replied with an unexpected
                                error code (other than a refusal of
                                a recipient).

        """
        subject = self.subject if subject is None else subject
        msg = self.format_mail(recipients, subject) if msg is None else msg

        failed_deliveries = \
                self.server_connection.server.sendmail(self.server_connection.email,
                                                       recipients, msg.as_string())
        if failed_deliveries:
            print('Could not reach these addresses:', failed_deliveries)
            return False
        else:
            print('Email successfully sent to %s' % recipients)
            return True

    def format_mail(self, recipients, subject):
        if isinstance(recipients, (list, dict, tuple)):
            recipients = ", ".join(recipients)

        # Compose email
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['To'] = recipients
        msg['From'] = self.server_connection.email
        msg.attach(self.email_body.format())
        return msg


class EmailBody(object):
    def __init__(self, filename, params=None):
        self.filename = filename
        self.params = params
        self.cache = True  # Cache pre-formatted content
        self.cached_content = None

    def read(self):
        with open(self.filename, "rb") as f:
            contents = f.read().decode("utf-8")
        return contents

    @staticmethod
    def text_to_html(text):
        """Convert the text to html code"""
        parts = core.publish_parts(source=text, writer_name='html')
        return parts['body_pre_docinfo']+parts['fragment']

    def render(self):
        content = self.cached_content
        if content is None:
            content = jinja2.Template(self.read())

        if self.cache:
            self.cached_content = content
        return content.render(**self.params)

    def format(self):
        body_text = self.render()
        body_text = self.text_to_html(body_text).encode('utf-8')  # ae, o, aa support
        body_text = MIMEText(body_text, 'html', 'utf-8')
        return body_text


