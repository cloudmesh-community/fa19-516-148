# Federated Kubernetes Clusters With Raspberry Pi

<!-- comment configures vim to enable word wrapping; gggqG to force rewrap -->
<!-- vim: set tw=79 fo+=t fo-=l: -->

After burning the pis we need to set up the pis. We developed a convenient set of deployment scripts that makes this possible


```
$ cms pi setup host[01-10]
$ cms pi kubernetes deploy host[01-10]
```

To configure the master and worker nodes we use the command (we assume host01 is the master):

```bash
$ cms pi kubernetes setup --master=host01 --worker=host[02-10]
```

If the two parameters --master and --worker are ommitted it is assumed that the first node is the worker node.

The services are integrated into an inventory file that can be inspected with the command

```bash
$ cms inventory
```

## Details

### cms pi setup 

After burning each Pi, we need use the `raspi-config` command to set the keyboard
layout and locale. 

:o2: improve and do this via commandline Gregor will than integrate in cms script

In addition we need to set up WiFi if necessary. 

:o2: This however can also be integrated into the burn or a cms command can be developed that sets this after the burn

It is very important to set the time on each pi.


```bash
$ sudo timedatectl set-ntp false
$ sudo timedatectl set-timezone America/Indiana/Indianapolis
$ sudo timedatectl set-time "2019-12-18 14:20:52"
```

(you can get a list of timezones with `timedatectl list-timezones`)

:o2: can this be automated, e.g. after the burn have a program that checksa . status value or the existance of a file and if its not there run some commands to automatically configure?


### cms pi deploy kubernetes 

For our install we will use docker as the container runtime environment.
To install  Kubernetes, we must first 
add the Kubernetes repository to the package manager.
Additionally, Kubernetes requires swap to be disabled. The following script 
does the instalation 

```bash
$ # install Docker
$ curl -sSl https://get.docker.com | sh

$ # install Kubernetes
$ echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
$ sudo apt-get update
$ sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 6A030B21BA07F4FB
$ sudo apt-get -y dist-upgrade
$ sudo apt-get -y install kubelet kubeadm kubectl

$ # disable swap, RPi-specific (https://raspberrypi.stackexchange.com/a/100606)
$ sudo dphys-swapfile swapoff
$ sudo dphys-swapfile uninstall
$ sudo update-rc.d dphys-swapfile remove
$ sudo apt -y purge dphys-swapfile
```

Initialize the master node:

```bash
$ sudo kubeadm init
$ mkdir -p /home/pi/.kube
$ sudo cp -i /etc/kubernetes/admin.conf /home/pi/.kube/config
$ sudo chown 1000:1000 /home/pi/.kube/config
```

And have worker nodes (other Pis) join the cluster:

```bash
$ kubeadm join [MASTER-IP:6443] --token [TOKEN] --discovery-token-ca-cert-hash [HASH]
```

These steps can be done on all Pis at once using SSH in a loop.
[multi-pi-setup-steps.txt](multi-pi-setup-steps.txt) contains a list of the
exact commands to be executed. This should be replaced with a cms command that
integrates with cloudmesh-inventory. It should read a list of Pis and IPs in a
cluster from the inventory YAML file, and then run the commands using
os.system(). This seems fairly simple. However, there is one step that needs to
be done manually on every Pi. It is part of the Docker install script at
<https://get.docker.com> and errors out if run remotely via a SSH command
command (e.g. `ssh pi7 'curl https://get.docker.com | sh'`); instead we must
`ssh pi7` to get a shell and then run the `curl|sh` command.


## Pytests

A number of pytests exists that check if the cluster is properly fucntioning

* ... list tests here and describeb what they do

## Example

We run the following example on teh cluster to demonstarte its use

... describe

## Benchmark

We observe the following benchmark results

... describe what the results are

## Network issues 

:o2: remove I and make general

:o2: split up into two sections general network issues that apply regardless of iu or not and specific iu issues

I have run into one critical issue regarding network connections; the master node is setup and ready to accept connections, and the worker nodes are prepared but will not join the cluster when I run the join command. The Pis have two network connections, one is local on the switch (connecting all the Pis and my computer, but no internet) and the other is their regular internet connection through IU WiFi. I've tried running the cluster in all three connnection configurations: ethernet/switch only, WiFi only, and with both active at the same time. What I've gathered over many hours of debugging is that:

 

*  k8s will not run without an internet connection available on the machine (I tried ethernet-only and it failed, workers still tried to connect to the master via its public internet-accessible IP, it also failed with WiFi completely disabled - this GitHub issue suggests that using k8s without an internet connection is completely unsupported: https://github.com/kubernetes/kubeadm/issues/982)

:o2: are you living in private residence whre you could use controlable wifi by you?

*  IU WiFi implements client isolation so that clients on the same network cannot talk to each other. Thus, the Pis cannot communicate over WiFi. And from the previous bullet point, they cannot communicate over ethernet only since there is no internet available on that interface, which is incompatible with k8s.

* IU network dows not allow network forwarding i believe, e.g making one node the master. 

The IU WiFi networks have some form of AP isolation enabled - (https://kb.iu.edu/d/bdjb#incompatible - that article is specifically about IU DeviceNet but I have observed the same behaviour on IU Secure). I have experienced personally also being unable to connect to other devices on the IU WiFi network, even when trying to connect directly to their IP address (not multicast/broadcast or mDNS). And it seems the same thing is going on with the Pis on IU DeviceNet. When I am SSH'd into pi1, I can use the private ethernet swtich IPs to SSH into pi2 (from pi1), and I can use nmap to port scan another pi. But when I use the WiFi public IPs, I cannot SSH from one pi into another, and nmap reports that its scan attempts are being dropped.

 

There is one loophole that may exist: from my computer, connected to IU Secure, I can use WiFi to SSH into the Pis, which are connected to IU DeviceNet. So *perhaps* the isolation is only enabled within each WiFi network.

 

There are four IU WiFi networks, IU Secure, eduroam, IU DeviceNet, and IU Guest. The Pis can only connect to the last two. So I suspect it might be fixable by having the master Pi connected to IU Guest and the rest of the Pis connected (as currently) to IU DeviceNet. Then perhaps the network will allow them to communicate.

 

The issue is that right now I am using raspbian lite on the Pis. IU DeviceNet uses MAC address enrollment which is OK, but IU Guest requires login through a web browser. I tried two CLI web browsers lynx and links to try to login to IU Guest but they failed (probably because the login requires JavaScript). So today I will try installing full 'normal' GUI raspbian on the master, reinstalling kubernetes and making a master node on it, and connecting it to IU Guest.

 

I have a final today from 12:30 to 2:30 and another final project due tonight. So I don't know whether I will have enough time to run benchmarks today. But I will be able to attempt the network stuff and hopefully it will not be blocked.
