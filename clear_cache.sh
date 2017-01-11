#!/bin/bash

rm -f ~/.mozilla/firefox/o6eogpb0.default/sessionstore-backups/recovery.bak

rm -f ~/.mozilla/firefox/o6eogpb0.default/sessionstore-backups/previous.js

rm -rf ~/.mozilla/firefox/o6eogpb0.default/storage/temporary/*

rm -rf ~/.cache/mozilla/firefox/*.default/*

rm -f ~/.mozilla/firefox/*.default/sessionstore-backups/recovery.js

rm -f ~/.mozilla/firefox/*.default/sessionstore-backups/recovery.bak

rm -f ~/.mozilla/firefox/*.default/content-prefs.sqlite

rm -f ~/.mozilla/firefox/*.default/search.json

rm -f ~/.mozilla/firefox/*.default/places.sqlite
