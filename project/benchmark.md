# Benchmark

The following tests were used to benchmark the Pis in these setups:

### Tests

Each test measures:

* Requests per second (for small and medium N)
* Latency (minus network RTT)
* Overhead (latency minus RTT minus server-reported computation time)

Tests:

* Small-N: 2,000 requests for 5!
* Medium-N: 300 requests for 30,000!
* Big-N: One request for 100,000!

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

| asdf       |        Latency        |  Server compute time  |       Overhead        | asdf | asdf | asdf |
| Test setup |    avg    |   stdev   |    avg    |   stdev   |    avg    |   stdev   |
|------------|-----------|-----------|-----------|-----------|-----------|-----------|
| Bare-metal | 0         | 0         | 0         | 0         | 0         | 0         |
| Single Pi  | 0         | 0         | 0         | 0         | 0         | 0         |
| 4 Pi       | 0         | 0         | 0         | 0         | 0         | 0         |
