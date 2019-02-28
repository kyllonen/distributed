import select
import socket
import sys
import Queue
import threading
import random
import time





class socketloop (threading.Thread):
        def __init__self(self):
                threading.Thread.__init__(self)
        def run(self):
                global port
		global clock
		global inputs
		global outputs
		global running
		global events
		global maxevents
                server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                #server.setblocking(0)


                server_address = (socket.gethostname(), port)

                print >>sys.stderr, 'starting up on %s port %s' % server_address
                server.bind(server_address)


                server.listen(5)

                inputs.append(server)

                while inputs:
                # Wait for at least one of the sockets to be ready for processing
                #print >>sys.stderr, '\nwaiting for the next event'
			if running == False | events >= maxevents :
				server.close()
				break
                        readable, writable, exceptional = select.select(inputs, outputs, inputs)
			
                        for s in readable:

                                if s is server:
                                        print 'is server'
                                        connection, client_address = s.accept()
                                        print >>sys.stderr, 'new connection from', client_address
                                        connection.setblocking(0)
                                        inputs.append(connection)
                                else:
                                        data = s.recv(1024)
                                        if data:
                                                print  'Recieved clock value %s  from %s' % (data, s.getpeername())
						clockvalue = int(data)
						tmp = clock
						clock = max(clockvalue, clock) + 1
						print 'incremented own clock value to %d' % (clock)
						outputline = 'r %s %d %d' % (s.getpeername(), clockvalue, clock)
						programoutput.append(outputline) 
						events += 1
                                                if s not in outputs:
                                                        outputs.append(s)
                                        else:
                                        # Interpret empty result as closed connection
                                                print >>sys.stderr, 'closing', client_address, 'after reading no data'
                                                # Stop listening for input on the connection
                                                if s in outputs:
                                                        outputs.remove(s)
                                                inputs.remove(s)
                                                s.close()
                        #for s in writable:
                                
    
    			for s in exceptional:
        			print >>sys.stderr, 'handling exceptional condition for', s.getpeername()
        			
        			inputs.remove(s)
        			if s in outputs:
            				outputs.remove(s)
      				s.close()




def localevent():
	clock += random.randint(1, 5)
	print 'Current clock value = %d' % (clock)
def message(clientid):
	global fileName
	global clock
	clock += 1
	tstamp = clock
	f = open(fileName)
	lines = f.readlines()
	line = lines[clientid]
	arguments = line.split()
	h = arguments[1]
	p = int(arguments[2])
	f.close()
	s = socket.socket()
	
	attempts = 0
	maxattempts = 10
	while attempts <= maxattempts:
		try:
			s.connect((h, p))
			s.send(str(clock))
		except Exception:
        		#print 'Could not connect to %s port %s, trying again' % (h, p)
                	attempts += 1
                	r = random.random() / 2
                	time.sleep(r)
        	else:
        		print 'Sent message to %s port %d' % (h, p)
               		s.close()
			tmp = clientid + 1
			outputline = 's %s %d' % (tmp, clock)
			programoutput.append(outputline)
                	break
	





programoutput = [ ]		
	




if len(sys.argv) != 3:
        print 'Invalid arguments; must be "program conf.file line"'
        sys.exit()
fileName = sys.argv[1]
thisclientid = sys.argv[2]
clients = 0

f = open(fileName)
for line in f.readlines():
	print line
        arguments = line.split()
        if arguments[0] == thisclientid:
                linefound = True
                host = arguments[1]
                port = int(arguments[2])
	
	clients =+ 1
f.close()        

if linefound == False:
        sys.exit('No line in conf. file that starts with %s, exiting' % (thisclientid))


# Sockets from which we expect to read
inputs = [ ]                
# Sockets to which we expect to write                
outputs = [ ]


running = True

events = 0
maxevents = 20



loop = socketloop()
loop.start()



clock = 0

clientsrunning = 1
f = open(fileName)
for line in f.readlines():
	arguments = line.split()
	if arguments[0] != thisclientid:
		h = arguments[1]
		p = int(arguments[2])
		s = socket.socket()
		attempts = 0
		maxattempts = 15
		while attempts <= maxattempts:
			try:
				s.connect((h, p))	
				#s.send('Starting executing %s port %s' % (host, port))
			except Exception:
				#print 'Could not connect to %s port %s, trying again' % (h, p)
				attempts += 1
				r = random.random() / 2
				time.sleep(r)
			else:
				print '%s at port %d is connected' % (h, p)
				s.close()
				clientsrunning += 1
				break







while events <= maxevents:
	r = range(0, int(thisclientid)) + range(int(thisclientid) + 1, clients)
	id_ = random.choice(r)		
	message(id_)
	events += 1

running = False
f = open('output.txt', 'w')

print '\n\n\n\nOUTPUT:'
for line in programoutput:
	print line


sys.exit()

	
