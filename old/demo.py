#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import TCLink

class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class NetworkTopo(Topo):
    def build(self, **_opts):
        d1 = self.addHost(name='d1',
                          ip='10.0.0.251/24',
                          defaultRoute='via 10.0.0.1')
        d2 = self.addHost(name='d2',
                          ip='10.1.0.252/24',
                          defaultRoute='via 10.1.0.1')
        r1 = self.addHost('r1', cls=LinuxRouter, ip='10.0.0.1/24')
        r2 = self.addHost('r2', cls=LinuxRouter, ip='10.1.0.1/24')

        self.addLink(d1,
                     r1,
                     intfName1='d1-eth1',
                     intfName2='r1-eth1',
                     params1={'ip':'10.0.0.251/24'},
                     params2={'ip':'10.0.0.1/24'})
        self.addLink(d2,
                     r2,
                     intfName1='d2-eth1',
                     inftName2='r2-eth1',
                     params1={'ip':'10.1.0.252/24'},
                     params2={'ip':'10.1.0.1/24'})

        self.addLink(r1,
                     r2,
                     cls=TCLink,
                     delay='300ms',
                     intfName1='r1-eth2',
                     intfName2='r2-eth2',
                     params1={'ip': '10.100.0.1/24'},
                     params2={'ip': '10.100.0.2/24'})


def run():
    topo = NetworkTopo()
    net = Mininet(topo=topo)

    # Add routing for reaching networks that aren't directly connected
    info(net['r1'].cmd("ip route add 10.1.0.0/24 via 10.100.0.2 dev r1-eth2"))
    info(net['r2'].cmd("ip route add 10.0.0.0/24 via 10.100.0.1 dev r2-eth2"))

    net.start()

    """ r1 = net.getNodeByName('r1')
    print(r1.intfs)
    for intf in r1.intfs.values():
        print(intf.IP()) """

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
