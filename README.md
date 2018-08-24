# Lucy

## Snips - Lucy Assistant workorder (for english, check below)


### Installation

Dependencies
```
sudo pip install spidev
sudo pip install paho-mqtt
```

Installation
```
git clone https://github.com/Psychokiller1888/MyChef.git
sudo rm -rf /usr/share/snips/assistant
sudo mv MyChef/mychef.service /etc/systemd/system

FRENCH
 * sudo mv lucy/assistants/assistant_fr /usr/share/snips/assistant
ENGLISH
 * sudo mv lucy/assistants/assistant_en /usr/share/snips/assistant
 * cd MyChef
 * sudo nano settings.py => change LANG = 'en'

sudo systemctl restart "snips-*"
sudo systemctl start lucy
sudo systemctl enable lucy
```


![cmdfr](https://puu.sh/Amr85.png)

![cmdsen](https://puu.sh/Amr4S.png)
