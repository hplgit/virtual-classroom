Welcome to INF5620
------------------
In this course we will use GitHub as a tool for 
version control and collaboration. You have now access to a repository 
which is called %(name)s. It is very important that everything you do in
this course is added to this repository.

There is a lot of information about git on the web,
and you will learn to use it during this course, but here is a short intro.

First you need to install git, this can be done by the command:

.. code-block::

	sudo apt-get install git

to clone the repository you have been given access to you simply write

.. code-block:: 

	git clone %(repo_adress)s

it's smart to be located where you want the folder/repository to be downloaded into.  
When you enter the folder you could say that you are in a git environment and you can now use it on
our files. 

So let's say you create a new file 'test.py' and want to "track" this file.

.. code-block:: 

	git add test.py

Now git will follow changes made to this file. So, now we could tell git that we are ready to 
commit this file. Let's say that we added some functionalty that now works. 

.. code-block:: 

	git commit test.py -m 'Add command line options'

Now we could continue to edit the file, but perhaps we did something that made
the file crash. Then we could simply remove the changes done since the last commit.

.. code-block:: 

	git checkout test.py

All the changes are stil on your local computer, so it's time to upload them to
the repository on github.

.. code-block:: 

	git push origin master

Some other handy commands is

.. code-block:: 

	git status
	git diff
	git log
	git commit -a -m 'Some message'
	git reset
	git checkout -b 'new branch name'


This is a short manual for working with your own repository. There will later on come a sort
manual for collaboration.

More information:
 * If you want to learn more about git, the three first chapters http://git-scm.com/book is a good reference.
 * Course material
 * GitHubs own tutorial


