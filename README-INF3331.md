Virtual classroom for INF3331/INF4331
=====================================

Start of semester
-----------------

1. Ask students to fill out the Google Form https://docs.google.com/a/simula.no/forms/d/1JGSMC-9sRcuCanLF7MavHlGWVxuOjX-bwcIoyoM4yPE/edit
2. Make sure the response Google Spreadsheet has the ordering: *Timestamp, UiO-Username, Username on Github, Email Address, Course, Full name*
3. Download the student list with `cd virtual-classroom/src/scripts && ./get-info-google-spreadsheet.py`
4. Mark all participating students with an `x` in `Attendance/INF3331-students_base.txt`
4. Create a github repository and team for each student with 

   `cd virtual-classroom/src && ./start_group.py --i True --no-email --f Attendance/INF3331-students_base.txt`

   (If you choose `--email`, make sure to update the file `message_new_student.rst` beforehand).
   
   *Note*: This command will *not* overwrite existing repositories. This means that you can execute this command again if new students join the course.

Correcting solutions
--------------------

1. Download all repositories with

   `python start_group.py --get_repos True --get_repos_filepath assignment2_solutions --f Attendance/INF3331-students_base.txt`
   

Steps to start new peer-review group
------------------------------------
1. run scripts/copy-attendance-file.py
2. mark the students that take part of the group with "x"
3. python start_group.py --f Attendance/INF3331-2015-12-01_others.txt  # Creates teams of 3

After review, end the review group with

4. python start_group.py --e True


End of semester
---------------

1. Backup all repositories. For example:

```bash
python start_group.py --university=UiO --course=INF3331 --get_repos=True --get_repos_filepath=../repos_2015
```

2. Delete all course repositories, teams and members (not owners) with:

```bash
python end_semester.py
```
