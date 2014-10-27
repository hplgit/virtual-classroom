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

try:
  from docutils import core
except ImportError:
  print('docutils is required, exiting.\n\n sudo pip install docutils')
  exit(1)

# Python3 and 2 compatible
try: input = raw_input
except NameError: pass

class EmailServer(object):
  """
  Class holds a connection to an email server to avoid closing and opening
  connections for each mail.
  """
  def __init__(self, smtp_server, port):
    self.smtp_server, self.port = smtp_server, port

    """Get username and password from user"""
    self.username = input("\nFor %s\nUsername: " % smtp_server)
    self.password = getpass("Password:")

    self.login()

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
    super(SMTPGoogle, self).__init__('smtp.gmail.com',587)
    self.email = self.username

  def login(self):
    try:
      self.server = SMTP(self.smtp_server, self.port)
      self.server.starttls()
      self.server.login(self.username, self.password)
    except:
      print('Username or password is wrong for %s, please try again!'\
          % smtp_server)
      exit(1)

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
    except:
      print('Username or password is wrong for %s, please try again!'\
          % self.smtp_server)
      exit(1)

class Email():
    def __init__(self, server_connection):
        self.server_connection = server_connection

    def get_text(self, filename):
        """Read the given file"""
        file = open(filename, 'r')
        text = file.read()
        file.close()
        return text

    def logout(self):
        """
        Logs out of currently open e-mail server connection. Only call
        when sending is finished.
        """
        self.server_connection.logout()
    
    def rst_to_html(self, text):
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

    def new_group(self, group, team_name, correcting):
        """Compose an email for the event that some collaboration has started."""
        # Variables for the email
        email_var = {}
        get_repos = ""
        correcting_names = ""
        for student in correcting:
            correcting_names += " "*4 + "* %s\n" % student.name
            get_repos += ' '*4 + 'git clone git@github.com:%s/%s\n' % \
                                       (student.org, student.repo_name)
            get_repos_https = ' '*4 + 'git clone https://github.com/%s/%s\n' % \
                                        (student.org, student.repo_name)

        email_var['get_repos'] = get_repos
        email_var['get_repos_https'] = get_repos_https
        email_var['correcting_names'] = correcting_names
        email_var['team_name'] = team_name
        email_var['course'] = group[0].course

        for student in group:
            recipient = student.email
            email_var['name'] = student.name.split(' ')[0]
            rest_of_group = [s.name for s in group if s.name != student.name]
            email_var['team_emails'] = "".join([" "*4 + "* " + s.email + '\n' for s in \
                                            group if s.name != student.name])
            email_var['group_names'] = ", ".join(rest_of_group[:-1]) + " and " + \
                                       rest_of_group[-1]

            # Compose message
            text = self.get_text('message_collaboration.rst')
            text = text % email_var
            text = self.rst_to_html(text).encode('utf-8') # ae, o, aa support

            # Compose email       
            msg = MIMEMultipart()
            msg['Subject']  = 'New group'
            msg['To'] = recipient
            msg['From'] = self.username
            body_text = MIMEText(text, 'html', 'utf-8')
            msg.attach(body_text)

            # Attach template for feedback
            if path.isfile(args.f):
                fileMsg = MIMEBase('application','octet-stream')
                fileMsg.set_payload(open('./feedback_template.txt', 'rb').read())
                encode_base64(fileMsg)
                fileMsg.add_header('Content-Disposition','attachment;filename=Feedback_template.txt')
                msg.attach(fileMsg)

            self.send(msg, recipient)

    def send(self, msg, recipients):
        """Send email"""
        failed_deliveries = self.server_connection.server.sendmail(self.username, recipients, msg.as_string())
        if failed_deliveries:
            print('Could not reach these addresses:', failed_deliveries)
        else:
            print('Email successfully sent to %s' % recipients)
