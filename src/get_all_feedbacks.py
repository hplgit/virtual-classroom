import re
import os
import sys
from requests import get
from classroom import Classroom

# Python3 and 2 compatible
try: input = raw_input
except NameError: pass


class Feedbacks:

    def __init__(self, auth, university, course, output_path):
        self.auth = auth
        self.university = university
        self.course = course
        #self.output_path = output_path

        org = "%s-%s" % (university, course)
        url_orgs = 'https://api.github.com/orgs/%s' % (org)

        # Need help functions from classroom
        self.classroom = Classroom(auth, url_orgs)

        # To look up information about students
        attendance_path = os.path.join(os.path.dirname(__file__), \
                                        'Attendance', '%s-students_base.txt' % course)
        if os.path.isfile(attendance_path):
            self.students_base_dict = self.get_students(open(attendance_path, 'r').readlines())
        else:
            attendance_path = input('There is no file %s, pleace provide the filepath \
                                           to where the student base file is located: ' % course)
            self.students_base_dict = self.get_students(open(attendance_path, 'r').readlines())


        mandatory_assignment = input('What is this assignment called: ')
        feedback_name_base = input( \
"""\nWhat are the base filename of your feedback files called, e.g. if 
you answer "REVEIW1" the program will look for "REVEIW1_YES
and "REVEIW1_NO" (case insensetive) : """).lower()

        # The files to look for
        file_feedback = [feedback_name_base + '_yes', feedback_name_base + '_no']
       
        # Create path
        original_dir = os.getcwd()
        if output_path == "":
            feedback_filepath = os.path.join(original_dir, "%s_all_feedbacks" % course)
        else:
            feedback_filepath = os.path.join(original_dir, output_path, \
                                              "%s_all_feedbacks" % course)

        # Save in self for later use
        self.passed_path = os.path.join(feedback_filepath, mandatory_assignment, 'PASSED')
        self.not_passed_path = os.path.join(feedback_filepath, \
                                mandatory_assignment, 'NOT PASSED')

        # Create folder structure
        try:
            os.makedirs(self.passed_path)
            os.makedirs(self.not_passed_path)
        except Exception as e:
            print(e)
            os.chdir(os.path.join(feedback_filepath, mandatory_assignment))
            if os.listdir('PASSED') == [] and os.listdir('NOT PASSED') == []:
                pass
            else:
                print("There are already collected feedbacks for %s. Remove these of copy \
                        them to another directory") 
                sys.exit(1)

        os.chdir(original_dir)

    def __call__(self):
        repos = self.classroom.get_repos()    
        for repo in repos:
            # Assumes that no repo has the same naming convension
            if course + "-" in repo['name'].encode('utf-8'):

                # Get sha from the last commit
                url_commits = repo['commits_url'][:-6]
                sha = get(url_commits, auth=self.auth).json()[0]['sha']

                # Get tree
                url_trees = repo['trees_url'][:-6]
                r = get(url_trees + '/' + sha, auth=self.auth)
                contents, success, status = self.find_file(r.json()['tree'])
                if success:
                    name = get(repo['teams_url'], auth=self.auth).json()['name']
                    personal_info = self.students_base_dict[name] # problems with ascii?
                    header = "/"*50 + "\n// Name: %(name)s \n" + "// Email: %(email)s \n" + \
                              "// Username: %(username)s \n" + "/"*50 + '\n'
                    text = header % personal_info + contents
                    filename = name.replace(' ', '_') + '.txt'
                    folder = self.passed_path if status == 'yes' else self.not_passed_path
                    folder = os.path.join(folder, filename)
                    feedback = open(folder, 'w')
                    feedback.write(text)
                    feedback.close()
                else:
                    pass
                    # TODO: Check if there exists a folder: Not corrected:
                    #       if not create one. Write a file like over.

    def get_students(self, text):
        student_dict = {}
        for line in text[1:]:
            pressent, name, username, email = re.split(r"\s*\/\/\s*", line.replace('\n', ''))
            student_dict[name] = {'name': name, 'username': username, 'email': email}
        return student_dict

    def find_file(self, tree):
        for file in r.json()['tree']:
            # Explor the subdirectories recursivly
            if file['type'] == 'tree':
                r = get(url_trees + '/' + file['sha'], auth=auth)
                self.find_file(r.json()['tree'])

            # Check if the files in the folder match file_feedback
            if file.split(os.path.sep)[-1].lower() in file_feedback:
                r = get(file['url'], auth=auth)
                return True, base64.b64decode(r.json['contents']), \
                        file.split(os.path.sep)[-1].split('_')[-1]

        # If file not found
        return False, "", ""
