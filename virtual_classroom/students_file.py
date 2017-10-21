from __future__ import print_function, unicode_literals
from re import split
import os

from .parameters import get_parameters


students_file_columns = ["present",
                         "name",
                         "uio_username",
                         "username",
                         "email",
                         "course"]


def get_students_file_path(filename=None):
    if filename is None:
        parameters = get_parameters()
        students_file = parameters["students_file"]
        filename = students_file.format(**parameters)
        filename = os.path.join(os.path.dirname(__file__), filename)
    return filename


def parse_students_file(filename=None):
    rs = open(get_students_file_path(filename), "rb")

    students_values = []
    i = 0
    for line in rs.readlines():
        i += 1
        entries = split(r"\s*\/\/\s*", line.decode("utf-8").replace('\n', ''))
        student_values = _extract_entries(entries)
        if student_values is not None:
            students_values.append(student_values)
        elif i > 1:
            print("Found no student on line %d. Possibly wrong formatting." % i)

    return students_values


def _extract_entries(entries):
    if len(entries) < len(students_file_columns):
        return None

    values = {}
    for i in range(len(students_file_columns)):
        values[students_file_columns[i]] = entries[i]

    if values[students_file_columns[0]].lower() not in ("x", "-"):
        return None

    return values


def save_students_file(students, filename=None):
    string = "Attendance // Name // UiO Username // Github username // Email // Course" + "\n"
    for student in students:
        string += " // ".join([getattr(student, i) for i in students_file_columns])
        string += "\n"

    with open(get_students_file_path(filename), "wb") as f:
        f.write(string.encode("utf-8"))
