# 0. Environment
OS: CentOS 7.5

Python: 3.6.6

DB: MariaDB 5.5.56

FrameWork: Django 2.1

JS FrameWork: Node.js 8.12

Asynchronous Processor: Celery 4.2.1

Memory Storage: Redis 4.0.11


# 1. GIT
$ mkdir -p /home/Dev && cd /home/Dev && su corebrdg

$ git clone https://github.com/joekim2000/cbwms.git

$ cd cbwms


# 2. CBWMS installation guide
- Install all corebrdg Dist (NAS:FileBridge/Source/CAMS/Installer/Corebridge)

- corebrdg install guide (NAS:FileBridge/Source/CAMS/Installer/Manual/Corebridge)

- Install all CBWMS material (NAS:FileBridge/Source/CAMS/Installer)

- Combined Approval System guide (Reference to Combined Approval System section in NAS:FileBridge/Source/CAMS/Installer/Manual/CAS/통합승인시스템_개발지침서_v1.0_20181010.pptx)

- copp NAS:FileBridge/Source/CAMS/Installer to /home/orebrdg/INSTALL

$ cd /home/corebrdg/INSTALL/OS

$ vi /etc/yum.repos.d/CentOS-Base.repo

...

[dvd]

name=CentOS-$releasever - DVD

baseurl=file:///mnt

gpgcheck=1

gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7

$ mount -t iso9660 -o loop CentOS-7-x86_64-DVD-1804.iso /mnt


# 2.0. Maria DB
$ yum install --disablerepo=\* --enablerepo=dvd mariadb-server

$ yum install --disablerepo=\* --enablerepo=dvd mariadb-devel

$ sudo systemctl start mariadb

$ sudo systemctl enable mariadb


# 2.1. Python V3.6.6
$ cd ../Python

$ tar xzf Python-3.6.6.tgz && cd Python-3.6.6

$ ./configure --enable-optimizations

$ make altinstall


# 2.1.0 Alias  (Use Python3.6 for default)
$ vi ~/.bashrc

if [ -f ~/.bash_aliases ]; then

. ~/.bash_aliases

fi

$ vi ~/.bash_aliases 

alias python="/usr/local/bin/python3.6"

alias pip="/usr/local/bin/pip3.6"

$ source ~/.bashrc

$ source ~/.bash_aliases


# 2.1.1 Alias  (corebrdg account)
$ su corebrdg

$ vi ~/.bashrc

if [ -f ~/.bash_aliases ]; then

. ~/.bash_aliases

fi

$ vi ~/.bash_aliases 

alias python="/usr/local/bin/python3.6"

alias pip="/usr/local/bin/pip3.6"

$ source ~/.bashrc

$ source ~/.bash_aliases

$ exit

$ cd ../..MySQL


# 2.2 MySQL Client
$ pip install mysqlclient-1.3.13.tar.gz

$ cd ..


# 2.3. Django 2.1
$ cd Django

$ pip install pytz-2018.5-py2.py3-none-any.whl

$ pip install Django-2.1.tar.gz

$ pip install django_cors_headers-2.4.0-py2.py3-none-any.whl


# 2.3.1. Django FrameWork
$ pip install djangorestframework-3.8.2-py2.py3-none-any.whl

$ pip install Markdown-3.0.1-py2.py3-none-any.whl

$ cd ..


# 2.4. Celery
$ cd Celery 

$ pip install billiard-3.5.0.4.tar.gz

$ pip install vine-1.1.4.tar.gz

$ pip install amqp-2.3.2.tar.gz

$ pip install kombu-4.2.1.tar.gz

$ pip install celery-4.2.1.tar.gz

$ pip install django-celery-beat-1.1.1.tar.gz

$ pip install django_celery_results-1.0.1.tar.gz

$ celery --help

$ celery worker --help

$ celery beat --help

$ mkdir -p /var/run/celery

$ mkdir -p /var/log/celery

$ chown -R corebrdg. /var/run/celery

$ chown -R corebrdg. /var/log/celery


# 2.5. Redis
$ cd Redis

$ yum install --disablerepo=\* --enablerepo=dvd tcl

$ tar xvzf redis-4.0.11.tar.gz && cd redis-4.0.11

$ make

$ make test 

$ sudo make install

$ sudo mkdir /etc/redis

$ sudo mkdir /var/redis

$ sudo cp utils/redis_init_script /etc/init.d/redis

$ cd ..


# 2.5.1. Combined Library
$ pip install redis-2.10.6-py2.py3-none-any.whl

$ sudo /etc/init.d/redis start &

$ sudo /etc/init.d/redis stop

$ cd ..


# 2.6. node.js
$ cd Node.js

$ rpm -ivh nodejs-8.12.0-1nodesource.x86_64.rpm

$ node --version

$ cd ..


# 2.7. yarn
$ cd Yarn

$ rpm -ivh yarn-1.10.1-1.noarch.rpm

$ cd ..


# 2.8. Repository 
# 2.8.0. Policy & Personle information
- mysql, Approval system database

CBWMSDB


# 2.8.1. Temporary user information (Scheduled for DB)

/home/DATA/INF/TMP/user.dat


# 2.8.2. user system information from NAC (Scheduled forDB)
/home/DATA/INF/usersystem.inf


# 2.8.3. Project(..ing)
./cbwms/cbwms                        # Starter

./cbwms/cbwms/settings               # Project configration

./cbwms/apps                         # Application root

./cbwms/apps/caengine                # Approval system engine

./cbwms/apps/caengine/bin            # Data transaction, Make Policy & Personal information  

./cbwms/apps/caengine/etc            # Approval system configration

./cbwms/apps/caengine/script         # Approval system tools

./cbwms/apps/locale                  # Globalization

./cbwms/apps/camodels                # Approval system models

./cbwms/apps/camodels/modelsframe    # Policy & Personal information models

./cbwms/apps/camodels/fixtures       # Json output

./cbwms/apps/caui                    # Frontend

./cbwms/help                         # Help


- Library & Deploy

./cbwms/bin

./cbwms/configs

./cbwms/doc

./cbwms/include

./cbwms/lib

./cbwms/lib64

./cbwms/requirements

./cbwms/static

./cbwms/run

# 3. Deploy ( Needs user.dat and usersystem.inf)
# 3.1. Create DB
$ vi cbwms/settings/development.py

DATABASES = {

                ...
                
                'NAME': 'dbname',
                
                'USER': 'username',
                
                'PASSWORD': 'password',
                
                ...
                
}

$ mysql
> CREATE DATABASE dbname CHARACTER SET utf8 COLLATE utf8_unicode_ci;

> CREATE USER 'username'@'localhost' IDENTIFIED BY 'password';

> GRANT ALL PRIVILEGES ON dbname.* TO 'username'@'localhost' WITH GRANT OPTION; 

> CREATE USER 'username'@'%' IDENTIFIED BY 'password';

> GRANT ALL PRIVILEGES ON dbname.* TO 'username'@'%' WITH GRANT OPTION; 

> FLUSH PRIVILEGES;

# 3.2. Migrate
$ rm apps/camodels/migrations/*.py

$ python manage.py makemigrations camodels

$ python manage.py sqlmigrate camodels 0001

$ python manage.py migrate


# 3.3. Scheduler
$ sudo /etc/init.d/redis start

$ vi cbwms/settings/celery.py

$ vi apps/caengine/tasks.py

$ vi apps/caengine/bin/caengineimport.py (line 90)
    subprocess.call([self.cfg.daemonPath + '/fcp2/bin/fcp2passwd', '-I', self.pwfile, '-p', ‘ServerIP:7776＇, userid]

$ su corebrdg

$ celery -A apps.caengine.tasks worker --beat --scheduler django --loglevel=info

# 3.4. Run & Route
$ cd /home/Dev/cbwms

# 3.4.1. Run server
$ python ./manage.py runserver ServerIP:8000

# 3.4.2. URL Configration
$ vi cbwms/urls.py

http://서버IP:8000/camodels on Webbrowser 

$ vi apps/camodels/urls.py

http://서버IP:8000/camodels/url_route

# 4.0. Django with Recat
# 4.0.0. Settings
$ cd /home/Dev
# 환경 초기화
$ npm init –y

# Webpack 설치
$ npm i webpack webpack-cli –save-dev
    
$ vi package.json
# 추가
"scripts": {

    "dev": "webpack –mode development ./cbwms/apps/frontend/src/index.js –output ./cbwms/apps/frontend/static/frontend/main.js",
    "build": "webpack –mode production ./cbwms/apps/frontend/src/index.js –output ./cbwms/apps/frontend/static/frontend/main.js"

},

# Babel 설치
$ npm i @babel/core babel-loader @babel/preset-env @babel/preset-react babel-plugin-transform-class-properties --save-dev

# React 와 prop-Type 배치
$ npm i react react-dom prop-types --save-dev

# Babel 설정
$ vi ./cdwms/.babelrc
{

    "presets": [
        "@babel/preset-env", "@babel/preset-react"
    ],
    "plugins": [
       "transform-class-properties"
    ]
    
}  

# Babel-loader 설정
vi webpack.config.js
module.exports = {

    module: {
      rules: [
        {
          test: /\.js$/,
          exclude: /node_modules/,
          use: {
            loader: "babel-loader"
          }
        }
      ]
    }
    
};

# View 생성
$ cd cbwms

$ vi ./apps/frontend/views.py

# Template 생성
$ vi ./frontend/templates/frontend/index.html

# Project URL 추가
$ vi ./cbwms/urls.py

# 설정 추가
vi ./cbwms/settings/common.py
DEFAULT_APPS = [

    ...
    'apps.caui',
    ...

]

# App main component
$ vi ./apps/frontend/src/components/App.js

# Data Provider
$ vi ./apps/frontend/src/components/DataProvider.js

# Table Component
$ vi ./apps/frontend/src/components/Table.js

# A better alternative to shortid for React is weak-key
$ npm i weak-key --save-dev

# Create entry point
$ vi ./apps/frontend/src/index.js

# Run webpack 
$ npm run dev

# run server
$ python manage.py runserver 10.211.55.78:8000

# Browsing
http://10.211.55.78:8000

