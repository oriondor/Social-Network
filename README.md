To launch this app you need to create config.py file that'd consist of one variable called mongo_uri that points to your MongoDB.

WSGI deploy is not provided for this app, so in order to launch this app you also need to add variables from environment_variables.txt and run 'flask run' command

When you first launch this app, you should create user 'admin' from regular register form, go to '/standart_user_photo' link and then upload an image that will be used as standart profile image for every new registered user. Example provided.

All required packages are in requirements.txt

Authentication mechanism for this app is JWT access token. JWT_Extended lib was used. 

SHORT DESCRIPTION:

Social Network is a small social network, where you can share you feelings creating posts. Also you can like posts of other people.

To create new post or like post of another person, you need to log in. If you don't have an account, you should create it first. After you log into the website, the access-token is saved into your cookies. 
As a user, you can now create/delete your posts and like or dislike posts of others.
When you like or delete post, the AJAX request is sent to a server, so the page doesn't need to be reloaded.

if you go to '/api/analytics/?date_from=2020-02-02&date_to=2020-02-15' you will get the analytics for likes count that is aggregated by day in JSON format.

if you go to '/api/activity/{username}' where {username} is the username of existant user, you'll get info about last_activity in JSON format. This info includes last logged date, when and whom profile was last viewed by this user, when this user last viewed posts and also date of last post like/dislike/deletion.