import os,sys,time
from pysyslogclient import *

class SyslogC:
    def SendSysLog(message,dict):
        syslog_server = dict['Syslog_server']
        syslog_port = dict['Syslog_port']
        syslog_message = message

        client = SyslogClientRFC3164(syslog_server,syslog_port, proto="udp")
        send = client.log(syslog_message, facility=FAC_SYSLOG, severity=SEV_NOTICE, program="SyslogClient", pid=os.getpid())
        return "Syslog message has been sent"
