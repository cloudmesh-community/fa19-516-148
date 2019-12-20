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
