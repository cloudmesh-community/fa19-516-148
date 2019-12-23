# Federated Kubernetes Clusters With Raspberry Pi

<!-- comment configures vim to enable word wrapping; gggqG to force rewrap -->
<!-- vim: set tw=79 fo+=t fo-=l: -->

After burning the Pis we need to set up the Pis. We developed a convenient set
of deployment scripts that makes this possible. First, you must use
cloudmesh-inventory to add your Pis to the inventory.

```bash
$ cms inventory add pi[1-5] --cluster CLUSTER_NAME --service pi_kubernetes --label worker
$ cms inventory set pi1 label to master   # change label for one pi from worker to master
$ cms inventory set pi[1-5] ip to 192.168.1.[21-25]
  # (or if IPs are not contiguous, set one Pi/IP pair at a time)
```

Next, cloudmesh-pi provides an automated setup process split into a few steps.
Step 1 is to connect the Pis to the internet and set their timezone.
If their ethernet connections have internet access, you can skip the WiFi step.
To connect to WiFi, SSH to every Pi and run the 'raspi-config' program under
sudo. This command will launch a shell on every host via SSH, and you can
manually run rapsi-setup on each Pi to connect to WiFi.

```bash
$ cms pi ssh pi[1-5]
```

TODO Investigate automatically setting WiFi on each Pi, given the SSID+password
once. See `do_wifi_ssid_passphrase`, line 1655:
<https://github.com/RPi-Distro/raspi-config/blob/master/raspi-config#L1655>

Once connected, this configures their timezones:

```bash
$ cms pi setup1 pi[1-5]
```

The next step is to install Docker on each Pi. This unfortunately must be done
manually on each Pi; the installation script provided by Docker fails to run
successfully if it is automatically run via SSH. Use cloudmesh-pi to SSH to
each pi:

```bash
$ cms pi ssh pi[1-5]
```

Once logged in to the first Pi, paste this command:

```bash
$ curl -sSl https://get.docker.com | sh ; tput bel; exit
```

That will install docker, then ring the terminal bell and close the SSH session
(`exit`). cms pi ssh will automatically SSH to the next Pi, so you can just
paste the same command in repeatedly until every Pi has Docker installed.

The remaining setup steps are automated:

```bash
$ cms pi setup2 pi[1-5]
```

This step can take a long time. The terminal bell will be rung when
cloudmesh-pi is finished.

The final two steps are to configure the master node and make workers join the
cluster.

```bash
$ cms pi setupmaster pi1
```
This step can take a long time. The terminal bell will be rung when
cloudmesh-pi is finished.

When `setupmaster` completes, the last line of its output will contain a 'join
command' which can be run on the workers to join the cluster. This can be
automatically run on every Pi:

```bash
# Note that pi1 is excluded here since it is the master.
$ "sudo JOIN_COMMAND" | cms pi cmd pi[2-5]
# Full example:
$ echo "sudo kubeadm join 192.168.1.122:6443 --token knlc4l.2pfdig67hb2cv16b --discovery-token-ca-cert-hash sha256:c9d558a1d63ddc27d5278c5ad3582d9697eb25b33c1c5643a10bec5b066969d4" | cms pi cmd pi[3-5]
```

`cms pi cmd` take the command from stdin instead of as an argument
(`cms pi cmd pi[2-5] "sudo kubectl join ..."`) because the cloudmesh shell
parser appears to ignore the quotation marks around "sudo kubectl join" and
thus the command is not parseable as a single argument.

To verify that everything is working correctly, SSH to the master node (`cms pi
ssh pi1`) and run `kubectl get nodes`. Alternatively:

```bash
$ echo "kubectl get nodes" | cms pi cmd pi1
```

The output should be like this:
```
NAME   STATUS     ROLES    AGE    VERSION
pi1    NotReady   master   27m    v1.17.0
pi2    NotReady   <none>   20m    v1.17.0
pi3    NotReady   <none>   101s   v1.17.0
pi4    NotReady   <none>   76s    v1.17.0
pi5    NotReady   <none>   39s    v1.17.0
```

As you can see, the master node has the role 'master' but the worker nodes have
no role. Label them with this command:

```bash
# on master node pi1, label nodes pi[2-5] as workers
$ cms pi label pi1 pi[2-5]
```

Finally, the output of `kubectl get nodes` should look like this:

```
NAME   STATUS     ROLES    AGE    VERSION
pi1    NotReady   master   27m    v1.17.0
pi2    NotReady   worker   20m    v1.17.0
pi3    NotReady   worker   101s   v1.17.0
pi4    NotReady   worker   76s    v1.17.0
pi5    NotReady   worker   39s    v1.17.0
```

## Details

### cms pi setup

After burning each Pi, we need use the `raspi-config` command to set the keyboard
layout and locale.

:o2: improve and do this via commandline Gregor will than integrate in cms script

In addition we need to set up WiFi if necessary. 

:o2: This however can also be integrated into the burn or a cms command can be developed that sets this after the burn

## Pytests

A number of pytests exists that check if the cluster is properly fucntioning

* TODO ... list tests here and describeb what they do
:o2: network more important


## Example

We run the following example on the cluster to demonstrate its use

TODO ... describe


## Benchmark

We observe the following benchmark results

TODO ... describe what the results are
:o2: network more important

## Network issues

### Internet access
Kubernetes requires each node (master and worker) to have an internet
connection. The Pis have two interfaces, Ethernet and WiFi.

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

 
### Network tunneling

is it possible to set up a tunnel between workers and hosts to get access to the network from the master node only, and than the workers use a tunnel to get to the master?


* <https://www.ssh.com/ssh/tunneling/example>

```bash
$ ssh -L 80:intra.example.com:80 gw.example.com
```

* <https://www.digitalocean.com/community/tutorials/how-to-route-web-traffic-securely-without-a-vpn-using-a-socks-tunnel>
