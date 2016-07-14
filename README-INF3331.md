INF3331 specific information
----------------------------


# Start new group
python start_group.py --i True

# Download all repos
python start_group.py --get_repos True --get_repos_filepath assignment2_solutions --f Attendance/INF3331-students_base.txt

# Steps to start new peer-review group
1. run scripts/copy-attendance-file.py
2. mark the students that take part of the group with "x"
3. python start_group.py --f Attendance/INF3331-2015-12-01_others.txt  # Creates teams of 3

# After review, end the review group with
4. python start_group.py --e True


# End of semester

Backup all repositories. For example:

```bash
python start_group.py --university=UiO --course=INF3331 --get_repos=True --get_repos_filepath=../repos_2015
```

At the end of the semester, delete all course repositories and all teams:

```bash
python end_semester.py
```

Finally, delete all members (not owners) of UiO-INF3331:
1. Go to https://github.com/orgs/UiO-INF3331/people?utf8=%E2%9C%93&query=role%3Amember%20
2. Delete all members
