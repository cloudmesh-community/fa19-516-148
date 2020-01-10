# Benchmark

The following tests were used to benchmark the Pis in these setups:

### Tests

Tests:

* Small-N: 2,000 requests for 5!
* Medium-N: 300 requests for 30,000!
* Large-N: One request for 100,000!

Each test measures:

* Requests per second (except for large-N)
* Latency (request->response time minus network RTT minus benchmarker overhead)
* Overhead (latency minus server-reported computation time)

### Test configurations

* 'Bare metal':
    * Python on Raspbian on one Pi; no additional software or configuration

* Single-Pi cluster:
    * Two-Pi Kubernetes cluster with one master node and one worker node

* 4-Pi cluster:
    * 5-Pi Kubernetes cluster with one master node and four worker nodes

# Test on laptop & notes on latency

I ran the factorial server in Docker on my laptop (Intel Kaby Lake i7-7700HQ
4/8x 3.5 GHz, with all security mitigations applied as of Linux 5.4.6) and
observed these results for the medium benchmark:

```
Starting benchmark of 300 factorial calls, n=30000
Total benchmark time: 66.7872 => 4.491881956272075 requests/second
avg/stdev values (in seconds):
  LATENCY       0.7470 0.0699
  SRVR COMPUTE  0.0205 0.0042
  OVERHEAD      0.7265 0.0689
```

Meanwhile, `time curl -s -X POST -d 30000 localhost` gives 0.263 seconds as the
real time.

Thus, we can see that the benchmarking program itself adds a lot of latency/
overhead. But this added latency should stay constant since the benchmarker
always does the same amount of work. So latency and overhead are only valid
to compare between test runs; they cannot be correctly interpreted as the
absolute values.

# Test Results

### Small

| Test setup | avg latency | stdev latency | avg server compute time | stdev server compute time | avg overhead | stdev overhead |
|------------|-------------|---------------|-------------------------|---------------------------|--------------|----------------|
| Bare-metal | 0.0275      | 0.0233        | 0                       | 0                         | 0.0275       | 0.0233         |
| Single Pi  | 0.0182      | 0.0570        | 0                       | 0                         | 0.0182       | 0.0570         |
| 4 Pi       | 0.0587      | 0.0361        | 0                       | 0                         | 0.0587       | 0.0361         |


### Medium

| Test setup | avg latency | stdev latency | avg server compute time | stdev server compute time | avg overhead | stdev overhead |
|------------|-------------|---------------|-------------------------|---------------------------|--------------|----------------|
| Bare-metal | 27.6534     | 3.7078        | 0.6060                  | 0.1572                    | 27.0474      | 3.5781         |
| Single Pi  | 24.6364     | 1.7218        | 0.5143                  | 0.0208                    | 21.1221      | 1.7246         |
| 4 Pi       | 11.4966     | 5.4865        | 0.5353                  | 0.0254                    | 10.9613      | 5.4930         |


### Large

| Test setup | avg latency | stdev latency | avg server compute time | stdev server compute time | avg overhead | stdev overhead |
|------------|-------------|---------------|-------------------------|---------------------------|--------------|----------------|
| Bare-metal | 79.8014     | 0             | 3.1747                  | 0                         | 76.6268      | 0              |
| Single Pi  | 82.4267     | 0             | 4.1829                  | 0                         | 78.2437      | 0              |
| 4 Pi       | 82.9208     | 0             | 4.1593                  | 0                         | 78.7614      | 0              |

# Analysis

For the small case when computing 5! many times, the time required to actually compute 5! is effectively 0, so this test mainly measures all the overhead from the OS + Docker + Kubernetes. The Python+Docker (bare-metal) and single-worker-node Kubernetes setups both had similar latencies, but the four-node Kubernetes cluster had a much higher latency per request. I suspect this is due to the overhead of having to coordinate the routing of requests between the four nodes.

For the medium case when computing 30,000! many times, Python+Docker and single-node Kubernetes both had similar performances, but the four-node Kubernetes cluster performed 2-3x better. When the factorial computations actually took some time, having four nodes to distribute the many requests across allowed the system to perform better overall.

For the large case when computing 100,000! once, the three setups had overall similar performances, with Kubernetes adding a small overhead. Of note is that the server reported that computing 100,000! took 3-4 seconds, but on the client side it took about 80 seconds between sending the request and getting the result. I haven't been able to figure out why this is the case - running this minimal timing example directly on a Pi, the program correctly prints out that 80 seconds have elapsed, and it does actually take 80 seconds to run:

```python
#!/usr/bin/env python3
import math
from time import time

start_time = time()
print(math.factorial(100000))  # without print(), this call is optimized out
print(time() - start_time)
```

This is the same timing code used in the Docker image being run on the Pis and in Kubernetes. Perhaps this is an issue with Docker and with the Pi not having a hardware clock?
