from __future__ import print_function
import getpass
import smtplib

# Python3 and 2 compatible
try: input = raw_input
except NameError: pass


class Email():

    def __init__():
        self.username = input("Username: ")
        self.password = getpass.getpass("Password:")

    def send(student, event):
        """Sends an email to the list of students about the event"""

        # Get emails
        if len(student) == 1:
            recipients = student.email
        else:
            emails = [s.email for s in student]
            recipients = ', '.join(emails)

        # Get text
        file = open('info_' + event + '.txt', 'r')
        text = file.readlines()
        file.close()

        # Compose email
        msg = """\
        From: %s
        To: %s
        Subject: New repository

        %s
        """ % (self.username, recipients, text)

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
