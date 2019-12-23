#!/usr/bin/env python3

import sys
import subprocess

if len(sys.argv) != 2:
	print("Usage: python test.py MASTER_NODE_NAME\ne.g. python test.py pi1")
	sys.exit(0)

master_node_name = sys.argv[1]

cmd = 'echo "kubectl get nodes" | cms pi cmd ' + master_node_name

result = subprocess.check_output(cmd, shell=True)
# ignore first line with column headers and empty split after last \n
result = result.decode('utf-8').split('\n')[1:-1]
result = list(map(str.split, result))

master_node = result[0]
worker_nodes = result[1:]

NODE_NAME_COL = 0
STATUS_COL = 1

output = ''
nerr = 0
nnodes = 1 + len(worker_nodes)

if master_node[STATUS_COL] != 'Ready':
	nerr += 1
	output += "MASTER NODE IS NOT READY!"

for node in worker_nodes:
	if node[STATUS_COL] != 'Ready':
		nerr += 1
		output += "Node {} is not ready!".format(node[NODE_NAME_COL])

if output == '':
	print('Cluster is fully functional')
else:
	print(output)
	print(f"{nnodes-nerr}/{nnodes} nodes are functional")
