# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
This is from Internal Builds before the official release of the bot
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
- the addfolder and addartist command now has the inverse parameter and will pass it on tot he getGalleryFunction
- Fixed a bug where the inverseparameter was not being correctly saved to artdata.json
- JSON object references have been updated to account for Multifolder sync and inverses. 


