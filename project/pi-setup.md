# Federated Kubernetes Clusters With Raspberry Pi - Pi Setup / Configuration
<!-- comment configures vim to enable word wrapping; gggqG to force rewrap -->
<!-- vim: set tw=79 fo+=t fo-=l: -->

After burning, on each Pi use the `raspi-config` command to set the keyboard
layout and locale, and to setup WiFi if necessary.
Also, set the time on each pi:

```bash
$ sudo timedatectl set-ntp false
$ sudo timedatectl set-timezone America/Indiana/Indianapolis
$ sudo timedatectl set-time "2019-12-18 14:20:52"
```

(you can get a list of timezones with `timedatectl list-timezones`)

Add the Kubernetes repository to the package manager and install Kubernetes.
First, Docker needs to be installed as the container runtime.
Additionally, Kubernetes requires swap to be disabled.

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
