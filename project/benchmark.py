#!/usr/bin/env python3

# Usage:
# ./benchmark.py
# ./benchmark.py fast      # much quicker, but less useful results

import sys

# Fast   =>  20 requests for 5!
# Normal => 300 requests for 30,000!
if len(sys.argv) == 2:
	NUM_REQUESTS = 20
	NUM = 5 # to compute factorial of
else:
	NUM_REQUESTS = 300
	NUM = 30_000 # to compute factorial of


import math
from time import time
from multiprocessing.dummy import Pool as ThreadPool
from cloudmesh.common.Shell import Shell
from pprint import pprint
from statistics import mean, pstdev


NUM_THREADS = 4

SERVER_IP = 'localhost'
SERVER_PORT = '8080'
SERVER_IP_PORT = f'{SERVER_IP}:{SERVER_PORT}'

CURL_CMD_STR_TEMPLATE = 'curl -s -X POST -d {} {}'
CURL_CMD_STR = CURL_CMD_STR_TEMPLATE.format(NUM, SERVER_IP_PORT)
CURL_NULL_CMD_STR = CURL_CMD_STR_TEMPLATE.format(NUM, '0.0.0.0')

NUM_PINGS = 5
PING_CMD_STR = f'ping -c {NUM_PINGS} -i 0.5 {SERVER_IP}'



def curl(i):
	"""
	curl the server and return the results

	:param i: sequence number (only used for bookkeping by benchmarker)
	:return: array of the form [i, factorial result, latency, server compute time, overhead]
	"""

	start_time = time()
	result = Shell.run(CURL_CMD_STR)
	latency = time() - start_time

	factorial = int(result.splitlines()[0].split(' ')[-1])
	server_compute_time = float(result.splitlines()[1].split(' ')[1])
	overhead = latency - server_compute_time
	#pprint([i, factorial, latency, server_compute_time, overhead])
	return [i, factorial, latency, server_compute_time, overhead]



#
# Step 1: measure the latency of the Shell.run() call to curl
#
print('Measuring Shell.run() latency => ', end='', flush=True)
latencies = []
for i in range(10):
	t = time()
	Shell.run(CURL_NULL_CMD_STR)
	t = time() - t
	latencies.append(t)
shell_run_latency = mean(latencies) #sum(latencies) / len(latencies)
print('{:.4f}'.format(shell_run_latency))


#
# Step 2: measure the RTT to the server
#
print('Pinging server to measure RTT => ', end='', flush=True)
ping_result = Shell.run(PING_CMD_STR)
ping_result = ping_result.splitlines()[-1]
avg_rtt = float(ping_result.split('/')[4])
print(avg_rtt)
print()


#
# Step 3: run the benchmark curl commands
#
benchmark_start_time = time()
print(f'Starting benchmark of {NUM_REQUESTS} factorial calls, n={NUM}')
results = ThreadPool(NUM_THREADS).map(curl, range(NUM_REQUESTS))
benchmark_time = time() - benchmark_start_time


#
# Step 4: analyze the results
#

# convert from a list of 5-length lists to 5 lists ('transpose')
results = [list(x) for x in list(zip(*results))]
#pprint(results)

# cols in transposed matrix
factorial_col = 1
latency_col = 2
server_compute_time_col = 3
overhead_col = 4

# subtract Shell.run() time and RTT from latency
for i in range(len(results[latency_col])):
	x = results[latency_col][i]
	#print(x); print(avg_rtt); print(shell_run_latency); print(); print()
	results[latency_col][i] = x - avg_rtt - shell_run_latency

# overhead = latency - server compute time
for i in range(len(results[overhead_col])):
	x = results[overhead_col][i]
	results[overhead_col][i] = results[latency_col][i] - results[server_compute_time_col][i]


# get average and stdev for latency, compute time, and overhead columns
avg_latency = mean(results[latency_col])
std_latency = pstdev(results[latency_col])
avg_server_compute_time = mean(results[server_compute_time_col])
std_server_compute_time = pstdev(results[server_compute_time_col])
avg_overhead = mean(results[overhead_col])
std_overhead = pstdev(results[overhead_col])


# check that all factorial values were correct
factorial = math.factorial(NUM)
nerr = len([x for x in results[factorial_col] if x != factorial])



#
# Step 5: print the results
#
rps = NUM_REQUESTS / benchmark_time
print('Total benchmark time: {:.4f} => {} requests/second'.format(benchmark_time, rps))

if nerr != 0:
	print(f'\n{nerr} INCORRECT RESULTS!')


print()
print('avg/stdev values (in seconds):')
print('  LATENCY       {:.4f} {:.4f}'.format(avg_latency, std_latency))
print('  SRVR COMPUTE  {:.4f} {:.4f}'.format(avg_server_compute_time, std_server_compute_time))
print('  OVERHEAD      {:.4f} {:.4f}'.format(avg_overhead, std_overhead))
