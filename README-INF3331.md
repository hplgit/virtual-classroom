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
