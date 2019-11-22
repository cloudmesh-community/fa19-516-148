<!-- comment configures vim to enable word wrapping; gggqG to force rewrap -->

<!-- vim: set tw=79 fo+=t fo-=l: -->

# Federated Kubernetes Clusters With Raspberry Pi - Docker Benchmarking/Test Image

A simple Docker image is used to test and benchmark the cluster. The image runs
a HTTP server which will compute the factorial of a POSTed number and
additionally return the real-world time used to compute it.

Make a file called `Dockerfile` with content:

```
FROM python:latest
COPY prog.py /
EXPOSE 80
CMD python3 prog.py
```

And a file `prog.py` with content:

```
# server that returns the factorial of a given number, along with the time taken
#  to compute it

from time import time
from math import factorial
from http.server import HTTPServer, BaseHTTPRequestHandler

class FactorialHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/plain')
		self.end_headers()
		self.wfile.write("server working!\n".encode('utf8'))

	def do_POST(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/plain')
		self.end_headers()

		n = int(self.rfile.read(int(self.headers['Content-Length'])))

		start_time = time()
		f = factorial(n)
		t = time() - start_time

		fmtstr = 'Factorial of {} is {}\nTook {} seconds to compute\n'
		self.wfile.write(fmtstr.format(n, f, t).encode('utf8'))

if __name__ == '__main__':
	print('running!')
	httpd = HTTPServer(('0.0.0.0', 80), FactorialHandler)
	httpd.serve_forever()
```

---

Build and then run the Docker image as follows:

```
$ sudo docker build -t factorial .
$ sudo docker run --rm -it --name factorial -p 8080:80 factorial
```

You can then test the program with this command:

```
$ curl -X POST -d 5 localhost:8080
```

The `-d` option specifies the data curl POSTs - in this case, the number to
compute the factorial of.

---

To publish the image to Docker Hub:

```
$ sudo docker build -t yourUsername/factorial:v1 .
$ sudo docker push yourUsername/factorial:v1
```
