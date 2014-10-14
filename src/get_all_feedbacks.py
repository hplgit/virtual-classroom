import re
import os
import sys
import base64
import codecs
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

        self.org = "%s-%s" % (university, course)
        url_orgs = 'https://api.github.com/orgs/%s' % (self.org)

        # Need help functions from classroom
        self.classroom = Classroom(auth, url_orgs)

        # To look up information about students
        attendance_path = os.path.join(os.path.dirname(__file__), \
                                        'Attendance', '%s-students_base.txt' % course)
        if os.path.isfile(attendance_path):
            self.students_base_dict = self.get_students(codecs.open(attendance_path, 'r',
                                                        encoding='utf-8').readlines())
        else:
            attendance_path = input('There is no file %s, pleace provide the' % attendance_path \
                                     + 'filepath to where the student base file is located:')
            self.students_base_dict = self.get_students(open(attendance_path, 'r').readlines())

        # Header for each file
        self.header = "/"*50 + "\n// Name: %(name)s \n" + "// Email: %(email)s \n" + \
                       "// Username: %(username)s \n" + "// Repo: %(repo)s \n" + \
                        "// Editors: %(editors)s \n" + "/"*50 + "\n\n"
        self.header = self.header.encode('utf-8')

        # TODO: these should be accessible through default_parameters
        # User defined variables
        assignment_name = input('What is this assignment called: ')
        feedback_name_base = input('\nWhat are the base filename of your feedback ' \
                                    + 'files called, e.g.\nif you answer "PASSED" the ' \
                                    + 'program will look for "PASSED_YES \nand "PASSED_NO" ' \
                                    + '(case insensetive) : ').lower()

        # The files to look for
        self.file_feedback = [feedback_name_base + '_yes', feedback_name_base + '_no']
       
        # Create path
        original_dir = os.getcwd()
        if output_path == "":
            feedback_filepath = os.path.join(original_dir, "%s_all_feedbacks" % course)
        else:
            feedback_filepath = os.path.join(original_dir, output_path, \
                                              "%s_all_feedbacks" % course)

        # Path for feedback
        self.passed_path = os.path.join(feedback_filepath, assignment_name, 'PASSED')
        self.not_passed_path = os.path.join(feedback_filepath, assignment_name, 'NOT_PASSED')
        self.not_done_path = os.path.join(feedback_filepath, assignment_name)

        # Create folder structure
        try:
            os.makedirs(self.passed_path)
            os.makedirs(self.not_passed_path)
        except Exception as e:
            if os.listdir(self.passed_path) == [] and os.listdir(self.not_passed_path) == []:
                pass
            else:
                print("There are already collected feedbacks for %s." % assignment_name \
                       + " Remove these or copy them to another directory.") 
                sys.exit(1)

    def __call__(self):
        print("\nLooking for feedbacks, this may take some time ...\n")
        repos = self.classroom.get_repos()    
        not_done = []

        for repo in repos:
            # Assumes that no repo has the same naming convension
            if self.course + "-" in repo['name'].encode('utf-8'):

                # Get sha from the last commit
                url_commits = repo['commits_url'][:-6]
                sha = get(url_commits, auth=self.auth).json()[0]['sha']

                # Get tree
                self.url_trees = repo['trees_url'][:-6]
                r = get(self.url_trees + '/' + sha, auth=self.auth)

                # Get feedback file
                success, contents, status, path, extension = self.find_file(r.json()['tree'])

                # Get infomation about user and the file
                r = get(repo['teams_url'], auth=self.auth)
                personal_info = self.students_base_dict[r.json()[0]['name'].encode('utf-8')]
                personal_info['repo'] = repo['name'].encode('utf-8')
                #print(repo['teams_url'])
                if success:
                    # Check if there is reason to belive that the user have cheated
                    personal_info['editors'] = ", ".join(self.get_editors(path, repo))
                    #print(personal_info['name'])
                    #print(personal_info['editors'])
                    #if (personal_info['name'].encode('utf-8') or personal_info['username']) \
                        #in personal_info['editors']:
                        #print(personal_info['name'])
                        #TODO: Store this feedback in a list of potential cheaters

                    # Write feedback with header to file
                    try:
                        text = self.header % personal_info
                        text += contents.decode('utf-8')
                    except Exception as e:
                        print(personal_info)
                        print(contents)
                        print("Could not get the contents of %(name)s feedback file. Error:" \
                                 % personal_info)
                        print(e)
                    filename = personal_info['name'].replace(' ', '_') + '.' + extension
                    folder = self.passed_path if status == 'yes' else self.not_passed_path
                    folder = os.path.join(folder, filename)
                    feedback = codecs.open(folder, 'w', encoding='utf-8')
                    feedback.write(text)
                    feedback.close()

                # No feedback
                else:
                    not_done.append(personal_info)

        # TODO: Only write those how where pressent at group and didn't get feedback
        #       now it just writes everyone how has not gotten any feedback.
        text = "Students that didn't get any feedbacks\n"
        text += "Name   //  username    //  email\n"
        for student in not_done:
            text += "%(name)s // %(username)s // %(email)s\n" % student 
        not_done_file = codecs.open(os.path.join(self.not_done_path, 'No_feedback.txt'), 'w',
                                     encoding='utf-8')
        not_done_file.write(text)
        not_done_file.close()

        number_of_feedbacks = len(repos) - len(not_done)
        print("\nFetched feedback from %s students and %s have not gotten any feedback" % \
                (number_of_feedbacks, len(not_done)))

    def get_students(self, text):
        student_dict = {}
        for line in text[1:]:
            pressent, name, username, email = re.split(r"\s*\/\/\s*", line.replace('\n', ''))
            student_dict[name.encode('utf-8')] = {'name': name, 
                                                   'username': username, 'email': email}
        return student_dict

    def find_file(self, tree):
        for file in tree:
            # Explore the subdirectories recursively
            if file['type'].encode('utf-8') == 'tree':
                r = get(file['url'], auth=self.auth)
                success, contents, status, path, extension = self.find_file(r.json()['tree'])
                if success:
                    return success, contents, status, path, extension

            # Check if the files in the folder match file_feedback
            if file['path'].split(os.path.sep)[-1].split('.')[0].lower() in self.file_feedback:
                # Get filename and extension
                if '.' in  file['path'].split(os.path.sep)[-1]:
                    file_name, extension = file['path'].split(os.path.sep)[-1].lower().split('.')
                else:
                    file_name = file['path'].split(os.path.sep)[-1].lower()
                    extension = 'txt'

                r = get(file['url'], auth=self.auth)
                return True, base64.b64decode(r.json()['content']), \
                        file_name.split('_')[-1], file['path'], extension

        # If file not found
        return False, "", "", "", ""

    def get_editors(self, path, repo):
        url_commit = 'https://api.github.com/repos/%s/%s/commits' % (self.org, repo['name'])
        r = get(url_commit, auth=self.auth, params={'path': path})
        # TODO: Change commiter with author?
        editors = [commit['commit']['author']['name'].encode('utf-8') for commit in r.json()]
        return editors
