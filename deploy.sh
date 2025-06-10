useradd -M aquario
usermod -aG gpio aquario
usermod -aG kmem aquario

chown aquario:aquario -R .
chmod 760 -R ./*
chmod 750 .

sudo apt update
sudo apt install python3 -y

pip install -r watering-controller/requirements.txt
sudo cp aquario.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable aquario