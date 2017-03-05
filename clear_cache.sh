#!/bin/bash

rm -f ~/.mozilla/firefox/o6eogpb0.default/sessionstore-backups/recovery.bak

rm -f ~/.mozilla/firefox/o6eogpb0.default/sessionstore-backups/previous.js

rm -f ~/.mozilla/firefox/o6eogpb0.default/sessionstore-backups/recovery.js

rm -rf ~/.mozilla/firefox/o6eogpb0.default/storage/temporary/*

rm -rf ~/.cache/mozilla/firefox/*.default/*

rm -f ~/.mozilla/firefox/*.default/sessionstore-backups/recovery.js

rm -f ~/.mozilla/firefox/*.default/sessionstore-backups/recovery.bak

rm -f ~/.mozilla/firefox/*.default/content-prefs.sqlite

rm -f ~/.mozilla/firefox/*.default/search.json

rm -f ~/.mozilla/firefox/*.default/places.sqlite

rm -f ~/.mozilla/firefox/*.default/logins.json

rm -rf ~/.mozilla/firefox/o6eogpb0.default/storage/default/*

rm -f ~/.mozilla/firefox/o6eogpb0.default/formhistory.sqlite

rm -f ~/.mozilla/firefox/o6eogpb0.default/bookmarks.html

#reference ==> http://kb.mozillazine.org/About:config_entries

#location of prefs.js ==> ~/.mozilla/firefox/o6eogpb0.default/ user.js is not present by default

#append these key vals in the prefs.js file: (or you can create a user.js file that overrides all prefs.js ==> recovering back to prefs.js is hard tho)
#user_pref(browser.search.defaultenginename,Google)
#user_pref(browser.search.defaulturl,http://www.google.com/search?lr=&ie=UTF-8&oe=UTF-8&q=)

