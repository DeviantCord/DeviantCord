************************************
Setting up DeviantCord
************************************
DeviantCord has two different options in terms of hosting the bot. You can either request hosting through us, or you can
host it yourself. You can see the differences between the two here


Finding a host
========================
Self Hosting the bot requires a bit of work to get it setup, however before getting into the configuration of the bot
you may want to consider where to host it. Cloud Hosting/ Virtual Private servers are usually the most affordable places
to host your bot if you know where to look.

*Note: If you are hosting the bot on your own machine you can skip to the Setup Section*

If you want more information it can be found :doc:`choosehost`

Installing Python3
==============================
Depending on what operating system you are using (eg. Windows, Mac, Linux) the setup process will be different.

Please select the your operating system

Linux
*****
Linux has many different types of Distributions with different Package Managers.
Some may have Python3 already installed, however we only support Python version 3.6 minimum, check to see what your
version of Python is (if any)::
    python3 --version

If your distribution is not below and does not come with a version of Python3 that isnt at least 3.6, then you will have to install python
manually.


Ubuntu/Linux Mint
------------------------

We only support Ubuntu Versions 18.04 and above

For Linux Mint we only support 19+


Ubuntu 18.04 has Python 3.6, the minimum version supported by the bot.
While the versions after it has 3.7 However PIP the module manager for Python
is not installed by default. You will have to install it.

To get started you first need to get the latest update headers otherwise you will not
be able to proceed. ::
    sudo apt-get update


Then you need to run the install command for PIP otherwise
you will not be able to install the needed modules that the bot uses. ::
    sudo apt-get install python3-pip

Once pip is intalled, you now have access to the pip command.
Now lets install the required modules. ::
    pip3 install discord.py discord asyncio urllib3

Debian 9
------------
Debian 9 uses Python 3.5.3, the minimum supported version for the bot.
It is not advised to use Python 3.5.3, as it may be deprecated within a future version.

If you want to use Python 3.5.3 then all you
need to do is install pip ::
    apt-get update && apt-get install python3-pip


Then you need to install the
python modules for the bot ::
    pip3 install discord.py asyncio urllib3

However, if you want to install Python 3.7 here is a guide to do so
`here <https://linuxize.com/post/how-to-install-python-3-7-on-debian-9/>`_

CentOS 7
----------------------------------
CentOS does not come with any version of Python3 by default, and as a result you will have to install it manually.
Additionally you will need to install a repository that allows you to install python3 ::
    yum install -y https://centos7.iuscommunity.org/ius-release.rpm

Once you have the repository installed, you should make sure that
there are no updates before installing Python3 ::
    yum update

Then input Y and enter to confirm the update (If there are any updates).

Once you have the updates installed,
you want to use the following command to install Python3 ::
    yum install -y python36u python36u-libs python36u-devel python36u-pip


After that, make sure the following
command returns something ::
    python3.6 -V


If it returns something, then Python3 is installed! Now we need to install
the required Python modules for the bot. Use the following command to accomplish it ::
    pip3.6 install discord.py asyncio urllib3


Fedora
----------------------------------
Fedora 28+ has Python 3.6 and usually updates its python3 version consistently to newer versions.
As a result you do not need to install Python3 or pip. So all you need to do is install the Python modules ::
    pip3 install discord.py asyncio urllib3



Raspian (Arm Linux Distros)
---------------------------
ARM based Linux Distributions are not supported at this time.



Windows
*******
Go download a release of Python 3.6+ `here  <https://www.python.org/downloads/>`_

Once it is installed, go to your search bar for Windows and search for cmd,
then right click it and Run as Administrator and type ::
    pip install discord.py asyncio urllib3


MacOS (OSX)
***********
DeviantCord is not tested on MacOS, however it will still run.
It should be noted however, that MacOS by default packages Python2, which is not compatible with DeviantCord.

You will need to install Python at their
website. Then Run ::
    pip3 install discord.py asyncio urllib3