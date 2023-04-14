Activate venv in powershell
$ ./venv/Scripts/activate
if error occurs use
$ Set-ExecutionPolicy Unrestricted -Scope Process

Deploy to Heroku
add git repository to Heroku existing repository

$ heroku login

$ heroku git:remote -a freezer-engine

Push to Heroku server
$ git push heroku master