import os
import sys
import argparse
import socket, ssl

import logging
import logging.handlers

log = logging.getLogger("Observatory")

def setup_logging(debug):
    formatter = logging.Formatter("[%(asctime)s] (%(levelname)s) %(message)s")
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    if debug:
        log.setLevel(logging.DEBUG)
        ch.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
        ch.setLevel(logging.INFO)
    log.addHandler(ch)
try:
    syslog = logging.handlers.SysLogHandler(address='/dev/log')
    syslog.setLevel(logging.WARN)
    syslog.setFormatter(formatter)
    log.addHandler(syslog)

except:
	pass

def setup_arguments():
    parser = argparse.ArgumentParser(description='Hacking Labs Observatory')
    parser.add_argument('-d', action='store_true', dest='debug',default=False, help='Enable debug logging')
    parser.add_argument('-f', action='store_true', dest='foreground',default=False, help='Keep application in foreground')
    parser.add_argument('--cert', action='store', type=str, required=True, dest='cert',default=False, help='Location of certificate')
    parser.add_argument('--key', action='store', type=str, required=True, dest='key',default=False,help='Location of key')
    parser.add_argument('--ca', action='store', type=str, required=False, dest='ca',default=7,help='Location of CA')
    return parser.parse_args()

def main():

    log.info("Server started")

    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.get_ca_certs(args.ca)
    context.load_cert_chain(certfile=args.cert, keyfile=args.key)

    bindsocket = socket.socket()
    bindsocket.bind(('localhost', 4433))
    bindsocket.listen(5)

    log.info("Socket bound")

    while True:
        newsocket, fromaddr = bindsocket.accept()
        connstream = context.wrap_socket(newsocket, server_side=True)
        log.debug('Connection wrapped')
        try:
            deal_with_client(connstream)
        finally:
            connstream.shutdown(socket.SHUT_RDWR)
            connstream.close()

    log.info("Server ended")

def deal_with_client(connstream):
    log.debug('Got client')
    data = connstream.recv()
    # null data means the client is finished with us
    connstream.send(bytes("HTTP/1.1 200 OK\nContent-Length: 0\n\n", 'UTF-8'))

if __name__ == "__main__":

    global args
    args = setup_arguments()
    setup_logging(args.debug)

    main()
