from virtual_classroom.classroom import Classroom

try: input = raw_input
except: pass

src_file = "Attendance/students_base.txt"
src_file_input = input("Students file to read from (default: %s): " % src_file)
src_file = src_file if src_file_input.strip() == "" else src_file_input

active_since = input("Mark students with commits after (date): ")

dst_file = "Attendance/students-active-since-%s" % active_since
dst_file_input = input("Students file to write to (default: %s): " % dst_file)
dst_file = dst_file if dst_file_input.strip() == "" else dst_file_input

ignore_present = input("Also check unmarked students in src file? (y/n): ")
ignore_present = (ignore_present.strip() == "y")

c = Classroom(src_file, ignore_present=ignore_present)
c.mark_active_repositories(active_since, dst_file)

