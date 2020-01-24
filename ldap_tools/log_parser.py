import datetime
import re

from collections import OrderedDict

# the maximum number of seconds (in real time) slapd will spend answering a search request. The default time limit is 3600
# L'id della connessione non è attendibile
# per questa ragione un LDAPauthLog non può aggiungere un altro ACCEPT... bisogna creare un identificativo univoco diverso!

ex = 'op=0 BIND dn="uid=peppe,ou=people,dc=testunical,dc=it" method='
regexp = 'op=0 BIND dn="[a-z\,\-\=]*" method='

# syslog format
#regexp_dt = '([a-z]{3} [0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2})'

regexp_dt = '([0-9]{2}-[0-9]{2}-[0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2})'
regexp_conn = 'conn=([0-9]*)'
regexp_status = '(ACCEPT|BIND|RESULT)+'

reg = '.*'.join((regexp_dt, regexp_conn, regexp_status))

# if accept get ip
regexp_ip = '(IP\=[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})'

# if BIND get dn and method
regexp_bind = 'BIND ([a-zA-Z\=\"\,\-\_\.0-9]+) method=([0-9]+)'

# if RESULT get err (if 0 auth failed)
regexp_res = 'RESULT tag=([0-9]+) err=([0-9]+)'

tracciato_good = """Jul 21 02:08:09 slapd-d9 slapd[524]: conn=1002 fd=16 ACCEPT from IP=192.168.56.1:39528 (IP=0.0.0.0:636)
Jul 21 02:08:09 slapd-d9 slapd[524]: conn=1002 fd=16 TLS established tls_ssf=256 ssf=256
Jul 21 02:08:09 slapd-d9 slapd[524]: conn=1002 op=0 BIND dn="uid=peppe,ou=people,dc=testunical,dc=it" method=128
Jul 21 02:08:09 slapd-d9 slapd[524]: conn=1002 op=0 BIND dn="uid=peppe,ou=people,dc=testunical,dc=it" mech=SIMPLE ssf=0
Jul 21 02:08:09 slapd-d9 slapd[524]: conn=1002 op=0 RESULT tag=97 err=0 text=
Jul 21 02:08:09 slapd-d9 slapd[524]: conn=1002 fd=16 closed (connection lost)"""

tracciato_fail = """Jul 21 02:08:21 slapd-d9 slapd[524]: conn=1003 fd=16 ACCEPT from IP=192.168.56.1:39530 (IP=0.0.0.0:636)
Jul 21 02:08:22 slapd-d9 slapd[524]: conn=1003 fd=16 TLS established tls_ssf=256 ssf=256
Jul 21 02:08:22 slapd-d9 slapd[524]: conn=1003 op=0 BIND dn="uid=peppe,ou=people,dc=testunical,dc=it" method=128
Jul 21 02:08:22 slapd-d9 slapd[524]: conn=1003 op=0 RESULT tag=97 err=49 text=
Jul 21 02:08:22 slapd-d9 slapd[524]: conn=1003 fd=16 closed (connection lost)"""

f = open('/var/log/slapd.log')

# devo greppare in questa sequenza
# - ACCEPT
# - BIND
# - RESULT

class LDAPAuthLogCollection(object):
    def __init__(self):
        self.items = OrderedDict()
    def add(self, event_log):
        """
        get AuthLog or related events
        create new items or classify events related to them
        """
        if not self.items.get(event_log.id):
            self.items[event_log.id] = LDAPAuthLog(event_log)
        self.items[event_log.id].add_event(event_log)
    def first(self):
        first = list(log_collection.items.keys())[0]
        return self.items[first]
    def last(self):
        last = list(log_collection.items.keys())[-1]
        return self.items[last]
    def sort_by_date(self):
        pass
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return '{} - {}'.format(self.first(),
                                self.last(),)
class LDAPAuthLog(object):
    def __init__(self, event_log):
        """
        get envet_log objects and collect next events related to the same
        connection
        """
        self.id = event_log.id
        self.date = event_log.date
        # list of LDAPEventLog objects
        self.events = []
        self.ip = ''
        self.bind = ''
        self.result = ''
    def add_event(self, event):
        """
        add LDAPEventLog
        """
        if not event.parsed:
            event.parse()
        if int(event.id) == self.id:
            self.events.append(event)
        else:
            raise Exception('{} doesn\'t belongs to {}'.format(event, self))
        # event classification
        if event.status == 'ACCEPT' and hasattr(event, 'ip'):
            self.ip = event.ip
        elif event.status == 'BIND' and hasattr(event, 'bind'):
            self.bind = event.bind
        elif event.status == 'RESULT' and hasattr(event, 'result'):
            self.result = event.result
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return '{} [{}]'.format(self.date, self.id)
        
        
class LDAPEventLog(object):
    def __init__(self, res, line):
        """
        get regexp result and original line to get other informations
        """
        self.status = res[2]
        self.id = int(res[1])
        self.date = datetime.datetime.strptime(res[0], '%d-%m-%Y %H:%M:%S')
        self.line = line
        # it gets the most important information related to this event
        self.parsed = ''
    def parse(self):
        """
        detect status and extract its attributes
        """
        if self.status == 'ACCEPT':
            self.ip = re.findall(regexp_ip, line)
            self.parsed = self.ip
        elif self.status == 'BIND':
            self.bind = re.findall(regexp_bind, line)
            self.parsed = self.bind
        elif self.status == 'RESULT':
            self.result = re.findall(regexp_res, line)
            self.parsed = self.result
        else:
            raise Exception('LDAPEventLog.parse failed on: {}'.format(line))
    def __repr__(self):
        return self.__str__()
    def __str__(self):
        return '{} {} {}'.format(self.date, self.status, self.parsed)
        

# Create a LDAPAuthLogCollection to manage the events
log_collection = LDAPAuthLogCollection()

# parse di datetime, azione, ip e codice di errore (0 = success)
for line in f.readlines():
    res = re.findall(reg, line)
    if res:
        event = LDAPEventLog(res[0], line)
        #print(res, line)
        event.parse()
        log_collection.add(event)
        #print(res)
    else:
        pass
        #print(line)
#ff = f.readlines()
f.close()

log_collection
