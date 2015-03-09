Hi %(name)s, and welcome to %(course)s
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this course we will use GitHub as a tool for version control and
collaboration.  You have now access to a repository which is called
%(repo_name)s. It is very important that every file you make in this
course that is supposed to be evaluated by others, is added to this
repo (short for repository). We recommend that you put all your course
work in the repo, because this serves as a backup and as an archive of
previous versions of the files. You work with the repo through the Git
version control system. The workflow may seem a bit cumbersome at
first sight, but this is how professionals work with software and
technical documents all around the world in %(year)s.

**Important**: Open your primary email on GitHub and confirm that you
want to join %(university)s-%(course)s. You have to do this to get
access to your new repo.

There is a lot of information about git on the web, but below we give
the quick need-to-know steps for the course. First you need to install
git. This can be done by the command:

.. code-block::

	sudo apt-get install git

The next step is to clone the repository you have been given access
to. You simply write

.. code-block::

	git clone %(repo_adress)s

which gives you a directory %(repo_name)s. When you enter the folder,
you are in a Git-control directory tree and must use certain Git
commands to register files and update the repo.

So let's say you create a new file 'test.py' that you want Git to track
the history of. Then you must write

.. code-block::

	git add test.py

After you have worked with files and they seem to be in an acceptable
state, or you stop working for the day, you should do

.. code-block::

	git commit test.py -am 'Short description of the changes you made to files since last git commit command...'

The file changes are now on your computer only. To send them to the
cloud and back them up, do

.. code-block::

	git push origin master

If you work on multiple computers, or if you collaborate with others
in the repo, it is very important that you do

.. code-block::

        git pull origin master

to download the latest version of the files before you start editing
any of them.


More information:

 * See the `Quick intro to Git and GitHub <http://hplgit.github.io/teamods/bitgit/Langtangen_github.pdf>`_
 * A more extensive introduction to Git is provided by the three first chapters in `this book <http://git-scm.com/book>`_
