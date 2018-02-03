apt update
apt upgrade
apt -y install python-pip
apt -y install python3-pip
apt -y install ipython ipython-notebook
apt -y  install pylint3
apt -y install git
wget -O /usr/local/bin/rsub https://raw.github.com/aurora/rmate/master/rmate
chmod a+x /usr/local/bin/rsub
python3 -m pip install --upgrade pip
wget http://somecomputer.xyz/files/tensorflow-1.3.0rc0-cp35-cp35m-linux_x86_64.whl
python3 -m pip install tensorflow-1.3.0rc0-cp35-cp35m-linux_x86_64.whl
rm tensorflow-1.3.0rc0-cp35-cp35m-linux_x86_64.*
python3 -m pip install -r requirements.txt

