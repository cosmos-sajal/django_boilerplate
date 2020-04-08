# Authentication APIs written in Django RestFramework

https://travis-ci.org/cosmos-sajal/auth_app.svg?branch=master

This is a base repository written in Django and Django Rest Framework that can be used for setting up authentication for your Django Projects.


## This repoistory contains the following APIs -

#### `POST /api/v1/user/register`
This API will register user and create them in core_user table in DB after parameter validations.

#### `POST /api/v1/user/login`
This API will return access and refresh token after authenticating the user.
Works both with emai-password and mobile_number-otp pairs.
This API has default Django Throttling class (UserThrottle), and is set to 3/min

#### `POST /api/v1/user/generate/otp`
This API will generate OTP and sets it in redis, you can extend the API to send the OTP on the SMS sender of your choice.


## Tech Stack Used -
Django, DjangoRestFramework, PostgreSQL, Redis, Docker, JWT Authentication.


## How to use this -
1. You should have at least docker installed on your system.
2. After installing docker, take a pull/fork of this repo.
3. Create a new file `secrets.py` inside app/app/ folder alongside settings.py and put the following in it -
```
from .settings import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'secret_key'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.environ.get('DB_HOST'),
        'NAME': 'auth_app_dev',
        'USER': 'postgres',
        'PASSWORD': 'password',
    }
}

# Redis Cache
CACHES = {
    'default': {
        'BACKEND': "django_redis.cache.RedisCache",
        'LOCATION': 'redis://redis:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient'
        }
    }
}

```
Keep adding your secret keys in this file.

4. Run `docker build .` from the auth_app folder.
5. Run `docker-compose build` to build the API and it's dependencies.
6. Run `docker-compose up` to run all containers.
7. Hit `localhost:8000/`, Django front page should come.
You can check all the containers running using `docker ps`, and user `docker exec -it <container_id> sh` to enter any container.


#### NOTE - If you get database not found, just enter the postgres container using the above command, and create a new database -
1. `docker exec -it <postgres container id> bash`.
2. `psql -U postgres`
3. `create database auth_app_dev`
