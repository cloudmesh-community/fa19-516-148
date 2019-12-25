# Benchmark

The following tests were used to benchmark the Pis in these setups:

### Tests

* Small-N performance
    * Requests per second for calculating 5!
    * Latency: time from request sent => response recieved, minus RTT to load
      balancer
    * Overhead: The server reports the real-world time used between receiving
      the HTTP request and sending the response; how much smaller is this than
      the latency timed by the request sender? After subtracting network RTT,
      this will show the latency increase caused by the clustering software.

* Big-N performance:
    * Time required for calculating 100,000!
    * Overhead (same as in small-N test)

### Test configurations

* 'Bare metal':
    * Python on Raspbian on one Pi; no additional software or configuration

* Single-Pi cluster:
    * Two-Pi Kubernetes cluster with one master node and one worker node

* 4-Pi cluster:
    * 5-Pi Kubernetes cluster with one master node and four worker nodes
