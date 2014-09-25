Hi %(name)s!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You are receiving this e-mail because you are taking the course
%(course)s and have submitted the first mandatory assignment.
You are now asked to join a collaboration with two of your fellow
students. Together you are asked to performed peer-review on three
other students. (Likewise, another group of three will be
reviewing your assignment.)

You have been assigned to work with %(group_names)s as part of
%(team_name)s. Start by contacting your collaborators to organize
yourself. Email addresses to your collaborators:

%(team_emails)s

Together, the three of you will be correcting the work of the
following repositories:

%(correcting_names)s

You now have access to push and pull to these repositories. You
should make a temporary directory and execute

.. code-block:: bash

%(get_repos)s

Rules
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deadline for review is one week. In other words, this assignment
must be completed within Friday, September 26 at 23:59.

Each collaborating group decides how review is organized. Meeting
each other in person is encouraged, but is not mandatory.

The reviewers shall answer/consider the following questions:

For a program:

    1. Are the files easy to locate? That is, does the directory has a logical name? Are individual files given names according to the exercise?
    2. Is the program easy to read? More specifically,
        2.1. Are variables given self-explanatory names or names in accordance of the mathematical description?
        2.2. Are enough comments in the code?
        2.3. Is the code well formatted (use of whitespace etc.)?
        2.4. Is the code well organized in terms of functions or classes? (Also consider overuse of functions and classes in simpler problems!)
    3. Does the program answer the various points in the exercise?
    4. Does the program work?
    5. Are there any (automatic) verifications of the code?
    6. Are you able to run the code?

For a report:

    1. Is the report easy to locate?
    2. Is the report well formatted (title, author, sections, paragraphs, right spacings, low amount of typos, nice layout, introduction, conclusions, etc.)?
    3. Is the text logic and easy to follow? Is there sufficient explanation of what is done?
    4. Are the results correct?
    5. Are there any verifications of the results?


To pass review, 4 out of 5/6 of the questions must have the answer yes.

A review is completed by pushing a file to each of the reviewed
repositories. The name of the file should either be: `PASSED1_YES`
or `PASSED1_NO`.  The names represent a pass and a fail
respectively. The name has to be exact, since they will be read
automagically.  The file should contain feedback of the review.  If
an assignment is failed, detailed description on how to pass review
must be included.

Second round of evaluation will not be performed by the students.
