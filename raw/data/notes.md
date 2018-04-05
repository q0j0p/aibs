### Install mongodb (community edition) on ubuntu

Import the public key used by the package management system.
```
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5
```
Create a list file for MongoDB.
```
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.6 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list
```
Reload local package database.
```
sudo apt-get update
```
Install the latest stable version of MongoDB.
```
sudo apt-get install -y mongodb-org
```

Issue the following command to start mongod:
```
sudo service mongod start
```

#### Data download using selenium phantom.js

- install phantomjs
```
sudo wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-1.9.7-linux-x86_64.tar.bz2
sudo tar xjf phantomjs-1.9.7-linux-x86_64.tar.bz2
# Create links
sudo ln -s /usr/local/share/phantomjs-1.9.7-linux-x86_64/bin/phantomjs /usr/local/share/phantomjs
sudo ln -s /usr/local/share/phantomjs-1.9.7-linux-x86_64/bin/phantomjs /usr/local/bin/phantomjs
sudo ln -s /usr/local/share/phantomjs-1.9.7-linux-x86_64/bin/phantomjs /usr/bin/phantomjs
# Fix for error ( cannot open shared object file: No such file or directory):
sudo apt-get install libfontconfig
conda install selenium
```
