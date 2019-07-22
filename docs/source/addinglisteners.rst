************************************
Setting Up Listeners
************************************

There are three commands in DeviantCord that adds listeners that check gallery folders for new deviations.
However this page aims to clear misconceptions with configuring listeners.
The addartist command is the first command that should be ran for a new artist,

Things to Note:
*********************
* The bot needs Exact Foldernames (Case Sensitive)
* The bot needs the artists name exactly (Not Case Sensitive)
* Artist Username should be in quotes
* Folder name should be in quotes
* The addartist command is used to add a new artist that has no other listeners
* The addfolder command adds another listener for an already existing artist's folder.


Correct Arguments
-----------------

For Example with the addartist and addfolder command it is :

$addartist *<artist_username>* *<folder>* *<channel_id>* *<inverted>*

$addfolder *<artist_username>* *<folder>* *<channel_id>* *<inverted>*

If we looked at an artists page, such as the one below

.. image:: SettingUp.PNG
*Example image from Zander-The-Artist (With Permission) see his work* `here <https://www.deviantart.com/zander-the-artist>`_

Looking above at the example image, and using it as an example you should note the following

The addartist command should have the artist name and in this case it would be "zander-the-artist" not "zander the artist"

The artist username field should be the same as the yellow highlighted area in the picture above.

The folder field for the Hope in Friends Comic folder should be the exactly what it is in the sidebar on the left.
In this case the folder for the comic Hope In Friends should be "Hope In Friends Comic" not "Hope in Friends"

$addartist "zander-the-artist" "Hope In Friends Comic" *<channel_id>* false

*Inverted in this case would be false, but it depends on what artist and what folder*

AllFolders
----------
On DeviantArt there is an all view that allows users to view all deviations from an artist. Starting with DeviantCord bt-1.4.0
allfolder commands are introduced allowing for DeviantCord to send notifications whenever an artist posts a deviation
no matter what folder it is put in.

$addallfolder *<artist_username>*  *<channel_id>* *<inverted>*

Using this command will work rather or not the artist already exists in artdata, and if the artist is not in artdata already
there is no need to use an addartist command.

Removing Folders
----------------
Removing a listener uses the same logic as the section above, if you haven't read the section it is suggested that you
read it first.

However there are some differences you should note. As there is only a remove folder listener command. This was
done to prevent accidentally deleting a whole artist from the folder as multiple folders can be stored under an artist.

As a result you can only delete one listener at a time.
The command is as follows ::
    $deletefolder <artist_username> <folder>

This will delete the folder from the artist.json file and no more notifications will be posted to Discord for that folder
unless you readd it.

Additionally if you are having trouble remembering what folders are currently being listened for new deviations you can
use the listfolders command ::
    $listfolders

Starting with bt-1.4.0 allfolders are introduced. To remove allfolders, you need to use the deleteallfolder command as
follows here.::
    $deleteallfolder <artist_username>

**NOTE: Using the deleteallfolder command does not remove all folders from an artist**



Inverted Galleries
------------------
Inverted galleries is the term we use to indicate that newest deviations are at the top instead of the bottom.
An example of an inverted gallery can be seen `here <https://www.deviantart.com/pkm-150/gallery/58231950/Eeveelution-Squad>`_

The inverted argument would be declared true or false in the addfolder command and addartist command.

.. warning::
    As of version bt-1.2.0, the inverse arguement should only be used for artists who have dependently posted an
    inverted gallery declaring inverse as false will now check for the 20 deviations posted at the top and will
    check for more at the bottom up until DeviantArt's API says there is no more deviations.




Discord Developer Mode
**********************
Discord Developer Mode is required in order to get text channel id's,
you will need to enable it by clicking the gear icon near your name

..  image:: discordprofile.png

Once you get into that menu click the Appearance Tab

..  image:: appearance.png

then scroll down to the bottom and enable Developer Mode.

..  image:: developermode.png

Credits
*******
Special Thanks to Tony/Zander-The-Artist for allowing DeviantCord to feature his gallery as an example
You can see his outstanding comic Hope in Friends `over here <https://www.deviantart.com/zander-the-artist>`_
