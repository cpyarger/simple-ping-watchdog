import socket


def socket_connect(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((str(host), int(port)))
    except socket.error:
        return False
    sock.close()
    return True
