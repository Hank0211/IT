#!/usr/bin/env python3
import subprocess
import json
import sys
import re
#根句柄：（100：）
#默认分类：（100:ffff）
#根分类：（100：1）
#分类：xxx:XYZZ(xxx是上级句柄，X代表第几层，Y代表网段（0-F），ZZ代表IP最后一个数字，这里的数字是16进制数字)
#QDISC:XYZZ(X代表第几层，Y代表网段（0-F），ZZ代表IP最后一个数字，这里的数字是16进制数字)
#
#          ┌───────默认分类（100:ffff）
#          │            
#          │
#          │
#          │
#          │                                         ┌─────────分类：htb（100:3001）───QDISC：sfq（3001:）
#          │                                         │         终端172.16.0.1
#          │                                         │
#          │            ┌──────分类：htb（100:2000）─┼─────────分类：htb（100:3002）───QDISC：sfq（3002:）
#          │            │      （网段172.16.0.x）    │         终端172.16.0.2
#          │            │                            │
#          │            │                            ├─────────......
#          │            │                            │
#          │            │                            └─────────分类：htb（100:30fe）───QDISC：sfq（30fe:）
#          │            │                                      终端172.16.0.254
#          │            │
#          │            │
#          │            │
#          │            │                            ┌─────────分类：htb（100:3101）───QDISC：sfq（3101:）
#          │            │                            │         终端172.16.1.1
#          │            │                            │
#          │            ├──────分类：htb（100:2100）─┼─────────分类：htb（100:3102）───QDISC：sfq（3102:）
#          │            │      （网段172.16.1.x）    │         终端172.16.1.2
#          │            │                            │
#          │            │                            ├─────────......
#          │            │                            │
#          │            │                            └─────────分类：htb（100:31fe）───QDISC：sfq（31fe:）
#          │            │                                      终端172.16.1.254
#          │            │
#          │            │
#          │            │
#          │            │                            ┌─────────分类：htb（100:3201）───QDISC：sfq（3201:）
#          │            │                            │         终端172.16.2.1
#根QDISC：htb（100：）  │                            │
#根分类：htb（100：1）──┼──────分类：htb（100:2200）─┼─────────分类：htb（100:3202）───QDISC：sfq（3202:）
#                       │      （网段172.16.2.x）    │         终端172.16.2.2
#                       │                            │
#                       │                            ├─────────......
#                       │                            │
#                       │                            └─────────分类：htb（100:32fe）───QDISC：sfq（32fe:）
#                       │                                      终端172.16.2.254
#                       │
#                       │
#                       │
#                       │                            ┌─────────分类：htb（100:3301）───QDISC：sfq（3301:）
#                       │                            │         终端172.16.3.1
#                       │                            │
#                       ├──────分类：htb（100:2300）─┼─────────分类：htb（100:3302）───QDISC：sfq（3302:）
#                       │      （网段172.16.3.x）    │         终端172.16.3.2
#                       │                            │
#                       │                            ├─────────......
#                       │                            │
#                       │                            └─────────分类：htb（100:33fe）───QDISC：sfq（33fe:）
#                       │                                      终端172.16.3.254
#                       │
#                       │
#                       │
#                       │                            ┌─────────分类：htb（100:3801）───QDISC：sfq（3801:）
#                       │                            │         终端172.16.8.1
#                       │                            │
#                       ├──────分类：htb（100:2800）─┼─────────分类：htb（100:3802）───QDISC：sfq（3802:）
#                       │      （网段172.16.8.x）    │         终端172.16.8.2
#                       │                            │
#                       │                            ├─────────......
#                       │                            │
#                       │                            └─────────分类：htb（100:38fe）───QDISC：sfq（38fe:）
#                       │                                      终端172.16.8.254
#                       │
#                       │
#                       │
#                       │                            ┌─────────分类：htb（100:3501）───QDISC：sfq（3501:）
#                       │                            │         终端172.16.5.1
#                       │                            │
#                       └──────分类：htb（100:2500）─┼─────────分类：htb（100:3502）───QDISC：sfq（3502:）
#                              （网段172.16.5.x）    │         终端172.16.5.2
#                                                    │
#                                                    ├─────────......
#                                                    │
#                                                    └─────────分类：htb（100:35fe）───QDISC：sfq（35fe:）
#                                                              终端172.16.5.254
#



class NODE():
    def __init__(self, Root_Id:str, Ip_Address:str, speed:str, prio:str)->'''Root_Id="100:1"指明根节点ID, 
                                                                             Ip_Address="172.16.2.11",
                                                                             speed="700kbit", 
                                                                             prio="x,{x|0-7}"''':
        self.__parent_id = Root_Id
        self.__ip = Ip_Address
        self.__class_id = Root_Id.split(':')[0]+ ':' + str(int(Root_Id.split(':')[1][0]) + 1) + hex(int(Ip_Address.split('.')[2]))[2:] + hex(int(Ip_Address.split('.')[3]))[2:].zfill(2)
        self.__handle_id = self.__class_id.split(':')[1]+ ':'
        self.__Speed=speed
        self.__Prio=prio
        
    def setParentId(self, parent_id:str)->"parent_id='X:Y'":
        self.__parent_id=parent_id
        
    def setClassId(self, class_id:str)->"parent_id='X:Y'":
        self.__class_id=class_id
        
    def setHandleId(self, handle_id:str)->"parent_id='X:'":
        self.__handle_id=handle_id
        
    def setSpeed(self, speed:str)->"speed='xxxkbit'":
        self.__Speed=speed
        
    def setPrio(self, prio:str)->"prio='x,{x|0-7}'":
        self.__Prio=prio
        
    def getParentId(self):
        return self.__parent_id
        
    def getIp(self):
        return self.__ip
    
    def getClassId(self):
        return self.__class_id
        
    def getHandleId(self):
        return self.__handle_id
    
    def getSpeed(self):
        return self.__Speed
        
    def getPrio(self):
        return self.__Prio 
        
        
def Tc_Set_Node(node:NODE, ceil:str, leaf:bool)->"node是自定义的类；ceil='12Mbit'ceil是父级流量":
    global ETH_INNER
    global ETH_OUTER
    
    result_inner=subprocess.run(['tc', 'class', 'add', 'dev', ETH_INNER, 'parent', node.getParentId(), 'classid', node.getClassId(), 'htb', 'prio', node.getPrio(), 'rate', node.getSpeed(), 'ceil', ceil, 'quantum','1600'],stdout=subprocess.PIPE, universal_newlines=True)
    if result_inner.returncode !=0 :
        print("Allocate Class Node {0} Error!".format(node.getClassId()))
        exit(1)
        
    if leaf == True:
        result_inner=subprocess.run(['tc', 'qdisc', 'add', 'dev', ETH_INNER, 'parent', node.getClassId(), 'handle', node.getHandleId(), 'sfq', 'perturb', '10'],stdout=subprocess.PIPE, universal_newlines=True)
        if result_inner.returncode !=0 :
            print("(inner)Allocate QDISC Node {0} Error!".format(node.getHandleId()))
            exit(1)        
        
    result_outer=subprocess.run(['tc', 'class', 'add', 'dev', ETH_OUTER, 'parent', node.getParentId(), 'classid', node.getClassId(), 'htb', 'prio', node.getPrio(), 'rate', node.getSpeed(), 'ceil', ceil, 'quantum','1600'],stdout=subprocess.PIPE, universal_newlines=True)
    if result_outer.returncode !=0 :
        print("Allocate Class Node {0} Error!".format(node.getClassId()))
        exit(1)
    if leaf == True:
        result_outer=subprocess.run(['tc', 'qdisc', 'add', 'dev', ETH_OUTER, 'parent', node.getClassId(), 'handle', node.getHandleId(), 'sfq', 'perturb', '10'],stdout=subprocess.PIPE, universal_newlines=True)
        if result_outer.returncode !=0 :
            print("(outer)Allocate QDISC Node {0} Error!".format(node.getHandleId()))
            exit(1)
       
def Tc_Init():
    global ETH_INNER
    global ETH_OUTER
    global TOT_SPEED
    #建立根
    result_inner = subprocess.run(['tc', 'qdisc', 'add', 'dev', ETH_INNER, 'root', 'handle', '100:', 'htb', 'default', 'ffff'], stdout=subprocess.PIPE, universal_newlines=True)
    result_outer = subprocess.run(['tc', 'qdisc', 'add', 'dev', ETH_OUTER, 'root', 'handle', '100:', 'htb', 'default', 'ffff'], stdout=subprocess.PIPE, universal_newlines=True)
    
    if result_inner.returncode !=0 and result_outer.returncode != 0 :
        print("Create Root Qdisc error!")
        exit(1)
        
    #建立HTB总流量
    result_inner = subprocess.run(['tc', 'class', 'add', 'dev', ETH_INNER, 'parent', '100:', 'classid', '100:1', 'htb', 'prio', '0', 'rate', TOT_SPEED, 'ceil', TOT_SPEED, 'quantum','1600'], stdout=subprocess.PIPE, universal_newlines=True)
    result_outer = subprocess.run(['tc', 'class', 'add', 'dev', ETH_OUTER, 'parent', '100:', 'classid', '100:1', 'htb', 'prio', '0', 'rate', TOT_SPEED, 'ceil', TOT_SPEED, 'quantum','1600'], stdout=subprocess.PIPE, universal_newlines=True)
    if result_inner.returncode != 0 and result_outer.returncode !=0 :
        print("Create Root Class error!")
        
    #建立默认组
    result_inner = subprocess.run(['tc', 'class', 'add', 'dev', ETH_INNER, 'parent', '100:', 'classid', '100:ffff', 'htb', 'prio', '7', 'rate', '128kbit', 'ceil', TOT_SPEED],stdout=subprocess.PIPE, universal_newlines=True)
    result_outer = subprocess.run(['tc', 'class', 'add', 'dev', ETH_OUTER, 'parent', '100:', 'classid', '100:ffff', 'htb', 'prio', '7', 'rate', '128kbit', 'ceil', TOT_SPEED],stdout=subprocess.PIPE, universal_newlines=True)
    if result_inner.returncode != 0 and result_outer.returncode !=0 :
        print("Create Default Class error!")
        exit(1)

        
if __name__ == '__main__' :
    #定义内外网卡
    ETH_INNER = 'INNER'
    ETH_OUTER = 'OUTER'
    #总流量
    TOT_SPEED = '65mbit'
    #设置网段信息
    CUR_NETWORK = [NODE('100:1','172.16.0.0','12mbit','2'),
                   NODE('100:1','172.16.1.0','12mbit','2'),
                   NODE('100:1','172.16.2.0','12mbit','2'),
                   NODE('100:1','172.16.3.0','12mbit','2'),
                   NODE('100:1','172.16.8.0','12mbit','2'),
                   NODE('100:1','172.16.5.0','12mbit','2')]

    #设置ip信息
    ip=[ ['' for i in range(254)] for j in CUR_NETWORK ]
    COUNTER=0
    for i in CUR_NETWORK:
        for j in range(254):
            #NODE(Root_Id:str, Ip_Address:str, speed:str, prio:str)
            ip[COUNTER][j]=NODE(i.getClassId(),i.getIp()[:-1]+str(j+1), '700kbit', '4')
        COUNTER+=1
        
    Tc_Init()
    #Tc_Set_Node(NODE类型，Ceil最高速度)
    for i in CUR_NETWORK:
        Tc_Set_Node(i,'65mbit', False)
        
    #Tc_Set_Node(ip[COUNTER][j], '12mbit')
    for i in range(len(CUR_NETWORK)):
        for j in range(254):
            Tc_Set_Node(ip[i][j], '12mbit', True)
            result_inner = subprocess.run(['tc', 'filter', 'add', 'dev', ETH_INNER, 'parent', '100:', 'prio', '2', 'protocol', 'ip', 'u32', 'match', 'ip', 'dst', ip[i][j].getIp() + '/32', 'flowid', ip[i][j].getClassId()],stdout=subprocess.PIPE, universal_newlines=True)
            if result_inner.returncode != 0 :
                print("Allocate Filter Parent id :{0} Error!".format(ip[i][j].getClassId()))
                exit(1)
            result_outer = subprocess.run(['tc', 'filter', 'add', 'dev', ETH_OUTER, 'parent', '100:', 'prio', '2', 'protocol', 'ip', 'u32', 'match', 'ip', 'src', ip[i][j].getIp() + '/32', 'flowid', ip[i][j].getClassId()],stdout=subprocess.PIPE, universal_newlines=True)
            if result_outer.returncode != 0 :
                print("Allocate Filter Parent id :{0} Error!".format(ip[i][j].getClassId()))
                exit(1)
        print("{0} is OK!".format(ip[i][0].getIp()))


