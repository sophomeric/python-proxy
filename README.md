# python-proxy
DNS to DNS over TLS proxy example in python.

## What this is
An academic exercise really. It is a python script that acts as a DNS proxy by listening on port 53 and querying Cloudflares DNS over TLS server for the backend. I started by reading about the [select module](https://pymotw.com/2/select/) to learn how to just make a server listening for any TCP request and echoing it back. I took this exercise and extended it by turning it into a proper object/class. It makes it look nicer and more like a proper daemon in my opinion and also a bit more reusable for future projects potentially. Following that, I tinkered with the socket module further to implement the actual proxying part.

## Wish List / To Do
- Accept UDP connections too
- Make it more reusable by allowing bind_to and forward_to to be CLI arguments or environment variables.
    - Personally I like docopt
    - In kubernetes you could change the ConfigMap and have the proxy periodically check for changes and reload/reconnect.
- Detect if the input actually is a DNS query and reject those that aren't.
- Convert to Python3
- Support multiple backends and provide some fault tolerance by using the next if the first doesn't answer or fails.
- Rate limiting or caching could be added

## References
- [select module implementing a generic server](https://pymotw.com/2/select/)
- [Python2 select module](https://docs.python.org/2/library/select.html)
- [Python2 socket module](https://docs.python.org/2/library/socket.html)
- [Python2 ssl module](https://docs.python.org/2/library/ssl.html)
- [Python2 Queues module](https://docs.python.org/2/library/queue.html)
    - Ultimately this was ripped out.
- [Hand writing DNS messages with Python](https://routley.io/tech/2017/12/28/hand-writing-dns-messages.html)
    - Not really used in this project but could be useful if you wanted to more elegantly format the log messages.
