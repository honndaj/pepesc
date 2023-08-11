#!/usr/bin/python
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI


class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()


class NetworkTopo(Topo):
    def build(self, **_opts):
        # Add 2 routers in two different subnets
        r1 = self.addHost('r1', cls=LinuxRouter, ip='172.20.35.34/26')
        r2 = self.addHost('r2', cls=LinuxRouter, ip='172.20.35.35/26')

        # Add 2 switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        # Add host-switch links in the same subnet
        self.addLink(s1,
                     r1,
                     intfName2='r1-eth1',
                     params2={'ip': '172.20.35.34/26'})

        self.addLink(s2,
                     r2,
                     intfName2='r2-eth1',
                     params2={'ip': '172.20.35.35/26'})

        # Add router-router link in a new subnet for the router-router connection
        self.addLink(r1,
                     r2,
                     intfName1='r1-eth2',
                     intfName2='r2-eth2',
                     params1={'ip': '172.20.35.91/26'},
                     params2={'ip': '172.20.35.92/26'}, bw=20, delay='300ms', loss=1)

        # Adding hosts specifying the default route
        d1 = self.addHost(name='d1',
                          ip='172.20.35.37/32',
                          defaultRoute='via 172.20.35.34')
        d2 = self.addHost(name='d2',
                          ip='172.20.35.38/32',
                          defaultRoute='via 172.20.35.35')

        # Add host-switch links
        self.addLink(d1, s1)
        self.addLink(d2, s2)


def run():
    topo = NetworkTopo()
    net = Mininet(topo=topo)

    # Add routing for reaching networks that aren't directly connected
    info(net['r1'].cmd("ip route add 172.20.35.38/32 via 172.20.35.92 dev r1-eth2"))
    info(net['r2'].cmd("ip route add 172.20.35.37/32 via 172.20.35.91 dev r2-eth2"))

    net.start()
    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    run()
