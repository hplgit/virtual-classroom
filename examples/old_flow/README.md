# Workflow similar to earlier version

## Start of semester

1. Edit `defaults_parameters.txt`.
2. Ask students to fill out the Google Form https://docs.google.com/a/simula.no/forms/d/1JGSMC-9sRcuCanLF7MavHlGWVxuOjX-bwcIoyoM4yPE/edit
3. Make sure the response Google Spreadsheet has the ordering: *Timestamp, UiO-Username, Username on Github, Email Address, Course, Full name*
4. Download the student list with `python download_spreadsheet.py`
5. Mark all participating students with an `x` in `Attendance/students_base.txt`
6. Create a github repository and team for each student with 

   `python manage_group.py --i True --no-email --f Attendance/students_base.txt`

   (If you choose `--email`, make sure to update the file `message_new_student.rst` beforehand).
   
   *Note*: This command will *not* overwrite existing repositories. This means that you can execute this command again if new students join the course.

Assignments
-----------
1. Each student has a repository with the name `{course}-*XYZ*` where `{course}` is the course parameter supplied in
 `default_parameters.txt` and `*XYZ*` is some substring of the student name. The solutions should be pushed into this repository.
2. If the assignment is a peer-reviewed assignment, see next section. Otherwise, proceed with the next step.
3. At the assignment deadline, all repositories can be downloaded with:

   `python manage_group.py --get_repos True --get_repos_filepath assignment2_solutions --f Attendance/students_base.txt`
   

Performing a peer-review
------------------------
1. Run `python copy_attendance_file.py` and mark the students that take part of the group with `x` (this is useful if some of the students hand in late).
2. Alternatively you may run `python mark_active.py` to mark students active since a given date.
2. Run `python manage_group.py --f Attendance/students_base-2015-12-01.txt`. This creates github teams of size 3 with access to 3 other student's repositories. Each group should review the student's solutions and push the reports to their repositories.

After review, delete all teams (and with it the access to their peers repositories) with:

3. `python manage_group.py --e True`

End of semester
---------------

1. Backup all repositories. For example:

```bash
python manage_group.py --get_repos=True --get_repos_filepath=repos_2015
```

2. Delete all course repositories, teams and members (not owners) with:

```bash
python end_semester.py
```

