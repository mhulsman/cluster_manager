#!/usr/bin/env python
import subprocess, sys, getopt, time,shlex
from subprocess import Popen
import xmlrpclib
import socket
import cluster_storage
import os,sys
import signal
import psutil
import shutil
from dns import resolver,reversename

mytype="LOCAL"
address = "localhost"
loadenv = False
port    = "30024"

opts,args = getopt.getopt(sys.argv[1:],"e:t:a:lp:",["env=","type=","address=","loadenv","port="])
for o,a in opts:
    if o in ('-t', '--type'):
        mytype = a
    elif o in ('-a' '--address'):
        address = a
    elif o in ('-l', '--loadenv'):
        loadenv = True
    elif o in ('-p', '--port'):
        port=a

#get IP address
socket.setdefaulttimeout(30)
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); 
s.connect(('google.com', 0)); 
myip = s.getsockname()[0]

try:
    addr=reversename.from_address(myip)
    myip = str(resolver.query(addr,"PTR")[0])[:-1]
except Exception,e:
    pass

#self register
print "Preparing to register on " + address + ":" + port
s = xmlrpclib.ServerProxy('http://' + address + ":" + port)
e_memtot = psutil.TOTAL_PHYMEM
e_ncpu = psutil.NUM_CPUS
myid,mycodeid = s.register(myip,mytype,e_ncpu,e_memtot/1024.0/1024.0)

print "Registered with controller, got id: " + myid

cwd = os.getcwd()
furl_path = cwd + "/engine.furl"
from_furl_path = "../../engine.furl"

def start_engine(mycodeid):
    if(loadenv):
        print "Retrieving code file from " + mycodeid 
        code_path = cluster_storage.receive_file(mycodeid)
        
        cmd = "tar -xzf " + code_path
        args = shlex.split(cmd)
        r = Popen(args).wait()
        if(r):
            raise RuntimeError, "Code unpacking failed" 
        
        print "Retrieving furl file from " + from_furl_path + " to " + furl_path
        shutil.copyfile(from_furl_path,furl_path)
        cmd = "python ../bin/ipengine --furl-file=" + furl_path
    else:
        cmd = "ipengine --furl-file=" + furl_path
    
    print "Starting local engine..."
    args = shlex.split(cmd)
    lengine = Popen(args)
    return lengine

def stop_engine(lengine):
    if(lengine.poll() is None):
        lengine.terminate() 

def handler(signum,frame):
    print "CATCH SYSTEM EXIT"
    sys.exit()

signal.signal(signal.SIGTERM,handler)

lengine=None

NOOP=0
DIE=1
RESTART_ENGINE=2

try:
    lengine = start_engine(mycodeid)
    lengine_monitor = psutil.Process(lengine.pid)
    while 1:
        if(not lengine.poll() is None):
            s.unregister(myid)
            break
        
        e_cpu = lengine_monitor.get_cpu_percent()
        e_mem = lengine_monitor.get_memory_percent()
        e_memphys,e_memvirt = lengine_monitor.get_memory_info()

        cmd,param = s.poll(myid,e_cpu,e_mem * e_ncpu, e_memphys / 1024.0 / 1024.0, e_memvirt / 1024.0 / 1024.0)
        print "POLL",cmd

        if(cmd):
            if(cmd == DIE):
                stop_engine(lengine)
                s.unregister(myid)
                break
            elif(cmd == RESTART_ENGINE):
                stop_engine(lengine)
                lengine = start_engine(mycodeid,param)
                lengine_monitor = psutil.Process(lengine.pid)
            else:
                print "UNKNOWN COMMAND RECEIVED, EXITING!"
                stop_engine(lengine)
                break
        time.sleep(120)
except (Exception, KeyboardInterrupt, SystemExit):
    if(not lengine is None):
        stop_engine(lengine)
    s.unregister(myid)
    raise
