from re import split

from student import Student
from send_email import Email, EmailBody, SMTPGoogle, SMTPUiO
from parameters import get_parameters
from collaboration import Collaboration


class Classroom(object):
    """Contains help functions to get an overveiw of the virtual classroom"""

    def __init__(self, file=None):
        self.students = {}
        self.collaboration = None
        if file is None:
            # TODO: Fetch default file
            return

        # Load parameters
        parameters = get_parameters()
        university = parameters["university"]
        course = parameters["course"]

        lines = open(file, "r").readlines()
        # Create a dict with students
        for line in lines:
            try:
                present, name, username, email, _, _ = split(r"\s*\/\/\s*", line.replace('\n', ''))
                rank = 1
            except:
                present, name, username, email, _ = split(r"\s*\/\/\s*", line.replace('\n', ''))
                rank = 1
            if present.lower() == 'x' and username != "":
                print "Handle student {0}".format(name)
                self.students[name] = Student(name, username, university, course, email, rank)

    def email_students(self, filename, subject="", extra_params={}, smtp=None):
        """Sends an email to all students in the classroom.

        Will try to format the email body text with student attributes and `extra_params`.

        Parameters
        ----------
        filename : str
            Path to the file containing the email body text
        subject : str, optional
            Subject of the email
        extra_params : dict, optional
            Dictionary of extra parameters to format the email body text
        smtp : str, optional
            The SMTP server to use. Can either be 'google' or 'uio'.

        """
        parameters = get_parameters()
        smtp = parameters["smtp"] if smtp is None else smtp
        # Set up e-mail server
        if smtp == 'google':
            server = SMTPGoogle()
        elif smtp == 'uio':
            server = SMTPUiO()
        email_body = EmailBody(filename)
        email = Email(server, email_body, subject=subject)

        for name in self.students:
            student = self.students[name]
            params = student.__dict__.copy()
            params.update(extra_params)
            email_body.params = params
            email.send(student.email)





