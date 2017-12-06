#!/usr/bin/python2.7
# -*- coding: utf8 -*-

import argparse, re, MySQLdb

from tabulate import tabulate

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

class BS:
    """
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
    """

    def __init__(self, label='noname', ip_address='192.168.88.1', online=0, hv_zone=1, host='localhost', host_id=1, mtu=1500, os_version=6, type='kvm'):
        self.label = label or 'default'
        self.ip_address = ip_address
        self.online = bool(online)
        self.hv_zone = 'NULL'
        self.host = host
        self.host_id = int(host_id)
        self.mtu = int(mtu)
        self.os_version = int(os_version)
        self.type = type

    def frontend_ip(self):
        return '10.200.{}.254'.format(self.host_id)


class HV(BS):

    def __init__(self, label='noname', ip_address='192.168.88.1', online=0, hv_zone=1, host='localhost', host_id=1, mtu=1500, os_version=6, type='kvm', disk_per_controller=0, disks=0):
        self.label = label or 'default'
        self.ip_address = ip_address
        self.online = bool(online)
        self.hv_zone = int(hv_zone)
        self.host = host
        self.host_id = int(host_id)
        self.mtu = int(mtu)
        self.os_version = int(os_version)
        self.type = type
        self.disk_per_controller = disk_per_controller
        self.disks = disks

    def controlers_count(self):
        count = self.disks // self.disk_per_controller
        rest = self.disks % self.disk_per_controller
        if rest != 0:
            count += 1
        return count

def show_list():
    """
    This function prints list of HVs ad BSs
    """
    lst = bss_list + hvs_list
    on_line, off_line = [],[]
    print '\n'
    print BOLD+RED+'ISmonit is checking cloud which running on $version of storage'+END
    print YELLOW+'NOTE: Can be issues with checking cloud due isd/groupmon differences'+END
    print '\n'
    on_line.append(['ONLINE:','','','','','',''])
    off_line.append(['OFFLINE:','','','','','',''])
    for i in lst:
        if i.online == 1:
            on_line.append([i.label,i.ip_address,i.host_id,i.hv_zone,i.mtu,i.os_version,i.type])
        elif i.online == 0:
            off_line.append([i.label,i.ip_address,i.host_id,i.hv_zone,i.mtu,i.os_version,i.type])
    if len(off_line) > 1:
        print tabulate(on_line+off_line,headers=['label','ip_address','host_id','hv_zone','mtu','os','type'])
    else:
        print tabulate(on_line,headers=['label','ip_address','host_id','hv_zone','mtu','os','type'])

def show_ips():
    """
    This function prints ips all HVs and BSs in 'for' cycle format
    """
    lst = bss_list + hvs_list
    hvs_ips = []
    print '\n'
    print BOLD+RED+'ISmonit is checking cloud which running on $version of storage'+END
    print YELLOW+'NOTE: Can be issues with checking cloud due isd/groupmon differences'+END
    print '\n'
    for i in lst:
        if i.online == 1:
            hvs_ips.append(i.ip_address.split('.'))
    tmp = '{' + hvs_ips[0][3]
    for i in range(1,len(hvs_ips)):
        tmp = tmp + ',' + hvs_ips[i][3]
    tmp = tmp + '}'
    print ('for i in {}.{}.{}.{}; do echo $i; ssh root@$i uptime; done'.format(hvs_ips[0][0],hvs_ips[0][1],hvs_ips[0][2],tmp))

def hvs_gener(crs,bss):
    #hvs_list = ['hv'+str(x) for x in range(1,len(hvs)+1)]
    global hvs_list
    global bss_list
    hvs_list, bss_list = [],[]
    for bs in bss:
        if len(bs) == 9:
            temp = BS(bs[0],bs[1],bs[2],bs[3],bs[4],bs[5],bs[6],bs[7],bs[8])
            bss_list.append(temp)
        else:
            print BOLD+RED+'It looks you do not have any cloudboot BSs'+END
    for cr in crs:
        if len(cr) == 11:
            temp = HV(cr[0],cr[1],cr[2],cr[3],cr[4],cr[5],cr[6],cr[7],cr[8],cr[9],cr[10])
            hvs_list.append(temp)
        else:
            print BOLD+RED+'It looks you do not have any cloudboot HVs'+END
    return None

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
        #print crs
        hvs_gener(crs,bss)
    crs = parse_db(database, host, password, port)
    #print crs

if __name__ == '__main__':
    parse_file()
    # Use nargs to specify how many arguments an option should take.
    parser = argparse.ArgumentParser(description='ISmonit utility')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    parser.add_argument('--ips',  action='store_true')
    parser.add_argument('--list', action='store_true')
    parser.add_argument("--verbose","-v",action="store_true", help="Full description", default=False)
    # Grab the opts from argv
    opts = parser.parse_args()
    if opts.ips:
        show_ips()
    if opts.list:
        show_list()