#!/usr/bin/env python 
# -*- coding:utf-8 -*-
# update 2018/08/28 shel
import commands
import time
import os, sys, time
import datetime
import platform
import subprocess
import math


def get_disk_info(warn):
    a = commands.getstatusoutput('df -h | grep dev | egrep -v "tmp|var|shm"')
    all_disk_info = {}
    for disk in a[1].split('\n'):
        if "Permission" in disk:
            continue
        info = disk.split(' ')
        percent, path = info[-2], info[-1]
        percent_int = int(percent.split('%')[0])
        if percent_int >= int(warn):
            all_disk_info[path] = percent
    return all_disk_info


def empty_today_logs(path, warn):
    a = commands.getstatusoutput('find /data -maxdepth 3 -name "*.log.*" -mtime -1')
    for path in a[1].split("\n"):
        empty_log = commands.getstatusoutput("echo > %s" % path)
    if get_disk_info(warn).keys():
        # rmi_images()
        print
        "begin..."
        if get_disk_info(warn).keys():
            clear_file()
            # print "2"
            if get_disk_info(warn).keys():
                # print "3"
                b = commands.getstatusoutput('find /data -maxdepth 3 -name "*.log" -mtime -1')
                for _path in b[1].split("\n"):
                    _empty_log = commands.getstatusoutput("echo > %s" % _path)
            else:
                pass
        else:
            pass


def clean_nginx():
    b = commands.getstatusoutput('find /nginx/upload/*/* -type f -mtime -1 -exec rm {} \;')
    c = commands.getstatusoutput('find /nginx/download/*.log -type f -mmin +30 -exec rm -rf {} \;')


def clean_file(path, warn):
    if path == '/nginx':
        clean_nginx()
    commands.getstatusoutput('find %s -maxdepth 4 -name "*.log" -mtime +0 -exec rm -rf {} \;' % path)
    commands.getstatusoutput('find %s -maxdepth 4 -name "*.out" -mtime +0 -exec rm -rf {} \;' % path)
    commands.getstatusoutput('find %s -maxdepth 4 -name "*.log.*" -mtime +0 -exec rm -rf {} \;' % path)
    # commands.getstatusoutput('find %s -maxdepth 4 -name "*message*" -mtime +0 -exec rm -rf {} \;'%path)
    if get_disk_info(warn).keys():
        empty_today_logs(path, warn)
    time.sleep(2)


def rmi_images():
    commands.getstatusoutput("docker rmi $(docker images -qa)")


def GetFileList(dirpath, fileList):
    newDir = dirpath
    if os.path.isfile(dirpath):
        fileList.append(dirpath.decode('gbk'))
    elif os.path.isdir(dirpath):
        for s in os.listdir(dirpath):
            # if s == "xxx":
            # continue
            newDir = os.path.join(dirpath, s)
            GetFileList(newDir, fileList)
    return fileList


def fileSize():
    is_linux = platform.system() == 'Linux'
    list2 = []
    list3 = []
    filePath = []
    list1 = GetFileList('/data/logs', [])
    ts = time.strftime("%Y-%m-%d-%H", time.localtime())
    for e in list1:
        list2.append(e)
    for i in list2:
        # filetime = os.path.getmtime(i)
        filetime = (datetime.datetime.fromtimestamp(os.path.getmtime(i))).strftime("%Y-%m-%d-%H")
        if filetime == ts:
            list3.append(i)
    for m in list3:
        cmd_ = 'du -sh {}'.format(m)
        # print cmd_
        p = subprocess.Popen(cmd_, stderr=subprocess.STDOUT, stdout=subprocess.PIPE,
                             shell=True, preexec_fn=os.setsid if is_linux else None)
        filesize = p.stdout.read().strip().split('\t')[0]
        tsize = filesize[:-1].split('.')[0]
        if 'G' in filesize and int(tsize) > 1:
            filePath.append(m)
        time.sleep(0.5)
        while True:
            if p.poll() is not None:
                break
    if filePath:
        return filePath
    else:
        return False


def clear_file():
    filepath_ = fileSize()
    if filepath_ == 'False':
        pass
    else:
        for i in filepath_:
            commands.getstatusoutput("echo > %s" % i)


if __name__ == '__main__':
    warn, critical = 90, 95
    disk_info = get_disk_info(warn)
    if disk_info.keys():
        for disk in disk_info.keys():
            clean_file(disk, warn)
            # print "---being clean---auto clean logs,please follow"
            if get_disk_info(warn).keys():
                print
                "Please check,You should clean disk manually:%s" % disk_info
                sys.exit(2)
            else:
                print
                "please follow,---being clean---auto clean %s logs!" % disk_info
                sys.exit(2)
    else:
        print
        "All disk space are OK"
        sys.exit(0)