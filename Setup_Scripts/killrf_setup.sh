sudo rm -f /etc/modprobe.d/raspi-blacklist.conf
sudo rm -f /nfs/client/etc/modprobe.d/raspi-blacklist.conf

sudo cat >> /etc/modprobe.d/raspi-blacklist.conf <<'endmsg'

#Disable the RF comms by not loading the kernel modules
#wifi
blacklist brcmfmac
blacklist brcmutil
#bt
blacklist btbcm
blacklist hci_uart

endmsg

sudo cp /etc/modprobe.d/raspi-blacklist.conf /nfs/client/etc/modprobe.d/raspi-conf

echo Finished killing RF comms, reboot may be required.
