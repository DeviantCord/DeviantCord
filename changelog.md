# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
This is from Internal Builds before the official release of the bot
## [ib-0.9.0] - 2019-04-25
## Added
- Additional error checking measures in regards to DA Clientid's and clientsecrets. 
- config.json to store bot settings and client.json to store token information for the bot.
- Methods to check for config files and act accordingly
- Methods to generate the needed json objects for the new configs 
- Exception Handler for async methods for the bots tasks. 
- Prefix customization
- Logging Toggle, not currently used but will be in the next update. 
### Fixed
- addfolder inverse field from not properly being saved due to a programming error. 
- Word spelling errors in some of the methods
## [ib-0.8.0] - 2019-04-24
### Added
- Added folderExists to jsonTools to check if a folder truly exists for a specific user
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
