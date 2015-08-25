# sids
Python Utility to detect Sudden Infant Death Syndrome

#Installation 

ln -s /path/to/git/folder/sids.py /bin/sids

ln -s /path/to/git/folder/sids-config.py /bin/sids-config

##Inittab
echo "ids:2345:respawn:/usr/bin/sids" >> /etc/inittab

##Systemd
echo "[Unit]
Description=Sudden Infant Death Monitor
 
[Service]
ExecStart=/bin/sids
Restart=always
 
[Install]
WantedBy=multi-user.target
" > /etc/systemd/system/sids.service

systemctl start sids.service

systemctl enable sids.service

