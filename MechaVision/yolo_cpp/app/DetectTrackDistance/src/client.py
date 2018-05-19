import zmq

context = zmq.Context()
socket = context.socket(zmq.REQ)
port = "1234"
socket.connect("tcp://localhost:%s" % port)

for i in range(1, 10):
    if i == 9:
	socket.send("Stop");
    else:
        socket.send("Sayiing hello from python");
    message = socket.recv()
    print "Received reply from server: ", message
