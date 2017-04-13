#!C:\Python27\pythonw.exe
"exec" "python" "-O" "$0" "$@"

__doc__ = """Tiny HTTP Proxy.

This module implements GET, HEAD, POST, PUT and DELETE methods
on BaseHTTPServer, and behaves as an HTTP proxy.  The CONNECT
method is also implemented experimentally, but has not been
tested yet.

Any help will be greatly appreciated.		SUZUKI Hisao
"""

__version__ = "0.2.1"

import BaseHTTPServer, select, socket, SocketServer, urlparse

import sys
import logging

logger = logging.getLogger(__name__)

class SuzukiHandler (BaseHTTPServer.BaseHTTPRequestHandler):
    __base = BaseHTTPServer.BaseHTTPRequestHandler
    __base_handle = __base.handle

    server_version = "TinyHTTPProxy/" + __version__
    rbufsize = 0                        # self.rfile Be unbuffered
    max_idling = 20

    def handle(self):
        (ip, port) =  self.client_address
        if hasattr(self, 'allowed_clients') and ip not in self.allowed_clients:
            self.raw_requestline = self.rfile.readline()
            if self.parse_request(): self.send_error(403)
        else:
            self.__base_handle()

    def _connect_to(self, netloc, soc):
        i = netloc.find(':')
        if i >= 0:
            host_port = netloc[:i], int(netloc[i+1:])
        else:
            host_port = netloc, 80
        logger.info( "\t" "connect to %s:%d" % host_port )
        try: soc.connect(host_port)
        except socket.error, arg:
            try: msg = arg[1]
            except: msg = arg
            self.send_error(404, msg)
            return 0
        return 1

    def do_CONNECT(self):
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if self._connect_to(self.path, soc):
                self.log_request(200)
                self.wfile.write(self.protocol_version +
                                 " 200 Connection established\r\n")
                self.wfile.write("Proxy-agent: %s\r\n" % self.version_string())
                self.wfile.write("\r\n")
                self._read_write(soc, 300)
        finally:
            logger.info( "\t" "bye" )
            soc.close()
            self.connection.close()

    def do_GET(self):
        (scm, netloc, path, params, query, fragment) = urlparse.urlparse(
            self.path, 'http')
        if scm != 'http' or fragment or not netloc:
            self.send_error(400, "bad url %s" % self.path)
            return
        soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if self._connect_to(netloc, soc):
                self.log_request()
                soc.send("%s %s %s\r\n" % (
                    self.command,
                    urlparse.urlunparse(('', '', path, params, query, '')),
                    self.request_version))
                self.headers['Connection'] = 'close'
                del self.headers['Proxy-Connection']
                for key_val in self.headers.items():
                    soc.send("%s: %s\r\n" % key_val)
                soc.send("\r\n")
                self._read_write(soc)
        finally:
            logger.info( "\t" "bye" )
            soc.close()
            self.connection.close()

    def _read_write(self, soc, max_idling=None):
        if max_idling is None:
            max_idling = self.max_idling
        iw = [self.connection, soc]
        ow = []
        count = 0
        while 1:
            count += 1
            (ins, _, exs) = select.select(iw, ow, iw, 3)
            if exs: break
            if ins:
                for i in ins:
                    if i is soc:
                        out = self.connection
                    else:
                        out = soc
                    data = i.recv(8192)
                    if data:
                        out.send(data)
                        count = 0
            else:
                logger.info( "\t" "idle" "%d" % count )
            if count == max_idling: break

    def log_message(self, format, *args, **kwargs):
        logger.log(logging.INFO, format, *args, **kwargs)

    def log_error(self, format, *args, **kwargs):
        logger.log(logging.ERROR, format, *args, **kwargs)

    do_HEAD = do_GET
    do_POST = do_GET
    do_PUT  = do_GET
    do_DELETE=do_GET

class SuzukiServer (SocketServer.ThreadingMixIn,
                           BaseHTTPServer.HTTPServer):

    def __init__(self, port=6666, allowed_clients=None, max_idling=20):
        server_address = ('', 6666)
        if allowed_clients:
            allowed = [socket.gethostbyname(cl) for cl in allowed_clients]
            SuzukiHandler.allowed_clients = allowed
        SuzukiHandler.max_idling = max_idling

        BaseHTTPServer.HTTPServer.__init__(self, server_address ,SuzukiHandler)

    def run(self):
        sa = self.socket.getsockname()
        logger.info( "Serving HTTP on %s port %d ..." % sa)
        if not hasattr(self.RequestHandlerClass, 'allowed_clients'):
            logger.info( "Any clients will be served..." )
        else:
            for ip in self.RequestHandlerClass.allowed_clients:
                logger.info ( "Accept: %s " % ip )
        self.serve_forever()


def run_suzuki(port=6666, allowed_clients=None, max_idling=20):
    suzuki = SuzukiServer(port=port, allowed_clients=allowed_clients,
            max_idling=max_idling)
    suzuki.run()
    return suzuki

def suzuki_main():
    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    if sys.argv[1:] and sys.argv[1] in ('-h', '--help'):
        print sys.argv[0], "[port [allowed_client_name ...]]"
    else:
        kwargs = {}
        if sys.argv[1:]:
            kwargs['port']=int(sys.argv[1])
            kwargs['allowed_clients'] = sys.argv[2:]
        run_suzuki(**kwargs)

if __name__ == '__main__':
    suzuki_main()
