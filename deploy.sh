useradd -M aquario
chmod 750 -R ./

sudo apt update
sudo apt install python3 -y

git clone https://github.com/bgnacinski/aquario

pip install -r watering-controller/requirements.txt
sudo cp aquario.service /etc/systemd/system/