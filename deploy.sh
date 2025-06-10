cd /opt
rm -r aquario

useradd -M aquario

sudo apt update
sudo apt install python3 -y

git clone https://github.com/bgnacinski/aquario

chmod 750 -R aquario
cd aquario

pip install -r requirements.txt
sudo cp aquario.service /etc/systemd/system/