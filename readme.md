xbps-cache-prune
================

Warning this has only been tested by me on a single system

USE THIS AT YOUR OWN RISK

Its important you understand how it works, when determining which files should be deleted it sorts the candidates by creation date of the file and not by package version number

Held packages and their full dependencies are not included when determining which files to delete

by default the script will only do a dry run, you should always do a dry run first and check with the actual contents of the cache before proceding

The script takes 2 parameters -n is the number of packages to keep for each package, use -d false to actually delete files from the cache

a dry run does not require super user privilages

Please do send feedback via http://bedroomcoders.co.uk/captcha/

