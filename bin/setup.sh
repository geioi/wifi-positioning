#network tools
echo "-----installing necessary network tools-----"
sudo apt install -y net-tools
sudo apt install -y wireless-tools
sudo apt install -y iw

#python dependencies
echo "-----installing necessary python dependencies-----"
sudo apt install -y tshark
sudo apt install -y python3-tk
sudo apt install -y python3-pip 

#pip installs 
echo "-----installing necessary python libraries-----"
pip3 install psutil
pip3 install pyshark
pip3 install mysql-connector-python
