from subprocess import Popen, PIPE, STDOUT
cmd = './gravi_utils balance /dev/serial/by-id/usb-FTDI_USB-RS232_Cable_FTWLDHTE-if00-port0'
p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
output = p.stdout.read()
print (output.decode())
