AllCapsBot
==========

IRC bot written in Python that kicks users in specified channels if they don't use uppercase.

Generally best used in a channel like #trashtalk

This assumes a NickServ operator that controls identification.

Configuration
=============

In all_caps_bot.py you can optionally change:
* the nickname AllCapsBot uses
* channels it monitors
* a specific character that would not trigger the bot if the IRC message starts with it
* nicknames specifically not to monitor (defaults with ChanServ and itself)
* the message AllCapsBot sends to users when it kicks them

Usage
=====

1. Obtain an identification for the AllCapsBot nickname.
2. Issue op privileges (or just kick privileges) to AllCapsBot.
3. Run python all_caps_bot.py from a command line.
4. Specify the host, port, IRC server password, and IRC ident password