#Installing Cython 
#Installing parasail

git clone git@github.com:jeffdaily/parasail.git

sudo ./configure
sudo make 
sudo make install
PARASAIL_PREFIX=/usr/local/lib/ python setup.py build
cp build/lib*/parasail.so 



