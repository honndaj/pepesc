#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.link import TCLink

"""
  node name     |     node A             node B                       node C             node D
eth1 address    |    10.0.0.1 --------- 10.0.0.2                     10.0.2.3 --------- 10.0.2.4
eth2 address    |                       10.0.1.2 ------------------- 10.0.1.3
Link conditions |                                 20Mbps, 300ms, 1%
"""

h1_eth0 = '10.0.0.1/24'
r1_eth0 = '10.0.0.2/24'
r1_eth1 = '10.0.1.2/24'
r2_eth0 = '10.0.2.3/24'
r2_eth1 = '10.0.1.3/24'
h2_eth0 = '10.0.2.4/24'

class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

class NetworkTopo(Topo):
    def build(self, **_opts):
        h1 = self.addHost(name='h1', ip=h1_eth0, defaultRoute='via 10.0.0.2')
        h2 = self.addHost(name='h2', ip=h2_eth0, defaultRoute='via 10.0.2.3')
        r1 = self.addHost('r1', cls=LinuxRouter, ip=r1_eth0)
        r2 = self.addHost('r2', cls=LinuxRouter, ip=r2_eth0)

        self.addLink(h1,
                     r1,
                     intfName1='h1-eth0',
                     intfName2='r1-eth0',
                     params1={'ip':h1_eth0},
                     params2={'ip':r1_eth0})
        
        self.addLink(h2,
                     r2,
                     intfName1='h2-eth0',
                     intfName2='r2-eth0',
                     params1={'ip':h2_eth0},
                     params2={'ip':r2_eth0})

        self.addLink(r1,
                     r2,
                     cls=TCLink,
                     bw=20,
                     delay='300ms',
                     loss=1,
                     intfName1='r1-eth1',
                     intfName2='r2-eth1',
                     params1={'ip':r1_eth1},
                     params2={'ip':r2_eth1})
        


         


def run():
    topo = NetworkTopo()
    net = Mininet(topo=topo)

    # Add routing for reaching networks that aren't directly connected
    info(net['r1'].cmd("ip route add 10.0.2.0/24 via 10.0.1.3 dev r1-eth1"))
    info(net['r2'].cmd("ip route add 10.0.0.0/24 via 10.0.1.2 dev r2-eth1"))

    net.start()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
