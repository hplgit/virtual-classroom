from datetime import datetime
import shutil

src_file = "Attendance/students_base.txt"

date = datetime.now()
month = str(date.month) if date.month > 9 else "0" + str(date.month)
day = str(date.day) if date.day > 9 else "0" + str(date.day)
dst_file = "Attendance/students_base-%s-%s-%s.txt" % (date.year, month, day)

shutil.copy(src_file, dst_file)
