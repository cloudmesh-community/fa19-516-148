# Benchmark

The following tests were used to benchmark the Pis in these setups:

### Tests

* Small-N performance
    * Requests per second for calculating 5!
    * Latency and overhead

* Big-N performance:
    * Time required for calculating 100,000!
    * Overhead

The factorial compute server reports along with its calculation reponse the
real-world time it spent doing the calculation (response created time - request
received time). Meanwhile, the computer sending requests can also measure its
latency (response received time - request sent time).

benchmarker observed latency = computation time + network RTT + OS overhead +
Python HTTP stdlib overhead + clustering software overhead

The computation time is reported by the server, and network RTT can be measured.
In the 'Bare metal' test configuration, subtracting the computation time and RTT
from benchmarker observed latency will leave just latency caused OS+Python.

In the single/4 Pi cluster case, subtracting compute time and RTT will leave
just latency caused by OS+Python+Kubernetes+Docker. Thus, we can see how much of
a latency increase is caused by Kubernetes+Docker.

### Test configurations

* 'Bare metal':
    * Python on Raspbian on one Pi; no additional software or configuration

* Single-Pi cluster:
    * Two-Pi Kubernetes cluster with one master node and one worker node

* 4-Pi cluster:
    * 5-Pi Kubernetes cluster with one master node and four worker nodes
