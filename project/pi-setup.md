<!-- comment configures vim to enable word wrapping; gggqG to force rewrap -->

<!-- vim: set tw=79 fo+=t fo-=l: -->

# Federated Kubernetes Clusters With Raspberry Pi - Burning SD Cards

After burning, on each Pi use the `raspi-config` command to set the keyboard
layout and locale, and to setup WiFi if necessary.

Add the Kubernetes repository to the package manager and install Kubernetes.
Docker also needs to be installed as the container runtime.

```
$ curl -sSl get.docker.com | sh
# echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" >>/etc/apt/sources.list.d/kubernetes.list
# apt get update
# apt get install -y kubelet kubeadm kubectl
```

Initialize the master node:

```
# kubeadm init
$ mkdir -p $HOME/.kube
$ sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
$ sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

And have worker nodes (other Pis) join the cluster:

```
$ kubeadm join [MASTER-IP:6443] --token [TOKEN] --discovery-token-ca-cert-hash [HASH]
```
