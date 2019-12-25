# Docker Benchmark With Raspberry Pi

A simple Docker image is used to test and benchmark the cluster. The
image runs a HTTP server which will compute the factorial of a POSTed
number and additionally return the real-world time used to compute it.

Make a file called `Dockerfile` with content:

```
FROM python:latest            # USE THIS LINE FOR RUNNING ON x64 COMPUTERS
FROM arm32v7/python:latest    # USE THIS LINE FOR RUNNING ON RASPBERRY PIS
COPY prog.py /
EXPOSE 80
CMD python3 prog.py
```

Note that if you are making an x64 image (with `python:latest`) you will need to
do these steps on an x64 computer, and if you are making an ARM32v7 image (with
`arm32v7/python:latest`) you will need to do these steps on a Pi (or another
ARM32v7 computer).

And a file `prog.py` with content:

```python
#/usr/bin/env python3

# server that returns the factorial of a given number, along with the time taken
#  to compute it

from time import time
from math import factorial
from http.server import HTTPServer, BaseHTTPRequestHandler

import socket
hostname = socket.gethostname()

class FactorialHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/plain')
		self.end_headers()
		self.wfile.write("server working on node {}!\n".format(hostname).encode('utf8'))

	def do_POST(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/plain')
		self.end_headers()

		n = int(self.rfile.read(int(self.headers['Content-Length'])))

		start_time = time()
		f = factorial(n)
		t = time() - start_time

		fmtstr = 'Factorial of {} is {}\nTook {} seconds to compute on node {}\n'
		self.wfile.write(fmtstr.format(n, f, t, hostname).encode('utf8'))

if __name__ == '__main__':
	print('running!')
	httpd = HTTPServer(('0.0.0.0', 80), FactorialHandler)
	httpd.serve_forever()
```

---

Build and then run the Docker image as follows:

```bash
$ sudo docker build -t factorial .
  # (or, with a different name for the ARM image)
$ sudo docker build -t factorial-arm .

$ sudo docker run --rm -it --name factorial -p 8080:80 factorial[-arm]
  # exposes port 80 of the container to port 8080 on localhost
```

You can then test the program with this command:

```bash
$ curl -X POST -d 5 localhost:8080
```

The `-d` option specifies the data curl POSTs - in this case, the number to
compute the factorial of.

---

To publish the image to Docker Hub:

```bash
$ sudo docker build -t yourUsername/factorial[-arm]:v1 .
$ sudo docker push yourUsername/factorial[-arm]:v1
```

I made an x64 image and ARM32v7 image and pushed them to my Docker Hub account
as `subraizada3/factorial:v2` and `subraizada3/factorial-arm:v2`. These will be
used later to benchmark the Kubernetes cluster. Of course, you can follow these
steps to create your own identical image and use that for benchmarking.
