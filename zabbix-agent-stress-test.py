#!/usr/bin/python

'''
 ** zabbix-agent-stress-test.py
 ** - script for zabbix agent stress testing - how many queries per second 
 ** can be reached for defined item key from zabbix-agent in passive mode
 **
 ** It's full sync multithreaded code => TODO: async code (twisted)
 ** 
 ** Copyright (C) 2015 Jan Garaj - www.jangaraj.com 
 **
 ** This program is free software; you can redistribute it and/or modify
 ** it under the terms of the GNU General Public License as published by
 ** the Free Software Foundation; either version 2 of the License, or
 ** (at your option) any later version.
 **
 ** This program is distributed in the hope that it will be useful,
 ** but WITHOUT ANY WARRANTY; without even the implied warranty of
 ** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 ** GNU General Public License for more details.
 **
 ** You should have received a copy of the GNU General Public License
 ** along with this program; if not, write to the Free Software
 ** Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.     
'''

import sys, getopt
import socket, struct, threading, multiprocessing
from timeit import default_timer as timer

# global variables
zabbix_agent_host = '127.0.0.1'
zabbix_agent_port = 10050
threads = 1
timeout = 10
key = ''
success = 0
error = 0
rate_avg = 0
count = 0

def str2packed(data):
    header_field =  struct.pack('<4sBQ', 'ZBXD', 1, len(data))
    return header_field + data

def packed2str(packed_data):
    header, version, length = struct.unpack('<4sBQ', packed_data[:13])
    (data, ) = struct.unpack('<%ds'%length, packed_data[13:13+length])
    return data

def zabbixconntest():
    global success
    global error
    global zabbix_agent_host
    global zabbix_agent_port
    global timeout
    global key
    conoptions = [((socket.AF_INET), (zabbix_agent_host, zabbix_agent_port))]
    family, hostport = conoptions[0]
    s = socket.socket(family, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect(hostport)
    except socket.timeout:
        error = error + 1
        return "Timeout"        
    except socket.error, err:
        error = error + 1
        return "Socket error (%s)" % str(err)
    s.sendall(str2packed(key))

    data = ''
    while True:
        buff = s.recv(1024)
        if not buff:
            break
        data += buff
    packed2str(data)
    s.close()
    success = success + 1
    return data   

def worker():
    global rate_avg
    global count 
    while True:
        count = count + 1
        start = timer()
        zabbixconntest()
        end = timer()
        rate = 1/(end-start)
        rate_avg = (rate_avg + rate)/2
        #print "Success: %d\tError: %d\tCurrent rate: %.2f qps\tAvg rate: %.2f qps" % (success, error, rate, rate_avg)

def main(argv):
    global zabbix_agent_host
    global zabbix_agent_port
    global timeout
    global key
    global threads
    try:
       opts, args = getopt.getopt(argv,"hs:p:k:t:",["host=", "port=", "key=", "threads="])
    except getopt.GetoptError, e:
       print 'Error option parsing' + str(e)
       sys.exit(2)
    for opt, arg in opts:
       if opt == '-h':
          print 'Usage:\n' + __file__ + ' [-h] [-s <host name or IP>] [-p <port>] -k <key>'
          print """
Utility for stress testing of zabbix_agent - how many queries per second can be reached for defined item key.

Options:
  -s, --host <host name or IP>
    Specify host name or IP address of a host. Default value is 127.0.0.1

  -p, --port <port>
    Specify port number of agent running on the host. Default value is 10050

  -k, --key <key of metric>
    Specify key of item to retrieve value for

  -t, --threads <number of thread>
    Specify number of worker threads

  -h, --help
    Display help information

Example: ./zabbix_agent_stress_test -s 127.0.0.1 -p 10050 -k agent.ping
          """
          sys.exit()
       elif opt in ("-s", "--host"):
          zabbix_agent_host = arg
       elif opt in ("-p", "--port"):
          zabbix_agent_port = arg
       elif opt in ("-k", "--key"):
          key = arg
       elif opt in ("-t", "--threads"):
          threads = int(arg)

    cpus=multiprocessing.cpu_count()
    if threads>cpus:
        print "Warning: you are starting more threads, than your system has available CPU cores (%s)!" % cpus
    print "Starting %d threads, host: %s:%d, key: %s" % (threads, zabbix_agent_host, zabbix_agent_port, key)
    for i in range(threads):
        t = threading.Thread(target=worker)
        t.setDaemon(True)
        t.start()

    import time
    startg = timer()    
    try:        
        while True:
            time.sleep(1)
            print "Success: %d\tErrors: %d\tAvg rate: %.2f qps\tExecution time: %.2f sec" % (success, error, rate_avg*threads, timer()-startg)
    except KeyboardInterrupt:
        total_time = timer()-startg
        print "\nSuccess: %d\tErrors: %d\tAvg rate: %.2f qps\tExecution time: %.2f sec" % (success, error, rate_avg*threads, total_time)
        print "Avg rate based on total execution time and success connections: %.2f qps" % (success/total_time) 
        sys.exit(0)

if __name__ == "__main__":
    main(sys.argv[1:])
