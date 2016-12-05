#!/usr/bin/python
from os.path import exists

delayed_students = []

assignment_no = 6
f = open("INF3331-students_base_assignment{}.txt".format(assignment_no), "r").readlines()

solution_path = "../assignment5_solutions/INF3331_all_repos/INF3331-{}/assignment{}"
solution_path2 = "../assignment5_solutions/INF3331_all_repos/INF3331-{}/Assignment{}"
solution_path3 = "../assignment5_solutions/INF3331_all_repos/INF3331-{}/assigment{}"
solution_path4 = "../assignment5_solutions/INF3331_all_repos/INF3331-{}/src/assignment{}"

for l in f:
    attends, uio, github, email, course, name =  l.split(r"//")
    if not attends.strip() == "x":
        continue

    uio = uio.strip()
    if not exists(solution_path.format(uio, assignment_n5o)) and \
       not exists(solution_path2.format(uio, assignment_no)) and \
       not exists(solution_path3.format(uio, assignment_no)) and \
       not exists(solution_path4.format(uio, assignment_no)):
            print "Student {} might have not submitted assignment {} but is in the student list".format(uio, assignment_no)


