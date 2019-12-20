# Federated Kubernetes Clusters With Raspberry Pi
<!-- comment configures vim to enable word wrapping; gggqG to force rewrap -->
<!-- vim: set tw=79 fo+=t fo-=l: -->

Sub and Gregor von Laszewski, [fa19-516-148](https://github.com/cloudmesh-community/fa19-516-148)

laszewski@gmail.com

[Insights](https://github.com/cloudmesh-community/fa19-516-148/graphs/contributors)

:o2: please report on progress on the kubernetes cluster

:o2: unfortunately the first line in the document must be a heading

do you have a command such as 

cms kubernetes deploy ... ?


## Abstract

## Introduction

## Related Work

## Architecture

We leverage or improve <https://github.com/cloudmesh/cm-burn>

Our goal is to craete and contrast the creation of Federated kubernetes
clusters. We have different models

1. The clusters are owned by a single user
2. The clusters are owned by multiple users

Goal is to create a federation of them. In each case the fedaration can
be achieved in one of two ways.

1. consider a big kubernetis cluster that integrates all resources
2. consider a cluster of kubernetes clusters

This requires some investigation into kubernetes

Some images are shown in cm-burn that we may want tocopy here.

## Technologies used

* cloudmesh cm-burn
* cloudmesh-inventory
* Kubernetes
* Docker

## Benchmark and Evaluation

## Conclusion

## Other documentation files

* [`sdcard-setup.md`](sdcard-setup.md) contains documentation on cm-pi-burn and
  how the Pi images are modified/initialized. Also refer to the `cm-pi-burn.md`
  file in the `cm-burn` repo.

* [`pi-setup.md`](pi-setup.md) contains documentation on post-burn configuration
  that must be done after a Pi is booted up for the first time.

* [`docker.md`](docker.md) contains documentation on creating the Docker image
  used for testing.
