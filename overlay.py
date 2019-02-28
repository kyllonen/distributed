


import threading
import socket
import sys
import random
import time
import select

m = 10
#port to listen to
port = 5000
#node id initialized as a global variable 
nid = -1


class socketlistener (threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
	def run(self):
		global nid
		global port
		global x	
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                #server.setblocking(0)
                host = socket.gethostname()
		#print '%s %s' % (host, port)
		
		server.bind((host,port))
                #print 'Node %s starting up on %s port %s \nwaiting for messages\n\n' % (nid, host, port)
		sys.stdout.flush()
                server.listen(5)
		#server.settimeout(15.0)
		server.setblocking(0)		

		inputs = [ ]
		outputs = [ ]
		inputs.append(server)
		connection = None
		while inputs:
			readable, writable, exceptional = select.select(inputs, outputs, inputs)

                        for s in readable:

                                if s is server:
					#print >>sys.stderr, 'Waiting'
                                        connection, client_address = s.accept()
                                        #print >>sys.stderr, 'Node %s received new connection from %s' % (nid, client_address)
                                        connection.setblocking(0)
                                        inputs.append(connection)
                                else:
					
					
                                        data = s.recv(1024)
					
				
                                        if data:
						a, b = s.getpeername()
						remotehost =socket.getfqdn(a)
						msg = None
						msgtype = data.split()[0]
						newnodeid = data.split()[1]	
						if msgtype == 'j':
							print 'Node %s (%s) joined network' % (newnodeid, remotehost)
							sys.stdout.flush()
                                                
						
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

					

class node:
	
	def __init__(self, nodeid):
		global m
		global nid
		self.predecessor = None
		self.successor = self
		self.nodeid = nid = nodeid
		self.host = socket.getfqdn(socket.gethostname())
		self.finger = [ ]
		for i in range(m):
			self.finger.append(None)
	#h - host(already existing node on the network) to join
	#nodeid - ID of the joining node
	def join(self, h, nodeid):
		global nid
		#print socket.getfqdn()
		if socket.getfqdn(self.host) == h: #node joins 'itself' and creates a new network
			for i in range(10):
                        	self.finger[i] = self
			print >>sys.stderr, 'Node %s (%s) created network' % (nid, self.host)
		else:
			self.sendmessage(h, 'j')
		#successor = self.findsuccessor(self.nodeid, 0)
		#print "Node %s from %s joined network" % (self.nodeid, self.host)
		
			
	def findnode(self, nodeid, hops, msg):
		target = None
		if self.successor.nodeid == nodeid:
			target = self.successor
			
		else:
			tmp = self.closestpredecessor(nodeid)
			
			hops = hops + 1
			
			sys.stdout.flush()
		sendmessage(target, 'f')
		
	def closestpredecessor(self, node):	
		for i in range(m-1, -1, -1):
			if self.nodeid < self.finger[i].nodeid < node:
				return self.finger[i]
		return self
	def notify(self, node):
		if self.predecessor == None or self.predecessor.nodeid < node.nodeid < self.nodeid:
			self.predecessor = node
	def stabilize(self):
		
		temp = self.successor.predecessor
		if self.nodeid < temp.nodeid < self.successor.nodeid:
			self.successor = temp
		self.successor.notify(self)
	def fixfingers(self):
		for i in range(1, m + 1, 1):
			a = i-1
			b = 2**a
			self.finger[i], z = self.findnode(b, 0)  
	#Sends a message msg to the specified host/node where
	#msgtype =
	#'j'; send message of joining network
	def sendmessage(self, h, msgtype, *others):
		global port
		s = socket.socket()
                attempts = 0
                maxattempts = 5
                while attempts <= maxattempts:
			try:
				s.connect((h, port))
				if msgtype == 'j':
					msg = '%s %s'  % (msgtype, nid)
				elif msgtype == 'r':
					msg = '%s %s %s %s'  % (msgtype, nid, others[0], others[1])
				s.send(msg)
				#data = s.rcv(1024)
				
			except Exception:
				print 'Could not connect to %s port %s' % (h, port)
                       		attempts += 1
                        	r = random.random() / 2
                        	time.sleep(r)
                	else:
                                #print 'Sent message to %s port %d' % (h, port)
                                s.close()
                                break
	
		


		
	#def checkpredecessor():
	#propably not necessary for the project as the failure of nodes is not a main concern(?)			






#main program loop
######################################
server = socketlistener()
server.start()
if len(sys.argv) != 3:
        print 'Invalid arguments; must be "program host nodeid"'
        sys.exit()

nid = sys.argv[2]
h = sys.argv[1]
#Node running on this process
x = node(nid)
x.join(h, nid)
