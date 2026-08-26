# Changelog

All notable changes to +2 Cipher are documented here.

## 1.2.0
- fix: ensure git tag exists and is specified for gh-release action when run manually
- fix: add workflow_dispatch trigger to release.yml so it can be manually triggered from GitHub UI
- feat: auto changelog from git commits on release tag, dynamic version in About screen
- feat: make APP_VERSION dynamic from buildozer.spec, bump to 1.1.0, update changelog
- fix: change softinput_mode from pan to resize so keyboard doesn't push input card off screen


## 1.2.0
- fix: add workflow_dispatch trigger to release.yml so it can be manually triggered from GitHub UI
- feat: auto changelog from git commits on release tag, dynamic version in About screen
- feat: make APP_VERSION dynamic from buildozer.spec, bump to 1.1.0, update changelog
- fix: change softinput_mode from pan to resize so keyboard doesn't push input card off screen


## 1.2.0
- fix: add workflow_dispatch trigger to release.yml so it can be manually triggered from GitHub UI
- feat: auto changelog from git commits on release tag, dynamic version in About screen
- feat: make APP_VERSION dynamic from buildozer.spec, bump to 1.1.0, update changelog
- fix: change softinput_mode from pan to resize so keyboard doesn't push input card off screen


## 1.1.0
- Fixed crash when opening History or Favorites tab
- Fixed ghost tooltips getting stuck on Android after tapping Copy/Share/Star buttons
- Fixed keyboard not opening on quick tap in the input field
- Fixed app crashing when typing (AttributeError in keyboard handler)
- History now saves after a 1.5s typing pause instead of every keystroke
- Input no longer pushed off screen when keyboard opens

## 1.0.0
- Initial release
- Encode / Decode with +2 / -2 alphabet shift
- Live transformation mode
- Conversion history with search
- Favorites with star button
- Dark / Light theme toggle with accent colors
- Full desktop (Linux) and Android support
- Share and copy output
- Settings: char limit, shift value, history limit, font size, density
