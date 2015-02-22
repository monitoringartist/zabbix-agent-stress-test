Zabbix Agent Stress Test
========================

Script for zabbix agent stress testing - how many queries per second can 
be reached for defined item key from zabbix-agent in passive mode?

It depends on:
* zabbix-agent config: how many passive threads are started - config option StartAgents
* item, items can be slower, if they need subshell or IOPs operation, e.g. UserParameters
* HW (CPU, network, ...)
 
I was (am) looking some monitoring solution, which can "collect" 10k values per second 
(it's very specific device with 10k metrics). 99.9% of monitoring population doesn't need so 
high rate, but it can be usefull for rest of them (0.1%).
 
Stress test code can be more precise and also async => provided results are only informative. 
Stress test is only for zabbix-agent passive mode and maybe active mode can provide  
better performance (IDNK).   

# Stress test examples

Some examples for Zabbix agent 2.4.3 on localhost and StartAgents=4:

Expected ~4 qps, because 4 agents threads are started and every execution needs 1 sec (sleep 1):

    [root@zabbixagent zabbix-agent-stress-test]# ./zabbix-agent-stress-test.py -s 127.0.0.1 -k "system.run[sleep 1]" -t 20
    Warning: you are starting more threads, than your system has available CPU cores (2)!
    Starting 20 threads, host: 127.0.0.1:10050, key: system.run[sleep 1]
    Success: 4      Errors: 0       Avg speed: 18.55 qps    Execution time: 1.00 sec
    Success: 7      Errors: 0       Avg speed: 11.04 qps    Execution time: 2.00 sec
    Success: 11     Errors: 0       Avg speed: 7.13 qps     Execution time: 3.00 sec
    Success: 12     Errors: 0       Avg speed: 6.88 qps     Execution time: 4.00 sec
    Success: 16     Errors: 0       Avg speed: 5.10 qps     Execution time: 5.01 sec
    Success: 20     Errors: 0       Avg speed: 4.05 qps     Execution time: 6.01 sec
    Success: 24     Errors: 0       Avg speed: 3.98 qps     Execution time: 7.01 sec
    Success: 28     Errors: 0       Avg speed: 3.97 qps     Execution time: 8.01 sec
    Success: 32     Errors: 0       Avg speed: 3.96 qps     Execution time: 9.01 sec
    Success: 36     Errors: 0       Avg speed: 3.96 qps     Execution time: 10.02 sec
    Success: 40     Errors: 0       Avg speed: 3.96 qps     Execution time: 11.02 sec
    Success: 44     Errors: 0       Avg speed: 3.96 qps     Execution time: 12.02 sec
    Success: 48     Errors: 0       Avg speed: 3.96 qps     Execution time: 13.02 sec
    Success: 52     Errors: 0       Avg speed: 3.97 qps     Execution time: 14.03 sec
    Success: 56     Errors: 0       Avg speed: 3.98 qps     Execution time: 15.03 sec
    ...
    
Expected ~400 qps value, because 4 agents threads are started and execution needs ~0.01 sec (echo 1):

    [root@zabbixagent zabbix-agent-stress-test]# ./zabbix-agent-stress-test.py -s 127.0.0.1 -k "system.run[echo 1]" -t 20
    Warning: you are starting more threads, than your system has available CPU cores (2)!
    Starting 20 threads, host: 127.0.0.1:10050, key: system.run[echo 1]
    Success: 596    Errors: 0       Avg speed: 525.18 qps   Execution time: 1.00 sec
    Success: 1144   Errors: 0       Avg speed: 564.76 qps   Execution time: 2.00 sec
    Success: 1673   Errors: 0       Avg speed: 479.72 qps   Execution time: 3.00 sec
    Success: 2230   Errors: 0       Avg speed: 646.48 qps   Execution time: 4.00 sec
    Success: 2808   Errors: 0       Avg speed: 577.59 qps   Execution time: 5.01 sec
    Success: 3357   Errors: 0       Avg speed: 532.59 qps   Execution time: 6.01 sec
    Success: 3950   Errors: 0       Avg speed: 589.85 qps   Execution time: 7.01 sec
    Success: 4536   Errors: 0       Avg speed: 527.77 qps   Execution time: 8.01 sec
    Success: 5112   Errors: 0       Avg speed: 595.04 qps   Execution time: 9.01 sec
    Success: 5686   Errors: 0       Avg speed: 620.66 qps   Execution time: 10.01 sec
    Success: 6247   Errors: 0       Avg speed: 600.07 qps   Execution time: 11.01 sec
    Success: 6802   Errors: 0       Avg speed: 521.53 qps   Execution time: 12.01 sec
    Success: 7362   Errors: 0       Avg speed: 548.17 qps   Execution time: 13.01 sec
    Success: 7933   Errors: 0       Avg speed: 580.31 qps   Execution time: 14.01 sec
    ...

Probably maximum qps value, when 4 agents threads are started - item key is agent.ping, so no subshell 
execution of IOPs is needed for this item:
    
    [root@zabbixagent zabbix-agent-stress-test]# ./zabbix-agent-stress-test.py -s 127.0.0.1 -k "agent.ping" -t 4
    Warning: you are starting more threads, than your system has available CPU cores (2)!
    Starting 4 threads, host: 127.0.0.1:10050, key: agent.ping
    Success: 3354   Errors: 0       Avg speed: 3406.18 qps  Execution time: 1.00 sec
    Success: 6692   Errors: 0       Avg speed: 4054.38 qps  Execution time: 2.00 sec
    Success: 9952   Errors: 0       Avg speed: 3347.73 qps  Execution time: 3.00 sec
    Success: 13395  Errors: 0       Avg speed: 3476.23 qps  Execution time: 4.00 sec
    Success: 16511  Errors: 0       Avg speed: 3946.44 qps  Execution time: 5.00 sec
    Success: 20041  Errors: 0       Avg speed: 4049.99 qps  Execution time: 6.01 sec
    Success: 23502  Errors: 0       Avg speed: 8685.35 qps  Execution time: 7.01 sec
    Success: 26875  Errors: 0       Avg speed: 5739.68 qps  Execution time: 8.01 sec
    Success: 30107  Errors: 0       Avg speed: 6029.05 qps  Execution time: 9.01 sec
    Success: 33344  Errors: 0       Avg speed: 3814.14 qps  Execution time: 10.01 sec
    ...
    
# Conclusion  
    
Zabbix Agent can handle ~3k-8k requests per second for in memory items.
If you need shell execution for your items, then it's ~0.5k requests per second.
    
    
    

 