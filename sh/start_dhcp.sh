#/bin/bash

sudo ip addr add 192.168.11.0/24 dev eth0
sudo systemctl start isc-dhcp-server.service
sudo systemctl enable isc-dhcp-server.service
