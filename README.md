# Bookservice
A web dev + cloud Project

### Features 

- Bootstrap admin dashboard provided by flask-admin
- Ckeditor to write perfectly without defining HTML tags
- Werkzeug.security password authentication
- Authorization by flask-login (csrf-tokens enabled)
- CRUD functionality Book service

## In LocalHost with same DB

* Install all dependencies by ```pip install -r requirements.txt```
* Run app.py and head to http://127.0.0.1:5000/

## In localHost with own DB

* Install all dependencies by ```pip install -r requirements.txt```
* Delete Database.db

* Open python terminal

```python
from app import db
db.create_all()

from werkzeug.security import generate_password_hash

from app import User

usr = User(username='{any usename}', password=generate_password_hash("{any password"))

db.session.add(usr)
db.session.commit()
```
* Run app.py and head to http://127.0.0.1:5000/

## For heroku

* Change database uri in config.cfg to postgres one after creating app at Heroku
* Change secret key to your own

* Just for getting random secret key (optional) or you can put your own
```python
import os
os.urandom(18)
```
* Create database on heroku-postgres as above defined process
* Upload to heroku cloud by running following command
```python
$ git add .
$ git commit -am "My book services"
$ git push heroku master
```
