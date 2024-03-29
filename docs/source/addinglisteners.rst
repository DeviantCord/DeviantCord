************************************
Setting Up Listeners
************************************
.. note::
    DeviantCord's default prefix is ~

Listeners are what DeviantCord uses to check for new Deviations (the term DeviantArt uses for new postings).
On DeviantArt all Deviations are put into a folder by an artist.

However, there are a few things you should note.

Things to Note:
*********************
..  note::
    To view your current listners you can use the listfolder command

* Once you create a listener, the bot will only see it exactly as you specified it at the listeners creation.

(Ex: You create a listener for the the Eeveelution Squad folder and specify the foldername as "Eeveelution Squad"
but when you try to update the listener, you accidently refer to it in commands as "EeVeelution Squad".
the bot will not recognize it. The foldername and artist name must be exact.

* The same goes for Artist Names as specified above regarding foldernames.
* Folder names, and artistnames should be in quotes
* The addallfolder command, adds the artists All Folder on DeviantArt. Meaning the listener will post notifications regarding any deviations the artist posts.

* The addfolder command adds a listener that will post notifications of new deviations in that folder only.


Folder Properties
-----------------
Artists can choose where in the folder they place their deviations at. Some put their newest deviations at the top,
while some post it to the bottom. DeviantCord cannot automatically detect whether artists post their newer deviations
at the top, or bottom.

To solve this, DeviantCord uses Folder Properties that server staff use to designate where deviations need to be found
and whether to filter certain content.

You will use these properties with the addfolder and addallfolder command and answer the properties as either true or false

**Properties**

* Inverse: Listeners that should only check for new deviations at the top of the folder
* Hybrid: Listeners that should also check for the opposite of what inverse is set to

    Example: Inverse is set to true and hybrid is set to true. Due to Hybrid being true
    the bottom deviations will also be checked.
* Mature: Whether Deviations flagged as mature in DeviantArt should be posted. If you set this flag to true

..  note::
    If your listener has the mature property set to true. The channel must be set to NSFW. Per Discord's ToS

Designating channels
--------------------
In any commands for DeviantCord referring to TextChannels, you just mention it like below

Ex: #general


Correct Arguments
-----------------

The Help command says that the usage for the addfolder and addallfolder commmand is :

~addfolder *<artist_username>* *<folder>* #channelname *<inverted>* *<hybrid>* *<mature>*

~addallfolder *<artist_username>* #channelname *<mature>*


If we looked at an artists page, such as the one below

.. image:: SettingUp.PNG
*Example image from Zander-The-Artist (With Permission) see his work* `here <https://www.deviantart.com/zander-the-artist>`_

Looking above at the example image, and using it as an example you should note the following

The addartist command should have the artist name and in this case it would be "zander-the-artist" not "zander the artist"

The artist username field should be the same as the yellow highlighted area in the picture above.

The folder field for the Hope in Friends Comic folder should be the exactly what it is in the sidebar on the left.
In this case the folder for the comic Hope In Friends should be "Hope In Friends Comic" not "Hope in Friends"

To add this folder we would use the following (replacing channelname with the text channel you want to use
~addartist "zander-the-artist" "Hope In Friends Comic" #channelname false false false

Removing Folders
----------------
Removing a listener uses the same logic as the section above, if you haven't read the section it is suggested that you
read it first.

However there are some differences you should note. As there is only a remove folder listener command. This was
done to prevent accidentally deleting a whole artist from the folder as multiple folders can be stored under an artist.

As a result you can only delete one listener at a time.
The command is as follows ::
    ~deletefolder <artist_username> <folder> #channelname

This will delete the listener from the database and no more notifications will be posted to Discord for that folder
unless you readd it.

Additionally if you are having trouble remembering what folders are currently being listened for new deviations you can
use the listfolders command ::
    ~listfolders

Credits
*******
Special Thanks to Tony/Zander-The-Artist for allowing DeviantCord to feature his gallery as an example
You can see his outstanding comic Hope in Friends `over here <https://www.deviantart.com/zander-the-artist>`_
