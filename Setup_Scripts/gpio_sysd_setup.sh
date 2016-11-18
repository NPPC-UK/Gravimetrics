#!/bin/sh

sudo rm -f /nfs/client/user/bin/gpio_init.sh # remove the old script, useful for when pushing updates
sudo rm -f /user/bin/gpio_init.sh # remove the old script, useful for when pushing updates

echo Setting up for master pi! 

sudo cat >> /usr/bin/gpio_init.sh << 'endmsg'
#!/bin/sh

pins="2 3 4 17 27 22 10 9 11 5 6 13 19 25 8 15"

for i in $pins ; do

    echo "Exporting $i"
    echo $i > /sys/class/gpio/export
    echo "setting $i to output"
    echo "out" > /sys/class/gpio/gpio$i/direction
    echo "Setting $i to zero"
    echo "0" > /sys/class/gpio/gpio$i/value
    echo

done

endmsg

echo Setting up for slave pis

sudo cat >> /nfs/client/usr/bin/gpio_init.sh << 'endmsg'

#!/bin/sh

pins="26 19 13 6 21 20 16 12 14 15 18 23 4 2 3 17"

for i in $pins ; do

    echo "Exporting $i"
    echo $i > /sys/class/gpio/export
    echo "setting $i to output"
    echo "out" > /sys/class/gpio/gpio$i/direction
    echo "Setting $i to zero"
    echo "0" > /sys/class/gpio/gpio$i/value
    echo

done

endmsg

sudo chmod +x /nfs/client/usr/bin/gpio_init.sh


sudo rm -f /etc/systemd/system/gpio_enable.service # remove the old script, useful for when pushing updates
sudo rm -f /nfs/client/etc/systemd/system/gpio_enable.service # remove the old script from the nfs partition, useful for when pushing updates

sudo cat >> /etc/systemd/system/gpio_enable.service <<'endmsg'
[Unit]
Description=Enables the GPIO pins for each Pi

[Service]
Type=oneshot
ExecStart=/usr/bin/gpio_init.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
endmsg

sudo cp /etc/systemd/system/gpio_enable.service /nfs/client/etc/systemd/system/gpio_enable.service

echo Finished installing systemd service for GPIO
