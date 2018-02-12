# aibs

- EDA of cell type data
- Characterize cell type morphology
- Simulate the development of different cell types using random walk growth


### Data sources
- [Allen Institute cell types api](http://alleninstitute.github.io/AllenSDK/cell_types.html)
- [neuromorpho.org](http://neuromorpho.org/byspecies.jsp)

#### Data download using phantom.js

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
```
