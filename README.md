# VEKIN README

# Requirements
* [python 3.6.x](https://www.python.org/) or higher (pip also come with python 3.4.x or higher)
* [mariadb 10.3.x](https://mariadb.org/) or higher
* [memcached 1.5.x](https://memcached.org/) or higher

# Setting Up
### Project
* clone project
> $ git clone https://glrepo.vekin.co.th/co2/co2-backend.git

* use [virtualenv](https://virtualenv.pypa.io/en/latest/) or install packages globally


* pip install -r requirements.txt

* create [local_settings.py](#local-settings) at ev-home-api/VEKIN

### Database
> $ sudo mysql -uroot

> MariaDB [(none)]> GRANT USAGE ON *.* TO 'root'@localhost IDENTIFIED BY 'password';

> $ CREATE DATABASE DATABASE_NAME CHARACTER SET utf8 COLLATE utf8_thai_520_w2;

* create table in database
> $ python manage.py migrate

# Run Project
### Django
* run server
> $ python manage.py runserver

### Celery

* run worker
> $ celery -A co2 worker -l info -E -Q user,user_priority,transaction,export,encode

* run worker explicitly (use this one)
> $ celery -A co2 worker -l info -E -c 2 -O fair

* run monitor
> $ celery -A co2 events -l info --camera django_celery_monitor.camera.Camera --frequency=2.0

* delete all tasks
> $ celery -A co2 purge

### Run with Docker
* run mariadb
> $ docker run -d --restart always --name mariadb -p 3306:3306 --env MYSQL_ROOT_PASSWORD=password -v /..{{path of your user}}../mnt/mariadb/var/lib/mysql:/var/lib/mysql -v /..{{path of your user}}../mnt/mariadb/etc/mysql/mariadb.conf.d/:/etc/mysql/mariadb.conf.d/ mariadb:10.6.5-focal

* run redis
> $ docker run -d --restart always --name redis -p 6379:6379 --env ALLOW_EMPTY_PASSWORD=yes -v /..{{path of your user}}../mnt/redis/:/usr/local/etc/redis/redis.conf -v /..{{path of your user}}../mnt/redis-data:/data redis

* run memcached
> $ docker run -d --restart always --name memcached -p 11213:11211 memcached 

* run rabbitmq
> $ docker run -d --restart always --name rabbitmq  -p 5673:5672 -p 15673:15672 -v /..{{path of your user}}../mnt/rabbitmq/data/:/var/lib/rabbitmq/ -v /..{{path of your user}}../mnt/rabbitmq/log/:/var/log/rabbitmq -v /..{{path of your user}}../mnt/rabbitmq/rabbit.conf:/etc/rabbit/rabbit.conf rabbitmq:3-management-alpine

* run flower
> $ docker run -d --restart unless-stopped --name flower -p 5555:5555  mher/flower:0.9.5 flower --address=0.0.0.0 --broker='amqp://admin:admin@rabbitmq:5672/myvhost' --port=5555 --logging=DEBUG

# Problems
### [mysqlclient](https://github.com/PyMySQL/mysqlclient-python) problem
* for Mac OS
> brew install mysql-connector-c

> https://pypi.org/project/mysqlclient/

* for Ubuntu/Linux
> sudo apt-get install python-dev default-libmysqlclient-dev


### [NameError: name '_mysql' is not defined](https://stackoverflow.com/questions/7475223/mysql-config-not-found-when-installing-mysqldb-python-interface) problem
* for Ubuntu/Linux
> sudo apt-get install libmariadb-dev
> 
> sudo apt-get install libmariadbclient-dev


# Lib WeasyPrint
* for Mac OS
> brew install python3 cairo pango gdk-pixbuf libffi

> [Ref.](https://weasyprint.readthedocs.io/en/stable/install.html)


### [NameError: python setup.py egg_info Check the logs for full command output.](https://stackoverflow.com/questions/61063676/command-errored-out-with-exit-status-1-python-setup-py-egg-info-check-the-logs) problem

>python3 -m -pip install --upgrade pip

>pip install gevent --pre

>pip install auto-py-to-exe 


### [mysql-utf8](https://mathiasbynens.be/notes/mysql-utf8mb4) incorrect string value
* for Ubuntu/Linux
```bash
# Modify connection, client, and server character sets
$ sudo gedit /etc/mysql/my.cnf

# data
[client]
default-character-set = utf8mb4 

[mysql]
default-character-set = utf8mb4

[mysqld] 
character-set-client-handshake = FALSE 
character-set-server = utf8mb4 
collation-server = utf8mb4_unicode_ci 

# restart MySQL
$ service mysqld restart
# or
$ service mysql restart
```

### [xmlsec](https://github.com/mehcode/python-xmlsec) problem
* for Mac OS
> brew install libxml2 libxmlsec1

* for Ubuntu/Linux
> sudo apt install libxml2-dev libxmlsec1-dev libxmlsec1-openssl

### error: command 'clang++' failed with exit status 1
> xcode-select --install
> brew install --with-toolchain llvm
> pip install -U xxx

* for Ubuntu
> sudo apt-get install python3 python-dev python3-dev \
     build-essential libssl-dev libffi-dev \
     libxml2-dev libxslt1-dev zlib1g-dev \
     python-pip

### For psycopg2
> https://stackoverflow.com/questions/26288042/error-installing-psycopg2-library-not-found-for-lssl


### Local Settings
* local_settings.py insert this code to file at same path with setting.py

```python
from .settings import INSTALLED_APPS, MIDDLEWARE

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS.append('django_extensions')
INSTALLED_APPS.append('debug_toolbar')
MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
INTERNAL_IPS = ('127.0.0.1',)

CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_HTTPONLY = False
#
DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ev_vekin',
        'USER': 'root',
        'PASSWORD': 'password',
        'TEST': {
            'NAME': 'hrd_test',
        },
        'HOST': '127.0.0.1',
        'PORT': '3306'
    }
}


CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

SWAGGER_SETTINGS = {
    'IS_ENABLE': True,
    'SHOW_REQUEST_HEADERS': True,
    'IS_SUPERUSER': True,
    'VALIDATOR_URL': None,
}

```
