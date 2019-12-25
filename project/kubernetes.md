# Using the Kubernetes Cluster

Follow the [Docker image creation guide](docker.md) to create a test image for
ARM. Upload it to Docker Hub or another image repository (if you do not use
Docker Hub, you will need to fully qualify the image name when adding it to
Kubernetes, such as by providing `gcr.io/username/imagename:v7` instead of
`username/imagename:v7`).

SSH to the master node and run these commands (for the factorial test example):

```bash
  #           DEPLOYMENT_NAME   IMAGE_NAME                             PORT
$ kubectl run factorial         --image subraizada3/factorial-arm:v2   --port=80

$ kubectl get pods --output=wide
  # should list one pod running factorial
  # if state is ContainerCreating, Kubernetes is downloading the container image

$ kubectl scale deployment factorial --replicas=4
  # specify that 4 instances of this should run (since we have 4 worker nodes)

$ kubectl get deployment factorial
  # verify that 4 instances have started up
$ kubectl get pods --output=wide
  # should list 4 pods, along with the hosts they are running on and their IPs
```

At this point you should be able to interact with the service.
`kubectl get pods --output=wide` will list the cluster-private IPs of the Pods.

`curl {IP}` should give a success message, and `curl -X POST -d 5 {IP}` should
give you 120 and the compute time. This will always run on the same host since
you are specifying a pod-specific IP.
These will only work within the cluster since the IP addresses are private to
the cluster overlay network.

---

The final step is to expose the deployment outside the cluster via a
load-balancing service:

```bash
$ kubectl expose deployment factorial --external-ip=MASTER_IP --port=80 --target-port=80
```

`MASTER_IP` should be the 'normal' IPv4 address of the master node. From the
master itself or from any other computer with a network connection to the
master, you should now be able to `curl {MASTER_IP}` to get a success message.
If you do this repeatedly you will notice the responses come from different
nodes.

The factorial example ran on port 80. If your container image listens on
another port (such as 3000) and you want to expose the service publically on
port 4000, you should use this command right now:

```bash
$ kubectl expose deployment factorial --external-ip=MASTER_IP --port=4000 --target-port=3000
```

And the port in the very first `kubectl run` step should also be 3000.

---

At this point the cluster is fully setup and is running a container image. To
the changes from this document, you can do:

```bash
$ kubectl delete deployment factorial   # also deletes the pods for this deployment
$ kubectl delete service factorial
```
