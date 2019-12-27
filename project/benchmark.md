# Benchmark

The following tests were used to benchmark the Pis in these setups:

### Tests

* Small-N performance
    * Requests per second for calculating 5!
    * Latency (minus network RTT)
    * Overhead (latency minus RTT minus server-reported computation time)

* Big-N performance:
    * Time required for calculating 100,000!
    * Latency (minus network RTT)
    * Overhead (latency minus RTT minus server-reported computation time)

### Test configurations

* 'Bare metal':
    * Python on Raspbian on one Pi; no additional software or configuration

* Single-Pi cluster:
    * Two-Pi Kubernetes cluster with one master node and one worker node

* 4-Pi cluster:
    * 5-Pi Kubernetes cluster with one master node and four worker nodes
