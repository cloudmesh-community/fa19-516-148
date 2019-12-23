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
NAME   STATUS   ROLES    AGE    VERSION
pi1    Ready    master   27m    v1.17.0
pi2    Ready    <none>   20m    v1.17.0
pi3    Ready    <none>   101s   v1.17.0
pi4    Ready    <none>   76s    v1.17.0
pi5    Ready    <none>   39s    v1.17.0
```

As you can see, the master node has the role 'master' but the worker nodes have
no role. Label them with this command:

```bash
# on master node pi1, label nodes pi[2-5] as workers
$ cms pi label pi1 pi[2-5]
```

Finally, the output of `kubectl get nodes` should look like this:

```
NAME   STATUS   ROLES    AGE    VERSION
pi1    Ready    master   27m    v1.17.0
pi2    Ready    worker   20m    v1.17.0
pi3    Ready    worker   101s   v1.17.0
pi4    Ready    worker   76s    v1.17.0
pi5    Ready    worker   39s    v1.17.0
```

## Details

### cms pi setup

After burning each Pi, we need use the `raspi-config` command to set the keyboard
layout and locale.

:o2: improve and do this via commandline Gregor will than integrate in cms script

In addition we need to set up WiFi if necessary. 

:o2: This however can also be integrated into the burn or a cms command can be developed that sets this after the burn

## Pytests

See [`test.py`](test.py). Run it with the the first argument being the name
given to the master node in cloudmesh-inventory (with the examples used earlier
in this documentation, that was `pi1`).

## Example

We run the following example on the cluster to demonstrate its use

TODO ... describe


## Benchmark

We observe the following benchmark results

TODO ... describe what the results are
:o2: network more important

## Network issues

Kubernetes requires each node (master and worker) to have an internet
connection. The Pis have two interfaces, Ethernet and WiFi. If their Ethernet
connection provides an internet connection, then WiFi is not required and can
be ignored. If their WiFi interface provides an internet connection, then
Ethernet is not required and can be ignored. However, the nodes must be able to
communicate with each other *on the interface that provides the internet
connection*. For example, if they are connected to each other via Ethernet and
to the internet via WiFi, but they cannot communicate with each other via WiFi
(in cases where your WiFi provider implements AP isolation), the cluster will
*not* work.

Secondly, it is highly advisable to provide the nodes with a static IP address
(via the DHCP assignment settings on a WiFi router, or through cm-pi-burn for
Ethernet), so that they are not subject to changing DHCP IP addresses. If the
IP address of a node changes, it may be necessary to reconfigure the cluster to
an unknown degree.

### Network tunneling

is it possible to set up a tunnel between workers and hosts to get access to the network from the master node only, and than the workers use a tunnel to get to the master?


* <https://www.ssh.com/ssh/tunneling/example>

```bash
$ ssh -L 80:intra.example.com:80 gw.example.com
```

* <https://www.digitalocean.com/community/tutorials/how-to-route-web-traffic-securely-without-a-vpn-using-a-socks-tunnel>
