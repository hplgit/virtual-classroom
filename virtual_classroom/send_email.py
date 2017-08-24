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


class Email():
    def __init__(self, server_connection, filename=None, params=None):
        self.server_connection = server_connection
        self.params = self.extract_params(params)
        self.filename = filename

    @staticmethod
    def extract_params(params):
        if isinstance(params, dict) or params is None:
            return params
        else:
            return params.__dict__

    def get_text(self, filename=None):
        """Read the given file"""
        filename = self.filename if filename is None else filename
        with open(filename, 'r') as f:
            text = f.read()
        return text

    @staticmethod
    def rst_to_html(text):
        """Convert the .rst file to html code"""
        parts = core.publish_parts(source=text, writer_name='html')
        return parts['body_pre_docinfo']+parts['fragment']

    def new_student(self, student):
        """Compose an email for the event that a new student is added to
        the course"""
        text = self.get_text('message_new_student.rst')

        # Variables for the email
        recipient = student.email
        email_var = {}
        email_var['year'] = datetime.now().year
        email_var['name'] = student.name.split(' ')[0]
        email_var['course'] = student.course
        email_var['university'] = student.university
        email_var['repo_name'] = student.repo_name
        email_var['repo_adress'] = 'git@github.com:/%s/%s.git' % \
                                        (student.org, student.repo_name)

        # Compose message
        text = self.get_text('message_new_student.rst')
        text = text % email_var
        text = self.rst_to_html(text).encode('utf-8') # ae, o, aa support

        # Compose email
        msg = MIMEMultipart()
        msg['Subject']  = 'New repository'
        msg['To'] = recipient
        msg['From'] = self.server_connection.email
        body_text = MIMEText(text, 'html', 'utf-8')
        msg.attach(body_text)

        self.send(msg, recipient)

    def new_group(self, team_name, review_group, eval_group):
        """Compose an email for the event that some collaboration has started."""
        # Variables for the email
        email_var = {}
        get_repos = ""
        correcting_names = ""
        for student in eval_group:
            correcting_names += " "*4 + "* %s\n" % student.name
            get_repos += ' '*4 + 'git clone git@github.com:%s/%s\n' % \
                                       (student.org, student.repo_name)
            get_repos_https = ' '*4 + 'git clone https://github.com/%s/%s\n' % \
                                        (student.org, student.repo_name)
            print(student.name)
            print(student.repo_name)

        #get_repos += ' '*4 + "git clone git@github.com:UiO-INF5620/Solutions\n"
        email_var['get_repos'] = get_repos
        email_var['get_repos_https'] = get_repos_https
        email_var['correcting_names'] = correcting_names
        email_var['team_name'] = team_name
        email_var['team_url'] = 'https://github.com/orgs/UiO-INF3331/teams/{}/repositories'.format(team_name)
        email_var['course'] = review_group[0].course

        for student in review_group:
            recipient = student.email
            email_var['name'] = student.name.split(' ')[0]
            rest_of_group = [s.name for s in review_group if s.name != student.name]
            email_var['team_emails'] = "".join([" "*4 + "* " + s.email + '\n' for s in \
                                            review_group if s.name != student.name])
            if len(rest_of_group) > 0:
                email_var['group_names'] = ", ".join(rest_of_group[:-1]) + " and " + \
                                           rest_of_group[-1]
            else:
                email_var['group_names'] = ""

            # Compose message
            text = self.get_text('message_collaboration.rst')
            text = text.format(**email_var)
            text = self.rst_to_html(text).encode('utf-8') # ae, o, aa support

            # Compose email
            msg = MIMEMultipart()
            msg['Subject']  = 'New group'
            msg['To'] = recipient
            msg['From'] = self.server_connection.email
            body_text = MIMEText(text, 'html', 'utf-8')
            msg.attach(body_text)

            # Attach template for feedback
            # TODO: Make it possible to change the name and location
            #       of the attachment.
            #path_dir = path.join(path.dirname(__file__), "feedback_template.tex")
            #if path.isfile("feedback_template.tex"):
            #    fileMsg = MIMEBase('application','octet-stream')
            #    fileMsg.set_payload(open('./feedback_template.tex', 'rb').read())
            #    encode_base64(fileMsg)
            #    fileMsg.add_header('Content-Disposition',
            #                        'attachment;filename=Feedback_template.tex')
            #    msg.attach(fileMsg)

            self.send(msg, recipient)

    def send(self, recipients, msg=None, subject="", params=None):
        """Send email"""
        if msg is None or params is not None:
            msg = self.format_mail(recipients, text=msg, subject=subject, params=params)

        failed_deliveries = \
                self.server_connection.server.sendmail(self.server_connection.email,
                                                       recipients, msg.as_string())
        if failed_deliveries:
            print('Could not reach these addresses:', failed_deliveries)
        else:
            print('Email successfully sent to %s' % recipients)

    def format_body(self, filename=None, text=None, params=None):
        text = self.get_text(filename=filename) if text is None else text
        params = self.params if params is None else self.extract_params(params)

        text = text.format(**params)
        text = self.rst_to_html(text).encode('utf-8')  # ae, o, aa support
        body_text = MIMEText(text, 'html', 'utf-8')
        return body_text

    def format_mail(self, recipients, text=None, subject="", params=None):
        body_text = self.format_body(text=text, params=params)
        if isinstance(recipients, (list, dict, tuple)):
            recipients = ", ".join(recipients)

        # Compose email
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['To'] = recipients
        msg['From'] = self.server_connection.email
        msg.attach(body_text)
        return msg


class Email(object):
    def __init__(self, server_connection, email_body, subject=""):
        self.server_connection = server_connection
        self.email_body = email_body
        self.subject = subject

    def send(self, recipients, subject=None, msg=None):
        """Send email"""
        subject = self.subject if subject is None else subject
        msg = self.format_mail(recipients, subject) if msg is None else msg

        failed_deliveries = \
                self.server_connection.server.sendmail(self.server_connection.email,
                                                       recipients, msg.as_string())
        if failed_deliveries:
            print('Could not reach these addresses:', failed_deliveries)
        else:
            print('Email successfully sent to %s' % recipients)

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
        with open(self.filename, "r") as f:
            contents = f.read()
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


