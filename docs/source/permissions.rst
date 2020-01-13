**********************
Setting Up Permissions
**********************
DeviantCord like many other bots requires that you grant permission to users via a role. If there is no role set,
then no commands besides admin commands will work.

However to set the role it should look for, you need someone with Administrator permissions to execute the setuprole command.

..  warning:: It should be noted that users with roles that are ranked higher then the bot role will automatically be granted permissions

However you will need to grab the roleid of the role you want to add. In order to get the roleid you will need to enable mentions for that role.

Then put the following
in the chat of a textchannel ::
    \@rolename

When the message is sent, it will reveal the id copy everything past the & sign except for the >

Then replace roleid in the command below and execute it

To set
the role use ::
    ~setuprole roleid

..  warning:: The prefix ($ above) may be different depending if you have a different prefix set. In that instance replace the $ with your used prefix

The bot should confirm that the prefix was updated. Otherwise if it is nonresponsive, check to see if you have a role
with Administrator. If problems still persist contact DeviantCord Support.

You can find details on contacting DeviantCord support here :doc:`support`