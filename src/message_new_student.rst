Hi %(name)s, and welcome to INF5620
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In this course we will use GitHub as a tool for 
version control and collaboration. You have now access to a repository 
which is called %(name)s. It is very important that everything you do in
this course is added to this repository. There is a lot of information 
about git on the web, and you will learn to use it during this course, 
but here is a short intro.

First you need to install git, this can be done by the command:

.. code-block::

	sudo apt-get install git

To clone the repository you have been given access to, you simply write

.. code-block:: 

	git clone %(repo_adress)s

It is smart to be located where you want the folder/repository to be downloaded into.  
When you enter the folder you could say that you are in a git environment and you can now use it on
our files. 

So let's say you create a new file 'test.py' and want to "track" this file.

.. code-block:: 

	git add test.py

Now git will follow changes made to this file. So, now we could tell git that we are ready to 
commit this file. Let's say that we added some functionality that now works. 

.. code-block:: 

	git commit test.py -m 'Add command line options'

Now we could continue to edit the file, but perhaps we did something that made
the file crash. Then we could simply remove the changes done since the last time 
we used "add" on the file.

.. code-block:: 

	git checkout test.py

All the changes are still on your local computer, so it's time to upload them to
the repository on github.

.. code-block:: 

	git push origin master

Some other handy commands are

.. code-block:: 

	git status                        # Overview of files that are changed
	git diff                          # List over changes
	git log                           # List over the last commits
	git commit -a -m 'Some message'   # Commits all changes
	git reset                         # Removes all changes to the last commit
	git checkout -b 'new branch name' # Creates a new branch

This is a short manual for working with your own repository. A manual for collaboration 
will be sent later on.

More information:
 * See the `course material <http://hplgit.github.io/teamods/bitgit/Langtangen_github.pdf>`_ 
 * If you want a more extensive introduction to git, see the three first chapters in `this book <http://git-scm.com/book>`_
