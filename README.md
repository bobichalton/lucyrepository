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
git clone https://github.com/bobichalton/lucyrepository/
sudo rm -rf /usr/share/snips/assistant
sudo mv Lucy/lucy.service /etc/systemd/system

ENGLISH
 * sudo mv lucy/assistants/assistant_en /usr/share/snips/assistant
 * cd Lucy
 * sudo nano settings.py => change LANG = 'en'

sudo systemctl restart "snips-*"
sudo systemctl start lucy
sudo systemctl enable lucy
```


![cmdsen](https://console.snips.ai/images/bundles/bundle-folder.svg)
