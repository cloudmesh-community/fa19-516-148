# Burning SD Cards

# Using cm-pi-burn

TODO Check that this is up-to-date with cm-pi-burn documentation. Has the
command API changed?

In a root shell:

```
# cm-pi-burn.py image get latest
# cm-pi-burn.py image ls
# cm-pi-burn.py create --image=2019-09-26-raspbian-buster-lite
                       --device=/dev/mmcblk0
                       --hostname=red[2-6] --ipaddr=192.168.1.[2-6]
                       --sshkey=id_ed25519
```

That's it.

---

# Alternative Approach Theory

The official Raspberry Pi lite image is a .img file of a disk with two
partitions - a FAT32 boot partition and a primary partition. You can view this
with fdisk: `fdisk -l 2019-09-26-raspbian-buster-lite.img`. This image can be
modified and repacked by burning it to an SD card (which will unpack the .img
onto a real disk with usable and editable partitions), modifying the files on
the SD card, and then rereading the data on the SD card to a file:

```
$ cat 2019-09-26-raspbian-buster-lite.img >/dev/mmcblk0
  # now the SD card /dev/mmcblk0 has two partitions which you can
  # mount and edit
$ mount /dev/mmcblk0p1 /your/mount/point
  # modify the files on the FS
$ umount /dev/mmcblk0p1
$ cat /dev/mmcblk0 >your-custom-sd-card-image.img
```

Now your custom SD card image can be burned to new SD cards to give them the
same configuration.

Burning the large 2 GB images to the SD cards takes a while, and requires a
human to be monitoring the process to swap completed SD cards with new ones
that are waiting to be burned. It would be easier to flash the exact same image
to 100 SD cards than to make 100 images and flash each image onto one SD card,
because in the second case either the human has to remember state (which number
am I on?) over a lengthy timespan (which is error-prone), or a machine has to
keep track of that state - which would not work because the human can make
errors that interrupt or mess up the flash process, so the program would need a
way to correct those errors, making the entire process complicated. On the
other hand, burning the same image 100 times just requires the human to plug
and unplug the cards with no added complexity.

The following things need to be configured on each RasPi:

* hostname
* network connection: IP and DNS
* add SSH keys and disable default Pi login
* installing Kubernetes

Since the goal is to have each new Pi use the exact same system image on boot,
a cluster controller will need to detect new Pis that connect to the network
and set them up. The process would be like this:

* New Pi flashed and powered and connected via Ethernet. Its SD card is configured with some static IP (e.g. 1.2.3.4), and with SSH configured and password login disabled.
* A cluster controller is polling to see if a Pi exists at the IP 1.2.3.4. As soon as it detects a new Pi there, it performs the following steps (which should take only a few seconds):
	* SSH into the Pi with the default username and the hardcoded initial (but not default) password.
	* Give it a hostname and assign it an IP.
	* Optionally, add more SSH keys
* The cluster controller will remember that Pi XXX was given hostname HHH and IP I.J.K.L, and it will instruct this Pi to reboot.
* At this point the 1.2.3.4 IP is free for another Pi to join the cluster.
* After giving enough time for Pi XXX to have rebooted, the cluster controller will SSH to it on its IP and perform any tasks that take time - such as installing Kubernetes.

The cluster controller will need a user interface to let the human specify
which Pi should be given which hostname. The blocking portion of Pi setup
(where it is on the 1.2.3.4 IP) should only take a few seconds per Pi, so a
human can configure 100 Pis within a few minutes. Another benefit is that since
a machine is in charge of cluster structure, this setup can be extended to
allow for the structure to be reorganized at runtime - for example, by adding a
script that will SSH to a Pi and change its hostname and IP. This introduces a
single point of failure for adding new Pis to the cluster or reconfiguring the
cluster, but existing cluster nodes will continue to operate if the cluter
controller fails.

# Implementation

## Creating the SD card image

The following things must be configured on the master disk image: network
connection (IP and DNS) and login (SSH).

Burn the image onto a SD card: `cat image.img >/dev/mmcblk0`

Mount the second (primary) partition:

```
$ mkdir mount
$ mount /dev/mmcblk0p1 mount # primary partition
$ mount /dev/mmcblk0p0 mount/boot # boot partition
```

Authorize your SSH key, for both the `pi` user and for `root`:

```
mkdir mount/home/pi/.ssh
mkdir mount/root/.ssh
cp ~/.ssh/id.pub mount/home/pi/.ssh/authorized_keys
cp ~/.ssh/id.pub mount/root/.ssh/authorized_keys
```

Disable SSH password login: in `etc/ssh/sshd_config`, uncomment the
`PasswordAuthentication` line and change `yes` to `no`

Configure static IP and DNS: append the following to `mount/etc/dhcpcd.conf`:

```
interface eth0
static ip_address=192.168.0.3/24
static routers=192.168.0.1
static domain_name_servers=10.79.1.1
```

`10.79.1.1` is the preferred DNS resolver address that IU's DHCP provides to my
personal computer when I connect to eduroam. This setting doesn't matter on the
Pi if it doesn't connect to the Internet. Alternatively, there are other DNS
providers available like 1.1.1.1 (Cloudflare) or 8.8.8.8 (Google).

And append to the kernel parameters commandline at `mount/boot/cmdline.txt`:
`net.ifnames=0`

The Linux command line parameter will cause it to use old-style `eth0` names
for network interfaces instead of the newer naming style which will assign a
name dependent on the Pi's MAC address - and that is incompatible with having a
single image for all the Pis.

Copy the Pi configuration script from this repository to the home folder of the
Pi's root user, so that it can be executed when the Pi is being configured:
`cp configure.py mount/root/`

Unmount both partitions (boot first, since it is mounted inside the primary
partition on the host computer):

```
$ umount mount/boot # or /dev/mmcblk0p0
$ umount mount # or /dev/mmcblk0p1
```

Clone the SD card onto a new image file: `cat /dev/mmcblk0 >image.img`

Now, new SD cards can be flashed with this image: `cat image.img >/dev/mmcblk0`

## Post-boot configuration

Upon boot, the Pi will connect to the network at its specified IP. At this
point, it should be logged into via SSH and the following Pi-specific
configuration needs to be done:

Set the hostname: change the hostname in `/etc/hostname` from `raspberrypi` to
the desired hostname, and do the same on the last line of `/etc/hosts`.

Set the IP address to the Pi's desired permanent IP address by changing the
static address line added to the bottom of `/etc/dhcpcd.conf` when creating the
master image.

These steps can be automated with the `configure.py` script copied to the
master disk image. The script takes in three arguments: the cluster group name
(e.g. red, blue, green), the cluster number (e.g. red = cluster 1, blue =
cluster 2, green = cluster 3), and the Pi number (within that cluster). The
`configure.py` script will set the hostname to `cluster_name + pi_number`: Pi#47
in the blue cluster will be given the hostname `blue`. It will also set the IP
to `192.168.cluster_number.pi_number`, so if blue is cluster #2, the Pi will be
given the IP `192.168.2.47`.

Since the configure script edits system files, it must be run as root. The
benefits of the single master image starts to come into play here: with one
command, a Pi can be configured or *reconfigured* to be part of any cluster.
New Pis will join the network at 192.168.0.3. To configure them, this command
can be used from the cluster controller Pi:
`ssh root@192.168.0.2 /root/configure.py blue 2 47` - and the Pi will be
configured as described above. If Pi 37 from the red group needs to be changed
to Pi 20 in the green group, just run this command from the cluster controller:
`ssh root@192.168.1.37 /root/configure.py green 3 20`.

The configure script will restart the Pi so that the hostname/IP change can be
applied.

Now, the Pi is ready to have Kubernetes installed. (TODO: run apt update on
first boot - this can also be put into the master image)
