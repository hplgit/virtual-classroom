"""
This is just a prelimenary version made for ad-hoc use in
one course
"""

from os import path, listdir
from re import split
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from send_email import SMTPGoogle, Email

students = {}
default_parameters_path = path.join(path.dirname(__file__),
                                    'Attendance/INF5620-students_base.txt')
lines = open(default_parameters_path, 'r').readlines()

for line in lines[1:]:
    pressent, name, username, email = split(r"\s*\/\/\s*", line.replace('\n', ''))
    students[name] = {'pressent':0, 'email': email, 'name': name,
                        'username':username}
passed = "INF5620_all_feedbacks/Oblig%d/PASSED"

# Requires that you have fetched the feedbacks
for i in range(1,5):
    path_passed = passed % i
    #print listdir(path_passed)
    for file in listdir(path_passed):
        file_name = file.split('.')[0].replace('_', ' ')
        try:
            students[file_name]['pressent'] += 1
        except:
            print "Student are no longer taking this course: ", file_name

# Not in use
#file = open('INF5620_stats', 'w')
#for parameters in students.itervalues():
#    values = parameters.values()
#    tmp_str = " // ".join(values)
#    file.write(tmp_str)
#file.close()

#print students
exceptions = ['Arnfinn Aamodt', 'Matthew Terje Aadne', 'Jens Kristoffer Reitan Markussen']
skip = False

smtp = SMTPGoogle()
email = Email(smtp)

#text_zero = email.get_text('message_missing_all_classes.rst')
text_missing_one = email.get_text('message_missing_one_class.rst')
text_passed = email.get_text('message_missing_none.rst')

for parameters in students.itervalues():
    if parameters['name'] in exceptions: 
        skip = True

    if parameters['pressent'] == 0 and not skip:
        print "None: ", parameters['name'], "NO EMAIL"
        #text_tmp = text_zero % parameters

    if parameters['pressent'] == 1 and not skip:
        #text_tmp = text_one % parameters
        print "One pressent: ", parameters['name'], "NO EMAIL"

    if parameters['pressent'] == 2 and not skip:
        text_tmp = text_missing_one % parameters
        #print "Two pressent: ", parameters['name']

    if parameters['pressent'] >= 3 and not skip:
        text_tmp = text_passed % parameters
        #print "Three or more: ", parameters['name']

    if parameters['pressent'] in [2, 3, 4] and not skip:
        #print parameters['name']
        text_tmp = email.rst_to_html(text_tmp).encode('utf-8')
        msg = MIMEMultipart()
        msg['Subject'] = 'Mandatory group sessions'
        msg['To'] = parameters['email']
        msg['From'] = smtp.email
        body_text = MIMEText(text_tmp, 'html', 'utf-8')
        msg.attach(body_text)
        email.send(msg, parameters['email'])

    skip = False

email.logout()
