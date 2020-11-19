try:
    import usocket as socket
except:
    import socket

response_404 = """HTTP/1.0 404 NOT FOUND

<h1>404 Not Found</h1>
"""

response_500 = """HTTP/1.0 500 INTERNAL SERVER ERROR

<h1>500 Internal Server Error</h1>
"""

response_template = """HTTP/1.0 200 OK

%s
"""

import machine
import ntptime, utime
from machine import RTC
from machine import Pin
from time import sleep

try:
    seconds = ntptime.time()
except:
    seconds = 0

rtc = RTC()
rtc.datetime(utime.localtime(seconds))

def time():
    body = """<html>
<body>
<h1>Time</h1>
<p>%s</p>
</body>
</html>
""" % str(rtc.datetime())

    return response_template % body

def dummy():
    body = "This is a dummy endpoint"

    return response_template % body

def switch():
    switch = Pin(4, Pin.IN)
    switch_status = switch.value()
    if switch_status == 0:
        body = "Your switch is off."
        return response_template % body
    if switch_status == 1:
        body = "Your switch is on."
        return response_template % body
    else:
        return response_template % "I have no idea what your switch is doing."

def light():
    adc = machine.ADC(0)
    body = "{value:" + str(adc.read()) + "}"
    return response_template % body
#pin = machine.Pin(10, machine.Pin.IN)

handlers = {
    'time': time,
    'dummy': dummy,
    'switch': switch,
    'light': light,
}

def main():
    s = socket.socket()
    ai = socket.getaddrinfo("0.0.0.0", 8080)
    addr = ai[0][-1]

    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind(addr)
    s.listen(5)
    print("Listening, connect your browser to http://<this_host>:8080")

    while True:
        res = s.accept()
        client_s = res[0]
        client_addr = res[1]
        req = client_s.recv(4096)
        print("Request:")
        print(req)

        try:
            path = req.decode().split("\r\n")[0].split(" ")[1]
            handler = handlers[path.strip('/').split('/')[0]]
            response = handler()
        except KeyError:
            response = response_404
        except Exception as e:
            response = response_500
            print(str(e))

        client_s.send(b"\r\n".join([line.encode() for line in response.split("\n")]))

        client_s.close()
        print("Done")


main()
