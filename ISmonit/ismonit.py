#!/usr/bin/python2.7
# -*- coding: utf8 -*-

import argparse, re, MySQLdb

DB_CONF_PATH = '/onapp/interface/config/database.yml'
#DB_CONF_PATH = '/home/rossardy/src/python/file'

#Colours & styles
CYAN = '\033[36m'           # cyan
PURPLE = '\033[35m'         # purple
BLUE = '\033[34m'           # blue
ORANGE = '\033[33m'         # orange
GREEN = '\033[32m'          # green
YELLOW = '\033[33m'         # yellow
RED = '\033[31m'            # red
BOLD = '\033[1m'            # bold
UNDERLINE = '\033[4m'       # underline
END = '\033[0m'             # white (normal)

class HV:
    label = 'Some HV'
    ip_address = '0.0.0.0'
    online = 0
    hv_zone = 0
    host = 'noname'
    host_id = 0
    mtu = 1500
    os_version = ''
    type = ''
    disk_per_controller = 0
    disks = 0

    def __init__(self, label = None, ip_address = '1.1.1.1'):
        self.label = label or 'default'

    def controlers_count(self):
        count = self.disks // self.disk_per_controller
        rest = self.disks % self.disk_per_controller
        if rest != 0:
            count += 1
        return count

def decorator_list(func):
    def wrapper(*args, **kwargs):
        print BOLD+RED+'ISmonit is checking cloud which running on $version of storage'+END
        print YELLOW+'NOTE: Can be issues with checking cloud due isd/groupmon differences'+END
        c = func(*args, **kwargs)
        print c
        #for i in c:
        #    print c
        #print '<{tag}>{0}/<{tag}>'.format(func(*args, **kwargs)
        #return crs
    return wrapper

def hvs_gener(hvs):
    #hvs_list = ['hv'+str(x) for x in range(1,len(hvs)+1)]
    hvs_list = []
    for i in range(len(hvs)):
        temp = HV()
        temp.label = hvs[i][0]
        temp.ip_address = hvs[i][1]
        temp.online = hvs[i][2]
        temp.hv_zone = hvs[i][3]
        temp.host = hvs[i][4]
        temp.host_id = hvs[i][5]
        temp.mtu = hvs[i][6]
        temp.os_version = hvs[i][7]
        temp.type = hvs[i][8]
        temp.disk_per_controller= hvs[i][9]
        temp.disks = hvs[i][10]
        hvs_list.append(temp)
        print temp.controlers_count()
    print hvs_list
    return


#@decorator_list
def parse_file():
    with open(DB_CONF_PATH, "r") as dbfile:
        for line in dbfile:
            result = re.findall(r'\S*\S',line)
            if result[0] == 'database:':
                database = result[1]
            if result[0] == 'host:':
                host = result[1]
            if result[0] == 'password:':
                password = result[1]
            if result[0] == 'port:':
                port = result[1]
    def parse_db(database,  host,  password, port):
        db = MySQLdb.connect(host=host,               # host, usually localhost
                             #port=port,               # port, usually 3306
                             user="root",             # username, usually root
                             passwd=password,         # password
                             db=database)             # name of the data base
        sql = db.cursor()
        sql.execute("select hypervisors.label, "
                    "hypervisors.ip_address, "
                    "hypervisors.online, "
                    "hypervisors.hypervisor_group_id, "
                    "hypervisors.host, "
                    "hypervisors.host_id, "
                    "hypervisors.mtu, "
                    "hypervisors.os_version, "
                    "hypervisors.hypervisor_type, "
                    "hypervisors.disks_per_storage_controller, "
                    "count(*) as disks from hypervisor_devices "
                    "left join hypervisors "
                    "on (hypervisor_devices.hypervisor_id = hypervisors.id) "
                    "where type = 'Hypervisor::DiskDevice' and status = 1 group by hypervisor_id")
        crs = tuple(sql)
        sql.execute("select label, "
                    "ip_address, "
                    "online, "
                    "hypervisor_group_id, "
                    "host, "
                    "host_id, "
                    "mtu, os_version, "
                    "hypervisor_type from hypervisors "
                    "where host_id is not Null and backup = 1")
        bss = tuple(sql)
        db.close()
        print crs
        hvs_gener(crs)
        return crs,bss
    crs = parse_db(database, host, password, port)
    #print crs
    return crs

if __name__ == '__main__':
    # Use nargs to specify how many arguments an option should take.
    parser = argparse.ArgumentParser(description='ISmonit utility')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    parser.add_argument('--ips',  action='store_true')
    parser.add_argument('--list', action='store_true')
    parser.add_argument("--verbose","-v",action="store_true", help="Full description", default=False)
    # Grab the opts from argv
    opts = parser.parse_args()
    if opts.ips:
        print 'test'
    if opts.list:
        crs = parse_file()