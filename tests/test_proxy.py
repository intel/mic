#!/usr/bin/python

import unittest
from mic.utils import proxy

def suite():
    return unittest.makeSuite(ProxyTest)

class ProxyTest(unittest.TestCase):

    def test_proxy(self):
        proxy.set_proxies('http://proxy.some.com:11', '1.2.3.4')
        self.assertEqual(proxy.get_proxy_for('http://1.2.3.4'), None)
        self.assertEqual(proxy.get_proxy_for('http://download.tizen.org'), 'http://proxy.some.com:11')

        proxy.set_proxies('http://proxy.some.com:11', 'download.am.org')
        self.assertEqual(proxy.get_proxy_for('http://download.am.org'), None)
        self.assertEqual(proxy.get_proxy_for('https://download.am.org'), None)
        self.assertEqual(proxy.get_proxy_for('http://download.tizen.org'), 'http://proxy.some.com:11')

        proxy.set_proxies('http://proxy.some.com:11', '1.2.3.0/24')
        self.assertEqual(proxy.get_proxy_for('http://1.2.3.4'), None)
        self.assertEqual(proxy.get_proxy_for('http://1.2.3.0'), None)
        self.assertEqual(proxy.get_proxy_for('http://1.2.3.255'), None)
        self.assertEqual(proxy.get_proxy_for('http://download.tizen.org'), 'http://proxy.some.com:11')

        proxy.set_proxies('http://proxy.some.com:11', '.hello.com')
        self.assertEqual(proxy.get_proxy_for('http://linux.hello.com'), None)
        self.assertEqual(proxy.get_proxy_for('http://linux.hello.com.org'), 'http://proxy.some.com:11')



if __name__ == "__main__":
    unittest.main()
