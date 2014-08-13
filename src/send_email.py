from __future__ import print_function
import getpass
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Python3 and 2 compatible
try: input = raw_input
except NameError: pass


class Email():

    def __init__(self):
        self.username = input("\nFor Gmail\nEmail address: ")
        self.password = getpass.getpass("Password:")

    def new_student(self, student):
        # Get text
        file = open('message_new_student.txt', 'r')
        text = file.readlines()[0]
        file.close()
   
        recipient = student.email
        email_var = {}
        email_var['name'] = student.name.split(' ')[0]
        email_var['repo_name'] = student.repo_name
        email_var['repo_adress'] = 'https://github.com/%s/%s' % \
                                        (student.org, student.repo_name)
        text = text % email_var

        # Compose email       
        msg = MIMEMultipart()
        msg['Subject']  = 'New repository'
        msg['To'] = recipient
        msg['From'] = self.username
        body_text = MIMEText(text)
        msg.attach(body_text)

        self.send(msg, recipients)

    def send(self, msg, recipients):
        """Sends an email"""

        # Send email
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(self.username, self.password)
        failed_deliveries = server.sendmail(self.username, recipients, msg)
        if failed_deliveries:
            print('Could not reach these addresses:', failed_deliveries)
        else:
            print('Email successfully sent')
        server.quit()
