import telnetlib,argparse,os,paramiko,tarfile


'''端口检测的主要实现过程'''
def getport(ip1,portname):
    # print(ip1,type(ip1),portname,type(portname))
    ip1=ip1.strip()
    portname=int(portname)
    try:
        telnetlib.Telnet(host=ip1, port=portname, timeout=2)
        print('>>>>>{0}   success'.format(ip1))
        return True
    except Exception as e:
        print(e)
        return False

'''sftp 发送文件的主要实现过程'''
def sendfile(username,host,pwd,sf,ef):
    transport = paramiko.Transport((host, 22))
    transport.connect(username=username, password=pwd)
    sftp = paramiko.SFTPClient.from_transport(transport)
    jj=True
    try:
        # sftp.put('node-exporter.tar.gz', '/app/prometheus/exporter/node-exporter.tar.gz')
        # sftp.put('node_exporter.service','/usr/lib/systemd/system/node_exporter.service')
        sftp.put(sf,ef)
    except  IOError  as e:
        jj=False
        print('{0}原文件或者目的文件路径问题:'.format(sf),e)
    except  Exception as  e:
        jj=False
        print('{0}sft传输传输过程出现问题:'.format(ef),e)
    finally:
        sftp.close()
    return jj

'''ssh密码登录的主要实现过程'''
def exe_cmd(username,host,pwd,cmd,key=0):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, port=22, username=username, password=pwd)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    nameid = str(stderr.read()).replace('b', '').replace("'", '')
    stdid=str(stdout.read()).replace('b','').replace("'",'').replace(r'\n','')
    if key:
        return  stdid
    else:
        if nameid:
            # print('______{0}______faile'.format(host))
            return False
        else:
            # print('______{0}______命令执行成功'.format(host))
            return True



'''从文件中得到ip列表并去重的主要过程'''
def  iplist(file):
	f=open(file)
	listda=[]
	for i in f:
		hh=i.strip().replace('\n','')
		if hh :
			listda.append(hh)
	print('___list____')
	print(listda,'\n',len(listda))
	list1=list(set(listda))
	print('___set___')
	print(list1,'\n',len(list1))
	return list1

'''从输入中得到ip列表'''
def   iplist_line(strings):
    str_to_list=strings.strip().strip(':').split(':')
    list_to_set=set(str_to_list)
    getlist=list(list_to_set)
    return getlist



'''批量端口检测的主要过程'''
def port_test(iplist,port):
    name=[]
    print('\n\n')
    for i in iplist:
        print('host  {0} start  ceshi>>>>>>'.format(i))
        getbool=getport(i,port)
        print('主机{0}端口{1}开启结果:{2} '.format(i,port,getbool))
        print('\n')
        if getbool:
            name.append(i)
    print('port-test  is complate')
    print('print iplist:{0}'.format(name))
    print('print NO iplist:{0}'.format(list(set(iplist).difference(set(name)))))



'''批量文件分发接口无论文件夹或者文件通吃'''

def  file1(list_name,username,pwd,sf,ef):
    iplist11=[]
    print('批量传输文件即将开始》》》》》》》》')
    print('\n\n')
    for i in  list_name:
        print('host {0} 传输文件开始'.format(i))
        try:
            if os.path.isfile(sf):
                sendfile(username,i,pwd,sf,ef)
            elif os.path.isdir(sf):
                tarfilename=sf.split('/').pop()
                sendfiletarname = '{0}.tar.gz'.format(tarfilename)
                endfilepath=ef+'/'+sendfiletarname
                cmd_name='tar xvf  {0}  -C {1};rm -rf {2}'.format(endfilepath,ef,endfilepath)

                tar=tarfile.open(sendfiletarname,'w')
                tar.add(sf)
                tar.close()
                sendfile(username, i, pwd,sendfiletarname,endfilepath )
                exe_cmd(username,i,pwd,cmd=cmd_name)
            iplist11.append(i)
            print('{0}传输结果:true'.format(i))
        except Exception as e:
            print('{0}传输结果:false'.format(i))

    return iplist11,list(set(list_name).difference(set(iplist11)))


'''定制化方法一'''
def fun1(filenames,username,pwd,list_name):
    cmd1 = 'ls   {0}|wc  -l'.format(filenames)
    cmd2 = 'mkdir -p /app/prometheus/exporter'
    cmd3 = 'tar zxvf /app/prometheus/exporter/node-exporter.tar.gz -C /app/prometheus/exporter;systemctl  enable node_exporter;systemctl  start node_exporter'
    for i in list_name:
        id = exe_cmd(username, i, pwd, cmd1, key=1)
        print(id, 'id____')
        if int(id):
            print('检测得到{0}存在,将不再进行部署操作'.format(filenames))
        else:
            print('检测到{0}不存在,下面进行端口检测'.format(filenames))
            if getport(i, 9100):
                print('指定主机{0}端口9100被占用,将不再进行下面的操作,sorry!!'.format(i))
            else:
                print('下面将进行部署操作')
                print('creat file {0} is {1}'.format('/app/prometheus/exporter', exe_cmd(username, i, pwd, cmd2)))
                sendfile(username, i, pwd, 'node-exporter.tar.gz', '/app/prometheus/exporter/node-exporter.tar.gz')
                sendfile(username, i, pwd, 'node_exporter.service', '/usr/lib/systemd/system/node_exporter.service')
                print('file 解压以及node-exporter 启动:{0}'.format(exe_cmd(username, i, pwd, cmd3)))

        print('{0} install node-expert  complate'.format(i))
        print('\n\n')

    else:
        pass

'''定制化命令一'''
def  cmd1(list_name,all_cmd,username,pwd):
    listmain = []
    try:
        list1 = eval(all_cmd)
        listmain = list1.copy().copy()
        del list1
    except Exception:
        print('输入的命令参数值错误，请重试')
        exit(1)
    for ip1 in list_name:
        print('正在对{0}主机进行操作'.format(ip1))
        for i in listmain:
            bools = ''
            if i['file']:
                sf, ef = i['file'].strip().strip(':').split(':')
                bools = sendfile(username, ip1, pwd, sf, ef)
            elif i['cmd']:
                bools = exe_cmd(username, ip1, pwd, i['cmd'])
            elif i['port']:
                bools =getport(ip1, i['port'])
            if bools == i['source']:
                continue
            else:
                exit(1)



'''参数的帮助信息的显示'''
def cmd_line():
    parser= argparse.ArgumentParser()
    parser.description = 'this is  a function for  mul_test_port_or_server   power  by zxf'
    parser.add_argument("--format", help="file|cmd_line  select filename use -f  filename;select cmd_line use -c  the string use ':' split;", type=str)
    parser.add_argument("-f", help="filename  path", type=str)
    parser.add_argument("-c", help="like ipname:ipname......", type=str)
    parser.add_argument("-e", help="port|cmd|file|fun",type=str)
    parser.add_argument("--port", help="port ", type=str)
    parser.add_argument("--files", help="sf:ef", type=str)
    parser.add_argument("--filefun", help="file  path,这里是通过检查文件的数量来进行判断", type=str)
    parser.add_argument("--cmd", help="a dirc ", type=str)
    parser.add_argument("--username", help="file  user", type=str)
    parser.add_argument("--passwd", help="file \n passwd", type=str)
    args= parser.parse_args()
    return args



'''在用户不用考虑方式的情况下获取ip列表'''
def all_get_ip_list(args):
    if args.format=='file':
        return iplist(args.f)
    elif args.format=='cmd_line':
        return iplist_line(args.c)


'''主方法的调度'''
def main(args,list_name):
    if args.e=='port':
        portname = args.port
        port_test(list_name,portname)
    elif  args.e=='file':
        filenames=args.files
        username=args.username
        pwd=args.passwd
        sf,ef=filenames.strip().strip(':').split(':')
        sf=sf.rstrip('/')
        ef = ef.rstrip('/')
        listip1,listip2=file1(list_name,username,pwd,sf,ef)
        print('已经成功执行ip列表:',listip1)
        print('未成功执行的ip列表:',listip2)
    elif args.e=='cmd':
        all_cmd=args.cmd
        username = args.username
        pwd = args.passwd
        cmd1(list_name,all_cmd,username,pwd)
    elif  args.e=='fun':
        print('install  prometheus  will  start  >>>>>>>>>>>>>>>>>')
        filenames=args.filefun
        username=args.username
        pwd=args.passwd
        fun1(filenames,username,pwd,list_name)


if  __name__=='__main__':


    args=cmd_line()
    list_name =all_get_ip_list(args)
    main(args,list_name)
    # print(getport('10.141.90.220','22'))
