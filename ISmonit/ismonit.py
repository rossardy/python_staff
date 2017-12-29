#!/usr/bin/python2.7
# -*- coding: utf8 -*-

# This utility designed by Yatsyshyn Rostyslav
# for internal L3 team using

# import usual modules
import argparse, re, subprocess, sys, os
from threading import Timer

def install_pkgs():
    '''
    This function installs missed modules
    '''
    pkgs_list = ['tabulate']
    tmp = 'pip install'
    for packet in pkgs_list:
        tmp = tmp + ' ' + packet
    subprocess.check_output(['bash', '-c', tmp + ' ' + tmp])

# <--- Check if I root?
# import non usual modules
try:
    # If modules don't exist
    import MySQLdb
    from tabulate import tabulate
    # Install pip and modules
except ImportError:
    subprocess.check_output(['bash', '-c', 'yum --enablerepo=extras install epel-release -y'])
    subprocess.check_output(['bash', '-c', 'yum -y install python-pip'])
    subprocess.check_output(['bash', '-c', 'yum install MySQL-python -y'])
    install_pkgs()
    subprocess.check_output(['bash', '-c', 'yum remove epel-release -y'])
    # Import them again
    import MySQLdb
    from tabulate import tabulate

# version of ismonit utility
__version__ = "0.4.1"

# Configuration default files
DB_CONF_PATH = '/onapp/interface/config/database.yml'
ONAPP_CONF_PATH = '/onapp/interface/config/on_app.yml'

# Storage packages and rpms begins from 5.0 version
pack_vers = (
            ('5.5.0-23', 'onappstore-master-7515.src.rpm', '06.09.17'),
            ('5.4.0-19', 'onappstore-5.4-7383.src.rpm', '17.05.17'),
            ('5.0.0-30', 'onappstore-5.0-7217.src.rpm', '15.03.17'),
            ('5.0.0-28', 'onappstore-0.0.1-2016.09.05_15.07.06.x86_64.rpm', '22.02.17'),
            ('5.3.0-4', 'onappstore-testing-0.0.1-1-2016.12.15_15.48.29.x86_64.rpm', '31.01.17'),
            ('5.2.0-5', 'onappstore-testing-0.0.1-1-2016.12.15_15.48.29.x86_64.rpm', '19.12.16'),
            ('5.2.0-4.1', 'onappstore-testing-0.0.1-1-2016.12.15_15.48.29.x86_64.rpm', '08.12.16'),
            ('5.0.0-25', 'onappstore-0.0.1-2016.09.05_15.07.06.x86_64.rpm', '13.12.16'),
            ('5.1.0-5', 'onappstore-0.0.1-2016.09.05_15.07.06.x86_64.rpm', '11.10.16'),
            ('5.0.0-22', 'onappstore-0.0.1-2016.09.05_15.07.06.x86_64.rpm', '26.09.16'),
            ('5.0.0-21', 'onappstore-0.0.1-2016.09.05_15.07.06.x86_64.rpm', '09.09.16'),
            ('5.0.0-19', 'onappstore-0.0.1-2016.09.05_15.07.06.x86_64.rpm', '05.09.16')
)

# Colours & styles
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
        """
        This method count amount of storage controllers on particular HV
        :return: amount of Storage Controllers
        """
        count = self.disks // self.disk_per_controller
        rest = self.disks % self.disk_per_controller
        if rest != 0:
            count += 1
        return count

def show_header():
    """
    Print welcome header in the top of terminal
    """
    print BOLD+YELLOW+'ISmonit is utility designed for checking Integrated Storage'+END
    print YELLOW+'NOTE: Can be issues with checking cloud due isd/groupmon differences'+END
    cp_ver, stor_ver = chck_version()
    print YELLOW+('Storage version is:       {}'.format(BOLD+stor_ver[0]))+END
    print YELLOW+('Control Penel version is: {}\n'.format(BOLD+cp_ver[0]))+END

def chck_version():
    """
    It checks CP and Storage version and if IS is enabled
    :return: versions of storage and Control Panel
    """
    cp_ver = stor_ver = 'not installed'
    try:
        # Get versions of CP and Storage
        cp_ver = re.findall(r"[0-9].{4,7}",subprocess.check_output(['bash', '-c', 'rpm -qa | grep onapp-cp-[345]']).rstrip('\n'))
        stor_ver = re.findall(r"[0-9].{4,7}",subprocess.check_output(['bash', '-c', 'rpm -qa | grep onapp-store-install']).rstrip('\n'))
        # Check if file on_app.yml exist
        if not os.path.exists('/onapp/interface/config/on_app.yml'):
            raise IOError(" file doesn't exist")
        elif not os.access(ONAPP_CONF_PATH, os.R_OK):
            raise IOError(" file has no read permissions for current user")
        # Check if IS enabled in on_app.yml
        is_enabled = subprocess.check_output(['bash', '-c','grep ^storage_enabled: /onapp/interface/config/on_app.yml | sed \'s/^storage_enabled: //g\'']).rstrip('\n')
        if not is_enabled == 'true':
            raise NameError('Integrated Storage isn\'t enabled')
    except subprocess.CalledProcessError:
        if cp_ver == 'not installed':
            print RED + BOLD + 'WARNING: ', ' Control Panel packet isn\'t installed' + END
            sys.exit(1)
        elif stor_ver == 'not installed':
            print RED + BOLD + 'WARNING: ', ' Storage packet isn\'t installed' + END
            sys.exit(1)
        else:
            print RED + BOLD + 'Unknown error' + END
    except NameError as e:
        print RED + BOLD + 'WARNING: ', str(e) + END
    except IOError as e:
        print RED + BOLD + 'WARNING: ', ONAPP_CONF_PATH, str(e) + END
        sys.exit(1)
    count = 0
    # <-- Maybe put to another function?
    # Check minor and major version difference for CS and Storage
    for i, j in zip(re.findall(r"[0-9]{1,}", cp_ver[0]), re.findall(r"[0-9]{1,}", stor_ver[0])):
        if i == j:
            count += 1
        else:
            break
    if count == 0:
        print RED + BOLD + 'WARNING: ' + END, 'Different major versions.'
    elif count == 1:
        print RED + BOLD + 'WARNING: ' + END, 'Different minor versions.'
    return cp_ver, stor_ver

def show_rpms():
    '''
    This simple function just print packages version of storage
    '''
    show_header()
    print tabulate(pack_vers,headers=['version','storage package','release date'])

def show_list():
    """
    This function prints list of HVs ad BSs
    """
    on_line, off_line = [],[]
    show_header()
    on_line.append([YELLOW+'ONLINE:'+END,'','','','','','',''])
    off_line.append([YELLOW+'OFFLINE:'+END,'','','','','','',''])
    def make_table(lst, bs=0):
        '''
        This function is used only to separate BSs and HVs in view list
        '''
        # Add additional mark if it's BS
        if bs == 0:
            addition = ''
        else:
            addition = 'Backup Server'
        for i in lst:
            if i.online == 1:
                on_line.append([i.label,i.ip_address,i.host_id,i.hv_zone,i.mtu,i.os_version,i.type,addition])
            elif i.online == 0:
                off_line.append([i.label,i.ip_address,i.host_id,i.hv_zone,i.mtu,i.os_version,i.type,addition])
    make_table(bss_list, 1)
    make_table(hvs_list)
    # Different tabels for online and offline CRs
    if len(off_line) > 1:
        print tabulate(on_line+off_line,headers=['label','ip_address','host_id','hv_zone','mtu','os','type',''])
    else:
        print tabulate(on_line,headers=['label','ip_address','host_id','hv_zone','mtu','os','type',''])

def show_ips():
    """
    This function prints ips all HVs and BSs in 'for' cycle format
    """
    lst = bss_list + hvs_list
    hvs_ips,hvs_end,scs_end = [],[],[]
    # Print welcome header in the top
    show_header()
    for i in lst:
        if i.online == 1:
            hvs_ips.append(i.ip_address.split('.'))
    output = []
    def build_str(ips, lvl=0):
        '''
        This function runs in recursion for building structures
        '''
        def grouping(d):
            '''
            This function formats output for last octet
            '''
            d.sort()
            m = [[d[0]]]
            count = 0
            lst = []
            # Checking difference in 1 trough all list
            for x in d[1:]:
                count += 1
                # Grouping them
                if x - 1 == d[count - 1]:
                    m[-1].append(x)
                else:
                    m.append([x])
            # Formatting output for last octet
            for y in m:
                # In case there is more then one value
                if len(y) > 1:
                    lst.append('{' + str(y[0]) + '..' + str(y[-1]) + '}')
                else:
                    lst.append(str(y[0]))
            return lst
        # It runs whern exist ips in list
        while len(ips) > 0:
            tmp = ips[0][lvl]
            buf = []
            # Converting to tuple
            for i in tuple(ips):
                if tmp == i[lvl]:
                    buf.append(i)
                    # Eliminate buffered ip
                    ips.pop(ips.index(i))
            if lvl < 2:
                a = build_str(buf, lvl + 1)
            else:
                ipss = []
                for i in buf:
                    ipss.append(int(i[lvl + 1]))
                # grouping last 4 octet of each ip address
                ipss = grouping(ipss)
                # Formatting with {}
                if len(ipss) > 1:
                    a = i[lvl] + '.' + '{' + ",".join(ipss) + '}'
                else:
                    a = i[lvl] + '.' + str(ipss[0])
                # Adds firtest octets
                output.append((buf[0][0] + '.' + buf[0][1] + '.' + a))
        return " ".join(output)
    # Get sorted and formatted list of management ips
    mgt_ips = build_str(hvs_ips)
    # Print mangement IPs of Hvs and BSs
    print YELLOW+BOLD+'From CP:'+END
    print (YELLOW+ 'Get all CRs :'+END + 'for i in {}; do echo $i; ssh root@$i uptime; done\n'.format(mgt_ips))
    print (YELLOW+ 'Copy to CRs :'+END + 'for i in {}; do echo $i; scp /tmp/ root@$i:/tmp ; done\n'.format(mgt_ips))
    # get last oct for SCs
    for i in hvs_list:
        # Checking if there are some ips of controllers
        if i.online == 1 and i.controlers_count() >= 1:
            for j in range(1,i.controlers_count()+1):
                scs_end.append(str(i.host_id)+ '.' + str(j))
    scs_end.sort()
    scs_string = "{" + ",".join(scs_end) + "}"
    if len(scs_end) > 0:
        if len(bss_list) > 0:
            tmp = bss_list[0].ip_address
        else:
            tmp = hvs_list[0].ip_address
        print (YELLOW+ 'Get all SCs :'+END + 'for i in 10.200.{}; do echo $i; ssh -tt root@{} -tt ssh $ssh_key $i uptime; done\n'.format(scs_string,tmp))
        print (YELLOW+ 'Copy to SCs :'+END + 'for i in 10.200.{}; do echo $i; scp -i ~/.ssh/id_rsa.pub $ssh_key -o ProxyCommand="ssh  -W %h:%p {}" /tmp/ $i:/tmp/; done\n'.format(scs_string,tmp))
        print YELLOW+BOLD+'From HV:'+END
        print (YELLOW+ 'Get all SCs :'+END +  'for i in 10.200.{}; do echo $i; ssh $ssh_key root@$i uptime; done\n'.format(scs_string))
        print ("ssh_key='-o ConnectTimeout=5 -o  ConnectionAttempts=1 -o PasswordAuthentication=no -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o LogLevel=quiet -o CheckHostIP=no'\n")
    else:
        print RED+BOLD+'WARNING: '+END,'No one Storage Controller is avaialble on whole cloud!\n'

def hvs_gener(crs,bss):
    '''
    This function pack exported CRs to objects
    '''
    global hvs_list
    global bss_list
    hvs_list, bss_list = [],[]
    for bs in bss:
        # Check if it's really BS
        if len(bs) == 9:
            temp = BS(bs[0],bs[1],bs[2],bs[3],bs[4],bs[5],bs[6],bs[7],bs[8])
            # Add object to list
            bss_list.append(temp)
        else:
            print BOLD+RED+'It looks you do not have any cloudboot BSs'+END
    for cr in crs:
        # Check if it's really HV
        if len(cr) == 11:
            temp = HV(cr[0],cr[1],cr[2],cr[3],cr[4],cr[5],cr[6],cr[7],cr[8],cr[9],cr[10])
            # Add object to list
            hvs_list.append(temp)
        else:
            print BOLD+RED+'It looks you do not have any cloudboot HVs'+END
    return None

def parse_file():
    '''
    This procedure parses database.yml file
    :return:
    '''
    #raise exections when yml file doesn't exist or no read permissions or has no full range of data
    try:
        if not os.path.exists(DB_CONF_PATH):
            raise IOError(" file doesn't exist")
        elif not os.access(DB_CONF_PATH, os.R_OK):
            raise IOError(" file has no read permissions for current user")
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
                if result[0] == 'username:':
                    user = result[1]
        # If password is quotes then rid out them
        if password.startswith("'") and password.endswith("'") or password.startswith('"') and password.endswith('"'):
            password = password[1:-1]
        if not database and host and password and port and user:
            raise NameError()
    except IOError as e:
        print RED + BOLD + 'WARNING: ', DB_CONF_PATH, str(e) + END
        sys.exit(1)
    except NameError as e:
        print RED + BOLD + 'WARNING: ', str(e) + END
        sys.exit(1)
    def parse_db(password, host='localhost', port=3306, user='root', database='onapp'):
        '''
        This function extract data from mysql
        '''
        try:
            # Establish sql connection to db
            db = MySQLdb.connect(host=host,               # host, usually localhost
                                 port=int(port),          # port, usually 3306
                                 user=user,               # username, usually root
                                 passwd=password,         # password
                                 db=database)             # name of the data base, usually onapp
        # Exception if no connection to mysql
        except MySQLdb.OperationalError as e:
            print RED + BOLD + 'WARNING: ', str(e) + END
            sys.exit(1)
        sql = db.cursor()
        # Get HVs list from database
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
                    "where type = 'Hypervisor::DiskDevice' and status = 1 and hypervisors.mac is not Null "
                    "group by hypervisor_id")
        crs = tuple(sql)
        # Get BSs list from database
        sql.execute("select label, "
                    "ip_address, "
                    "online, "
                    "hypervisor_group_id, "
                    "host, "
                    "host_id, "
                    "mtu, os_version, "
                    "hypervisor_type from hypervisors "
                    "where host_id is not Null and mac is not Null and backup = 1")
        bss = tuple(sql)
        db.close()
        # Make objects
        hvs_gener(crs,bss)
    crs = parse_db(password, host, port, user, database)

def chck_network(zone=None):
    '''
    This function run all needed another checks
    :param zone: If no zone provided, it hecks all CRs
    '''
    lst = []
    show_header()
    # Check if HV Zone is provided
    if zone is not None:
        # Compare HV's zone to provided one
        for hv in hvs_list:
            if int(hv.hv_zone) == zone:
                lst.append(hv)
        lst = bss_list + lst
    else:
        lst = bss_list + hvs_list
    for cr in lst:
        # Run cycle for each single HV/BS
        print (BOLD + YELLOW + '{} : {}  host_id={}'.format(cr.label, cr.ip_address, cr.host_id)) + END
        ping_network(cr, lst, zone)
        chck_nics(cr)
        chck_node(cr)
        # <-- Run network checks here

def ping_network(cr, lst, zone=None):
    """
    Ping check Hvs/BSs with mtu.
    :param zone: Check all BSs and only HVs from same HV zone
    """
    # Ping each frontend IP address
    for dst in lst:
        ping = 'ssh root@' + cr.ip_address + ' \"ping -q -c 10 -i 0.001 -M do -s ' + str(cr.mtu - 28) + ' ' + dst.frontend_ip() + '\"'
        ping_output = subprocess.Popen(['bash','-c', ping], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout, stderr = ping_output.communicate()
        stdout = re.findall(r"[0-9]*\%",str(stdout))
        # All packets lost
        if stdout[0] != '0%':
            print RED + BOLD + 'WARNING: ' + END + stdout[0] +' packets lost', dst.frontend_ip()

def chck_nics(cr):
    '''
    This function check NICs bridged to onappstoresan
    '''
    # Get list of NICs
    command = 'ssh root@' + cr.ip_address
    command2 = command + ' \"ls /sys/class/net/onappstoresan/brif\"'
    nics_output = subprocess.Popen(['bash','-c', command2], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, stderr = nics_output.communicate()
    nics = stdout.split()
    # Get mtu and Rx/Tx errors for each NIC
    for nic in nics:
        command2 = command + ' \"ifconfig {} | egrep \'errors|mtu\'\"'.format(nic)
        nics_output = subprocess.check_call(['bash','-c', command2])
        print nics_output

def chck_node(cr):
    '''
    This function get amount of modes on each HV/BS
    '''
    kill = lambda process: process.kill()
    output = subprocess.Popen(['bash','-c', ('ssh root@{} "onappstore nodes | grep ACTIVE -c"'.format(cr.ip_address))], stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    my_timer = Timer(5, kill, [output])
    try:
        # start timing
        my_timer.start()
        stdout, stderr = output.communicate()
    except subprocess.CalledProcessError:
        output = '0'
    # If stuck, gust kill by timer
    finally:
        my_timer.cancel()
    print 'Amount of Nodes: {}'.format(stdout)

#def omping(zone=None):
   # show_header()
   # lst = bss_list + hvs_list
   # for i in lst:

#ssh 10.76.0.23 "omping -q -c 100  10.200.5.254 10.200.4.254 10.200.3.254"

if __name__ == '__main__':
    parse_file()
    # Use nargs to specify how many arguments an option should take.
    parser = argparse.ArgumentParser(description='ISmonit utility')
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('--ips',  action='store_true')
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--rpms', action='store_true')
    parser.add_argument('-z', '--zone', nargs=1, type=int)
    # Grab the opts from argv
    opts = parser.parse_args()
    if opts.ips:
        show_ips()
    elif opts.list:
        show_list()
    elif opts.rpms:
        show_rpms()
    elif opts.zone:
        chck_network(opts.zone[0])
    else:
        chck_network()