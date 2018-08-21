# IRC Replacement

**Author**: Steph Harper, Alex Stone
**Version**: 1.0.0

## Overview
Allow us on the same network to talk to each other using the built in bash(or otherwise) console.

## Getting Started
Install python 3.6+, then run python3 server.py while in the same directory as the server.py file. This will start the server on the port it says. To connect to the server type nc localhost PORT_NUMBER into the console.

## Architecture
This is a TCP server using Python 3.6+ technology, AND NOTHING ELSE!

## API
@dm <username> <message> | This sends <message> to <username>
@nick <name> | Change your name for this session to <name>
@list | Lists every active user in the session to all other active users
@quit | Quits you out of the session
All other input will be interpreted as a message to the whole server


## Change Log
20-08-2018 5:22 PM : Initial Version 1.0 pushed to merge with master.
