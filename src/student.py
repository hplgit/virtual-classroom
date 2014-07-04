
class user()

    def __init__(self, name, username, course):
        self.name = name
        self.username = username
        self.course = course
    #TODO: extend baseclass for users


class Student(user)
   
    def __init__(self, name, username):
        super(name, username, course)
        if not repository_exists():
             create_repository(username)

    def create_repository(self, username):
        #TODO: create a repository for the username
        #TODO: Give a good feedback if the student doesn't have a user or the username
        #      is incorrect.

    def add_presens(self):
        #TODO: Store number of times present in some file

    def give_access(self, other):
        #TODO: give access to other students

    def repository_exists(self):
        #TODO: Check if repo exists

    def get_stats(self):
        #TODO: Get number of commits and so on, number of times present ect.

    def revoke_access(self):
        #TODO: Remove access after a group seassion. 


class TeachingAssistent(user)

    def __init__(self, name, username, course):
        super(name, username, course)
        if not is_admin(username):
            print("Username: %s is not admin, and can not be a teaching assistent." \
                    % username)

    def is_admin(username):
        #TODO: Check if user is admin

    def get_all_repsitoris(self, class_room)
        #TODO: Get all repositories beloning to students

    def give_alle_student_access(self, students):
        #TODO: Give students access to solutions ect.


class Professor(user)   #TODO: Do we need methods spesific for the professor?
