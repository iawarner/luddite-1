#Installing Cython 

sudo pip install cython
sudo pip install numpy

#Installing parasail

git clone git@github.com:jeffdaily/parasail.git
./configure
make 
make install
/usr/bin/python setup.py install --prefix=/usr/local




