# Example shell script for linux to generate and automatically open
# an html table using the system default web browser

./cmc-get.py -html > cmc-get.html
x-www-browser cmc-get.html

