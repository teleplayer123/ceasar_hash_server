# ceasar_hash_server
Description
----
This is an old project I made as a way to practice using python sockets. Also, I wanted to try to mimic
a user login, using a ceasar cipher as a hash method for passwords. This is not mean to be a completely
safe or secure program, so real world use would require quite a bit of fine tuning.

Contents
----
- [Server program](#server)
- [Client program](#client)

<a name='server'></a>Server: 
----
- Handles requests for creating new usernames and passwords.
- Stores hashed passwords and salts in local directory files.
- Handles loading and saving of user information.

<a name='client'></a>Client:
----
- Creates cli for making requests to register new user.
- Mimics user login by comparing user input against registered username and password.
- The 'Get Hash' option is just to see the output of registered hashed password, and not meant to
  be a secure function.
 
 
Credits
----
-Mark Summerfield: Programming in Python3
