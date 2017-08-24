Dear {{ student.name }}!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

{%- set filtered_group = group.students|rejectattr("name", "equalto", student.name)|list %}
{%- set filtered_group_names = filtered_group|map(attribute="name")|list %}
{%- if filtered_group_names|length >= 2 %}
    {%- set part_group_names = filtered_group_names[:-1]|join(", ") %}
    {%- set group_names = part_group_names + " and " + filtered_group_names[-1] %}
{%- else %}
    {%- set group_names = filtered_group_names|join("") %}
{%- endif %}

You are receiving this e-mail because you are taking the INF3331/INF4331
course and have submitted peer-reviewed assignement. You are now asked to join
a collaboration with {{ filtered_group|length }} of your fellow students.
Together you are asked to performed peer-review on {{ group.review_repos|length }} other fellow
solutions.

You have been assigned to work with {{ group_names }} as part of
{{ group.team_name }}. Start by contacting your collaborators to organize
yourself. The email addresses of your collaborators are:

|    {{ filtered_group|map(attribute="email")|join("\n|    ") }}

You now have access to push and pull to three (or two) other students repositories.
Please review the solutions in all of these repositories.

The repositories to be reviewed are listed here: https://github.com/orgs/{{ classroom.org }}/teams/{{ group.team_name }}/repositories.

You can clone these repositories with:

.. code-block:: bash
{# #}
{%- for repo_name in group.review_repos %}
   git clone git@github.com:{{ classroom.org }}/{{ repo_name }}.git
{%- endfor %}

If you get a "permission denied" error, try changing the URL in the command above to https://github.com/{{ classroom.org }}/NAME.git (replace NAME with the actual repo name).

Guidelines
~~~~~~~~~~

* The guidelines and a Latex template for the feedback file is available here: https://www.overleaf.com/read/cdtgqrrwktzm and should be used (you may alternatively use a Markdown version with the same layout). You can write the review with Overleaf (its free to sign up): open link above and click on "Create a new project to start writing!" to get started.
* A review is completed by pushing the review Latex and PDF files to each of the reviewed repositories. The name of the files should be: feedback.tex and feedback.pdf.
