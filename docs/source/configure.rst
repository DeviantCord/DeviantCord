************************************
Configuring DeviantCord  (Self Host)
************************************
DeviantCord requires you to get a token from DeviantArt and Discord in order to use the bot.
This page will guide you in getting those tokens.

Getting Registered
******************
In order to get the needed tokens to run the bot you will need to register the bot with Discord and DeviantArt
respectively

**Requirements**

* Discord Account
* DeviantArt Account (Preferably one that is not your primary)

DeviantArt
----------
First go to the developers page for DeviantArt `here <https://www.deviantart.com/developers/>`_

Register Click "Register Your Application"

..  image:: RegisterDAApp.png

Title the App whatever you want and click save. Since you are not using OAuth, you do not need to specify a callback URL

This should take you to your apps in the Developer page revealing your clientid and clientsecret

..  image:: tokensda.png

Open your client.json file where DeviantCord is being stored (With An Editor such as `Atom <https://www.atom.io>`_
or WinSCP's default editor


..  image:: changetokens.png

Replace the clientid and client secrets on the deviantart page with what is inside the file and save.

Discord
-------

First off we need to register the Bot with Discord,
go to the developers page `here <https://www.deviantart.com/developers/>`_

Click New Application

..  image:: appsdiscord.png

Add whatever information you want including the icon for the bot and the name for the bot.

Save your changes


Go to the Bot Category on the left

Click Add Bot

..  image:: addbotuser.png

**You do not need to specify permissions at the bottom. The bot will already have it setup**

Adding A Bot user to the bot will now make the app a full fledged bot! Now we need to invite the bot the server it will be running on

Go to OAuth2

Enable the bot scope and copy the link generated into your browser and invite the bot to the server its needed in.

..  image:: discordoauth.png

The Bot should appear on the server offine. Now go back to the bot tab and grab the token for the bot

..  image:: bot_tokendiscord.png

Grab the token and put in the client.json file where DeviantCord is stored.

..  image:: changetokens.png

The bot is now setup!


