

# SMTP System

This program was created to as part of the Networks and Security class at University of Derby.
Its a Server - Client implementation of the email RFC-821 standard (and partial RFC-5321 implementation), with the change of the server storing the emails rather than forwarding them, as well as user accounts with shared mailboxes.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.


### Prerequisites

Any **Windows**/**Linux**/**MacOs** machine running **Python 3.7** & Higher.

The program can run on any OS, however testing was mostly done in Windows, so there might be unexplored bugs with other operating systems.


### Usage

1. Download the latest Server and Client version archive (.zip) from the [releases](https://github.com/MrThanasiz/NWS_AS/releases) tab.
2. Extract the folder from the zip.
3. Modify host & port values in SMTPServer.py & SMTPClient.py as required (by default they're set to run on localhost and port 9999)
6. Run SMTPServer.py on the server machine & SMTPClient.py on the client machine.


## Built With

* [Python](https://en.wikipedia.org/wiki/Python_(programming_language)) - The programming language used.
* SMTPServer, SMTPClient, SMTPServerLib, SMTPClientLib were provided by the teacher of the class, and were slightly modified to work with the rest of the code.


## Versioning

For the versions available, check the [Releases tab on the repository](https://github.com/MrThanasiz/NWS_AS/releases). 
