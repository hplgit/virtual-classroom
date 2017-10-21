import virtual_classroom.utils as utils

# Name of spreadsheet on Google sheets (You should change this to correct value)
spreadsheet_name = "VirtualClassroomTest (Responses)"

# Download parse, return contents and save it in default place
csv_str = utils.download_google_spreadsheet(spreadsheet_name)  # Should prompt for login info if default not set

utils.create_students_file_from_csv(csv_str=csv_str, output_filename="Attendance/students_base.txt")

