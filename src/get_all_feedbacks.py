import re
import os
import sys
import base64
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
            self.students_base_dict = self.get_students(open(attendance_path, 'r').readlines())
        else:
            attendance_path = input('There is no file %s, pleace provide the' % attendance_path \
                                     + 'filepath to where the student base file is located:')
            self.students_base_dict = self.get_students(open(attendance_path, 'r').readlines())

        # Header for each file
        self.header = "/"*50 + "\n// Name: %(name)s \n" + "// Email: %(email)s \n" + \
                       "// Username: %(username)s \n" + "// Repo: %(repo)s \n" + \
                        "// Editors: %(editors)s \n" + "/"*50 + "\n\n"

        # TODO: these should be accessible through default_parameters
        # User defined variables
        assignment_name = input('What is this assignment called: ')
        feedback_name_base = input('\nWhat are the base filename of your feedback ' \
                                    + 'files called, e.g.\nif you answer "PASSED" the ' \
                                    + 'program will look for "PASSED_%s_YES \nand "PASSED_%s_NO" ' \
                                    % (assignment_name, assignment_name).upper()
                                    + '(case insensetive) : ').lower()

        # The files to look for
        self.file_feedback = [feedback_name_base + '_' + assignment_name '_yes', 
                               feedback_name_base + '_' + assignment_name + '_no']
       
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
                success, contents, status, path = self.find_file(r.json()['tree'])

                # Get infomation about user and the file
                r = get(repo['teams_url'], auth=self.auth)
                personal_info = self.students_base_dict[r.json()[0]['name'].encode('utf-8')]
                personal_info['repo'] = repo['name'].encode('utf-8')

                # Check if there is reason to belive that the user have cheated
                #if personal_info['name'] in personal_info['editors']:
                    #pass 
                    #TODO: Store this feedback in a list of potential cheeters

                # Write feedback with hreader to file
                if success:
                    personal_info['editors'] = ", ".join(self.get_editors(path, repo))
                    text = self.header % personal_info + contents
                    filename = personal_info['name'].replace(' ', '_') + '.txt'
                    folder = self.passed_path if status == 'yes' else self.not_passed_path
                    folder = os.path.join(folder, filename)
                    feedback = open(folder, 'w')
                    feedback.write(text)
                    feedback.close()

                # No feedback
                else:
                    not_done.append(personal_info)

        # TODO: Only write those how where pressent at group and didn't get feedback
        #       now it just writes everyone how has not gotten any feedback.
        text = "Students that didn't get any feedbacks\n"
        test += "Name   //  username    //  email   "
        for student in not_done:
            text += "%(name)s // %(username)s // %(email)s" % student 
        not_done_file = open(os.path.join(self.not_done_path, 'No_feedback.txt'), 'w')
        not_done_file.write(text)
        not_done_file.close()

    def get_students(self, text):
        student_dict = {}
        for line in text[1:]:
            pressent, name, username, email = re.split(r"\s*\/\/\s*", line.replace('\n', ''))
            student_dict[name] = {'name': name, 'username': username, 'email': email}
        return student_dict

    def find_file(self, tree):
        for file in tree:
            # Explore the subdirectories recursively
            if file['type'].encode('utf-8') == 'tree':
                r = get(file['url'], auth=self.auth)
                success, contents, status, path = self.find_file(r.json()['tree'])
                if success:
                    return success, contents, status, path

            # Check if the files in the folder match file_feedback
            file_name = file['path'].split(os.path.sep)[-1].lower().split('.')[0]
            if file_name in self.file_feedback:
                r = get(file['url'], auth=self.auth)
                return True, base64.b64decode(r.json()['content']), file_name.split('_')[-1], \
                        file['path']

        # If file not found
        return False, "", "", ""

    def get_editors(self, path, repo):
        url_commit = 'https://api.github.com/repos/%s/%s/commits' % (self.org, repo['name'])
        r = get(url_commit, auth=self.auth, params={'path': path})
        print(r.status_code)
        # TODO: Change commiter with author?
        editors = [commit['commit']['committer']['name'].encode('utf-8') for commit in r.json()]
        print(editors)
        return editors

