#!/usr/bin/python
from os.path import exists

delayed_students = []

assignment_no = 6
f = open("INF3331-students_base_assignment{}.txt".format(assignment_no), "r").readlines()

solution_paths = ["../assignment{}_solutions/INF3331_all_repos/INF3331-{}/assignment{}",
                "../assignment{}_solutions/INF3331_all_repos/INF3331-{}/Assignment{}",
                "../assignment{}_solutions/INF3331_all_repos/INF3331-{}/assigment{}",
                "../assignment{}_solutions/INF3331_all_repos/INF3331-{}/assignment-{}",
                "../assignment{}_solutions/INF3331_all_repos/INF3331-{}/Assignment-{}",
                "../assignment{}_solutions/INF3331_all_repos/INF3331-{}/virtual_classroom/assignment{}",
                ]

for l in f:
    attends, uio, github, email, course, name =  l.split(r"//")
    if not attends.strip() == "x":
        continue

    uio = uio.strip()
    has_solution = any([exists(solution_path.format(assignment_no, uio, assignment_no)) for solution_path in solution_paths])
    if not has_solution:
            print "Student {} might have not submitted assignment {} but is in the student list".format(uio, assignment_no)


