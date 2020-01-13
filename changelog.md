# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## DeviantCord 2
### [bt-2.0.7]

## Changes
- Mature Folders are now require the folder to be in a NSFW channel.

## Fixes
- Fixed an issue with minimum role ID not being the correct data type. 
### [bt-2.0.6]

## Fixes
- Fixed multiple crashing bugs from DeviantCord 1
## Removals
- Users no longer need to wait for DeviantCord staff to approve the bot on their server!
- Removed the addartist command, as addfolder will now add an artist regardless of whether the artist has a listener on the
guild involved or not. 
- Removed the manualSync command, for stability reasons. 
- Removed the reload command, due to server specific data being stored in a database and being applied instantly. 
- Artdata is no longer used in a JSON file. 
- The Errite Error Reporter is no longer used. As we have moved everything over to Sentry. 

## Changes
- Join Requests for the public bot no longer have to manually approved by the DeviantCord Staff. The bot can now jump
right in to your server by using the bot invite link on the Github, Documentation, or our Discord Server. 
- Self Hosted bots for DeviantCord 2 no longer needs to have separate configured bots running in different screen sessions.
DeviantCord2 runs within 1 screen session and is multiserver.
- You are no longer limited to only 1 channel for a specific folder serverwide. You can now have the same folder
posted to multiple channels (Not within the same command, you will need to use the command and specify each channelid
one at a time)
- Errite Error Reporter is no longer used on DeviantCord, we have moved all error reporting for the bot to Sentry.io.
This was implemented for our Production Servers to spot bugs more quickly and only grabs error data from the public bot.
- Json Data storage for Deviations are no longer used. DeviantCord uses PostGres 11+
- Cleaned Error Handlers for commands.
- **DeviantCord will automatically delete all listeners if the bot leaves the server for any reason.**
- AddFolder, deletefolder and update property commands have changed. Check the help command for more information!
- All commands have been rewritten to work with SQL, and multiserver. 
- Some config.json values are no longer used. 
- Debug Level for Discord no longer is used in the Discord Log file or DeviantCog
- DeviantCog now logs in JSON format, with additional information.
- DeviantCord now requires additional packages to run. psycopg2 sentry_sdk python-dateutil python-json-logger markdownify
- The Default prefix has changed to ~
- DeviantCord2 no longer uses the Apache License. We now use the AGPL v3.
## Additions
- Added Mature Property, to addfolder and addallfolder. You can now specify if you want Mature Deviations to be posted.
- Added support command for users to easily get access to the DeviantCord Support server. 
## DeviantCord 1
### [Beta]

### [bt-]

## [bt-1.4.0] - 2019-07-10

## Added 
- AllFolder Listeners via the addallfolder command
- Added AllFolder related fields in artdata.json
- Added venv for Linux and Windows for Developers
- Devistion Notifications now use Embeds. Embeds have less of an issue resolving images.
- More debug messages in logs for DeviantCog, and daparser

## Changes
- artdata.json version changed to bt-1.4.0
- Json path for folderlisteners have been moved to art-data/artist/folders/foldername
- listfolders now accounts for allfolders
- AllFolder Listeners do not store all Deviation ID's when it is imported for the first time. Instead it stores the latest 10.
- AllFolder Listeners use slicing when comparing UUID's for better memory usage and a faster response time.
- listfolders 

## Fixed
- Issues with preview images not showing sometimes.
- The update inverse and update hybrid command not working at all
- Fixed a bug where the listfolder command could stop working if you had enough folder names that exceeded the 2000
character limit. 
- Fixed a crash with the bot that occurs with a discrepency with the error handler. 


## [bt-1.3.0] - 2019-06-26
## Added 
- Errite exclusive fields such as errite and errite-channel-id in config.json. This is used by the new Error Notifier that lets DeviantCord Support know of errors experienced by the public bot as soon as it happens.
- erritetoggle command that allows for server owners using the public DeviantCord bot to opt out of the Error Notifier

## Changes
- DeviantCord now allows for third party cogs written with DiscordPy to used be alongside DeviantCord on self-hosted bots. Though we are not responsible for any cogs you use with DeviantCord.  
- config.json version updated to bt-1.2.5

## [bt-1.2.5] - 2019-06-22
NOTE THIS BUILD: Was not released to the public, it was only used on our public hosting before an incident in the community caused us to have to implement a needed feature thus the creation of bt-1.3.0
### Fixed
- An inconsistency with skiprolecheck not being declared in addfolder that caused a UnBoundLocalError
- Incorrect naming in logs for deviantcog, and the discord debug file
- Issues with a the findFolderUUID method always returning None if the artist does not have more then 10 folders
- An infinite loop that would occur if a gallery with less then 20 deviations uses the getGallery method. This would cause the bot to freeze and stop responding. The SSH session using the bot would also freeze/ctrl + c would not respond. 
- An issue with the error handler not being awaited for

### Changes
- If the getGallery method in daParser interacts with a galleryfolder with less 20 deviations, the bot will recognize it and break out of the while loop to prevent an infinite loop.
- In daParser the getGallery method now uses findDuplicateElementArray instead of findDuplicateElementJson
- The error handler method in daCommands is no longer async.
- The error_handler has been reworked slightly to at least perform basic diagnostics using methods from the upcoming bt-1.4.0 build of DeviantCord.

### Removed
- Some console output that could be easily misinterpreted. 

## [bt-1.2.4] - 2019-06-11

### Fixed
- An issue where the bot would not correctly catch messages meant for another server using the same token as the bot.

## [bt-1.2.3] - 2019-05-19


### Added
- Added command_error handler for handling invalid commands

### Fixed
- Fixed invalid commands from spamming the console.


## [bt-1.2.2] - 2019-05-18


### Added
- Added additional log messages to the manualGetToken
- Added Rate Limit Measures for SyncGallery, that will trigger upon getting a HTTP Error 429

### Fixed
- Fixed an issue where an error encountered in error_handler would stop all automatic tasks for the bot.
- Fixed an issue where an 503 Error from DeviantArt would stop the bot from looking for new deviations
- Fixed an issue where the word await was missing for the manualGetToken method.

### Changed
- manualGetToken now runs as a last resort to renew all async tasks
- softTokenRenewal now replaces the functionality of manualGetToken
- Error handler no longer exits when detecting an Unauthorized or bad client error.  Depending on the error, the bot will ignore it or will try to take the necessary steps to fix it.
- Changed error_handler to async



## [bt-1.2.1] - 2019-05-15

### Fixed
- Really fixed the jsonlock from not unengaging in the SyncFolders
- Fixed a bug where the offset was being saved, when it should not with inverse. 
- Fixed a typo in permissions check


## [bt-1.2.0] - 2019-05-14

### Added
- Added Checks for invalid
- Added additional check near the beginning for an active json lock to prevent encountered exception from turning off a json lock that may be still in use.
- Hybrid Mode for listeners, meaning that for some artists who do not stay inverted or non-inverted with their folders this will check the first 20 deviations in a folder and also check the next 10 from the previous count. 
- updatehybrid that will allow you to enable or disable hybrid for a folder. Just note that by default a non-inverse folder will have it enabled by default. On the otherhand 
- Converter from bt-1.0.1 data for config and artdata to the new format bt-1.2.0
### Changed
- updateinverse will now set the hybrid to the appropriate setting. As the hybrid setting is ignored if it is an inverse folder. 

### Fixed
- Fixed an issue where using comparison operators on Roles when a role was first setup would not work. 
- Fixed an issue where new config.json would have the 1.0.0 version
- Fixed an issue with the setuprole command not properly adding the new roleid to memory.
- Fixed an issue with deprecated role checks for Admin
- Fixed an issue where the json lock wouldn't be closed when the roleid was invalid. 
- Json lock was not properly enabled when using the updatechannel command
- Fixed some areas where the json lock would not be released.
- Fixed reload command
- Fixed syncgalleries from not initializing the json lock


## [bt-1.1.0] - 2019-05-13

### Added
- deletefolder command, this will allow you to deletefolders
- listfolders command, that will list all current folder listeners
- added json lock to prevent issues during a deletion of a folder. 

### Updates
- Updated Repository for Discord.py version 1.1.1, websockets version 7.0 and urllib3 to 1.25.2

### Changes
- Changed some log messages
- Changed the task error handler to proper indentation

### Fixes
- Fixed an issue with addFolder where a if statement would not return if an folder already exists
- Fixed an error message back from an very old build that has since then changed 
- Fixed an log message that was not given a level, and as a result it stopped the updateinverse command from working.
- Fixed an conditional statement in updateinverse that would not allow the inverse to be updated to false. 
- Fixed an error message in addartist that had a spelling error
- Fixed an error message from returning in addartist for an invalid DA Folder UUID.
- Fixed an error message from returning with an invalid DA Folder UUID for a completely different condition
- Fixed ErrorHandler for Tasks to automatically release the json lock when an error occurs within a task. 


## [Beta]
## [bt-1.0.1] - 2019-05-10
### Fixes
- Fixed an issue in regards to ChannelID's working on other servers.
- Fixed the issues with logs all logs should work as intended
- Fixed the setprefix error handler
- Updated the help command
- Fixed an issue with configs not generating correctly


## [bt-1.0.0] - 2019-05-10
### Added
- updateinverse command, this will set a folder to the inputed inverse setting (true or false)
- Version field in all json configs. 
- Permissions page to documentation
- Reload command for daCommands
- Version field in all json configs. 
### Changed
- Help Command is now in the daCommands Cogs
- THe Admin only commands now use a ~$ prefix. These commands are the only ones unaffected 
### Fixes
- Fixed an issue with the jsonTools with folder names being improperly referenced.
- Fixed an issue with DAParser and daCommands where artist's names were not being put in JSON in lowercase. 
- A bug in the checks for rather a guild exists/ when DM's are used that raised an Attribute Error.
- A potential error that would occur if roleid value was invalid. 
- Fixed an error message from not properly sending
- Fixed an issue with rotating log names. 
- Put in an exception that will allow members with Administrator Permissions to bypass checks for role permissions to setup the bot.
- Fixed a case sensitive issues with input and artdata. 
- Fixed an issue with inverted galleries where the newest deviations would be posted in the wrong order. 
- Fixed an issue
- Fixed an issue with logging output.
- Fixed an issue where logs would stop.
- Fixed an issue with filehandlers with logs.

## [Unreleased]
## [ib-0.10.0] - 2019-05-06
## Added
- Sphinx is now used is the project for documentation. 
- DocStrings to some methods. We will start going through them and documenting the functions. 
- Cogs are now used to allow for easy reloading of the bot without having to restart the bot manually.
- reload command, the bot can now be manually reloaded instead, of the bot automatically reloading when it needs to.  
- setsynctime command, you can now set the frequency of when deviations are checked within the bot. 
- updatechannel command so that admins can update an existing listener to a new channel.
- updateprefix command so that the prefix can be changed on the fly. 
- setuprole command so that you can define a role that will be required to access the bots commands. For the first time execution, this command needs to be executed by a user with a role that has Administrator
- Log channel feature for admins, you can specify a channel to know if something is wrong with the bot. 
- Parameter Checks for commands to make sure they are not empty
- Various checks for arguments to make sure that the proper datatype is being used. 
- More Http codes indicators for errors.
- Messages that will now vary depending on the http code encountered to give better context. 
- Various error messages to be more clear if something is wrong. 
- Checks to make sure that artdata exists, and methods that will generate a blank artdata in configManager
### Changed
- Made all commands guild_only/ the bot will no longer respond via DM. 
- Major refactoring, removed the com namespace in com.errite, it is now just errite.
- com.errite.deviantart/errite.deviantart python package is now just errite.da
- renamed the discord python package to just discordapi
- removed the json pythonpackage
- Permissions are now required in order to execute commands. 
- The Bot python file no longer has the commands inside of it, it now has it in the cogs folder. 
- Changed the Artist not found message to be more clear for when someone forgets quotations
### Fixes
- Fixed a Module Not found error with the discord python package and json python package
- Fixed a bug in the multitoken check for addfolder
- Fixed a bug with the updatechannel command

## [ib-0.9.0] - 2019-04-25
## Added
- Additional error checking measures in regards to DA Clientid's and clientsecrets. 
- Added config.json to store bot settings and client.json to store token information for the bot.
- Added methods to check for config files and act accordingly
- Added methods to generate the needed json objects for the new configs 
- Added publicmode/singletoken. It will allow you to run the bot using the same token on multiple servers. Just keep in mind
that you need to run a separate instance of the bot per server. 
- Added exceptionhandler for async methods for the bots tasks. 
- Prefix customization
- Logging Toggle, not currently used but will be in the next update. 
### Fixed
- Fixed the addfolder inverse field from not properly being saved due to a programming error. 
- Word spelling errors in some of the methods
## [ib-0.8.0] - 2019-04-24
### Added
- Added folderExists to jsonTools to check if a folder truly exists for a specific user
- Added publicmode, used for using the same discord token under several bots under a different server. Pretty useless for selfhosting.
- Multifolder's syncs for multiple artists. The bot can now listen to multiple folders per artist instead of just one!
- Inverse field for DAParser's 
- Inverse field for the bots addFolder and addArtistCommand
- Added various error checking measures, for example an Invalid artist will now let the user know that the artist they requested is invalid. The same goes for invalid folders. 
- There are now checks on the inverse field to make sure that a bool is properly received by other functions. 
### Changed
- addfolder now checks for a valid folder and additionally checks to see if an artist does not exists.
- DAParser's getGallery now accounts for the inverse field, and will act accordingly with the Inverse field
- the addfolder and addartist command now has the inverse parameter and will pass it on to the createArtistData, createFolderData and findGalleryFolder
- Fixed a bug where the inverseparameter was not being correctly saved to artdata.json
- JSON object references have been updated to account for Multifolder sync and inverses. 


