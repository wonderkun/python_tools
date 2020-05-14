import socket
import ssl

def http():

    p = b'''GET /get HTTP/1.1
Host: www.httpbin.org
User-Agent: raw-socket-aaa

'''.replace(b'\n', b'\r\n')

    with socket.create_connection(('www.httpbin.org', '80'), timeout=5) as conn:
        conn.send(p)
        print(conn.recv(10240).decode())

def https():
    context = ssl.create_default_context() 
    p = b'''GET / HTTP/1.1
Host: sha512.badssl.com
User-Agent: raw-socket-aaa

'''.replace(b'\n', b'\r\n')
    with socket.create_connection(('sha512.badssl.com', 443), timeout=5) as conn:
        with context.wrap_socket(conn, server_hostname='sha512.badssl.com') as sconn:
            sconn.send(p) 
            print(sconn.recv(10240).decode())

if __name__ == "__main__":
    http()
    https()
