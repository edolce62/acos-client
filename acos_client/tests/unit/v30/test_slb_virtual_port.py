# Copyright 2014,  Doug Wiegley,  A10 Networks.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import absolute_import
from __future__ import unicode_literals

try:
    import unittest
    from unittest import mock
except ImportError:
    import mock
    import unittest2 as unittest

from acos_client import client
import acos_client.errors as acos_errors
import json
import responses


HOSTNAME = 'fake_a10'
BASE_URL = 'https://{}:443/axapi/v3'.format(HOSTNAME)
AUTH_URL = '{}/auth'.format(BASE_URL)
VSERVER_NAME = 'test'
CREATE_URL = '{}/slb/virtual-server/{}/port/'.format(BASE_URL, VSERVER_NAME)
OBJECT_URL = '{}/slb/virtual-server/{}/port/80+http'.format(BASE_URL, VSERVER_NAME)
ALL_URL = '{}/slb/virtual-server/{}/port/'.format(BASE_URL, VSERVER_NAME)


class TestVirtualPort(unittest.TestCase):

    def setUp(self):
        self.client = client.Client(HOSTNAME, '30', 'fake_username', 'fake_password')
        self.maxDiff = None

    @responses.activate
    def test_virtual_port_create_no_params(self):
        responses.add(responses.POST, AUTH_URL, json={'session_id': 'foobar'})
        json_response = {'response': {'status': 'OK'}}
        responses.add(responses.POST, CREATE_URL, json=json_response, status=200)
        params = {
            'port':
            {
                'extended-stats': 1,
                'name': 'test1_VPORT',
                'port-number': 80,
                'protocol': 'http',
                'service-group': 'pool1'
            }
        }

        resp = self.client.slb.virtual_server.vport.create(
            VSERVER_NAME, 'test1_VPORT', protocol=self.client.slb.virtual_server.vport.HTTP, port='80',
            service_group_name='pool1'
        )

        self.assertEqual(resp, json_response)
        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(responses.calls[1].request.method, responses.POST)
        self.assertEqual(responses.calls[1].request.url, CREATE_URL)
        self.assertEqual(json.loads(responses.calls[1].request.body), params)

    @responses.activate
    def test_virtual_port_create_with_params(self):
        responses.add(responses.POST, AUTH_URL, json={'session_id': 'foobar'})
        json_response = {'response': {'status': 'OK'}}
        responses.add(responses.POST, CREATE_URL, json=json_response, status=200)
        params = {
            'port':
            {
                'auto': 1,
                'extended-stats': 1,
                'ipinip': 1,
                'name': 'test1_VPORT',
                'pool': 'test_nat_pool',
                'port-number': 80,
                'protocol': 'http',
                'service-group': 'pool1',
                'ha-conn-mirror': 1,
                'no-dest-nat': 1,
                'conn-limit': 50000,
                'tcp_template': 'test_tcp_template',
                'template-persist-cookie': 'test_c_pers_template',
                'template-persist-source-ip': 'test_s_pers_template',
                'udp_template': 'test_udp_template'
            }
        }

        resp = self.client.slb.virtual_server.vport.create(
            virtual_server_name=VSERVER_NAME,
            name='test1_VPORT',
            protocol=self.client.slb.virtual_server.vport.HTTP,
            port='80',
            service_group_name='pool1',
            s_pers_name="test_s_pers_template",
            c_pers_name="test_c_pers_template",
            ha_conn_mirror=1,
            no_dest_nat=1,
            conn_limit=50000,
            status=1,
            autosnat=True,
            ipinip=True,
            source_nat_pool="test_nat_pool",
            tcp_template="test_tcp_template",
            udp_template="test_udp_template",
        )

        self.assertEqual(resp, json_response)
        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(responses.calls[1].request.method, responses.POST)
        self.assertEqual(responses.calls[1].request.url, CREATE_URL)
        self.assertEqual(json.loads(responses.calls[1].request.body), params)

    @responses.activate
    def test_virtual_port_create_already_exists(self):
        responses.add(responses.POST, AUTH_URL, json={'session_id': 'foobar'})
        json_response = {
            "response": {"status": "fail", "err": {"code": 1406, "msg": "The virtual port already exists."}}
        }
        responses.add(responses.POST, CREATE_URL, json=json_response, status=200)

        with self.assertRaises(acos_errors.ACOSException):
            self.client.slb.virtual_server.vport.create(
                VSERVER_NAME, 'test1_VPORT', protocol=self.client.slb.virtual_server.vport.HTTP, port='80',
                service_group_name='pool1'
            )

        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(responses.calls[1].request.method, responses.POST)
        self.assertEqual(responses.calls[1].request.url, CREATE_URL)

    @mock.patch('acos_client.v30.slb.virtual_port.VirtualPort.get')
    @responses.activate
    def test_virtual_port_update_no_params(self, mocked_get):
        mocked_get.return_value = {"foo": "bar"}
        responses.add(responses.POST, AUTH_URL, json={'session_id': 'foobar'})
        json_response = {"foo": "bar"}
        responses.add(responses.POST, OBJECT_URL, json=json_response, status=200)
        params = {
            "port":
            {
                "name": "test1_VPORT",
                "service-group": "pool1",
                "protocol": "http",
                "port-number": 80,
                "template-persist-source-ip": None,
                "template-persist-cookie": None,
                "extended-stats": 1,
                "no-dest-nat": 0
            }
        }

        resp = self.client.slb.virtual_server.vport.update(
            VSERVER_NAME, 'test1_VPORT', protocol=self.client.slb.virtual_server.vport.HTTP, port='80',
            service_group_name='pool1'
        )

        self.assertEqual(resp, json_response)
        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(responses.calls[1].request.method, responses.POST)
        self.assertEqual(responses.calls[1].request.url, OBJECT_URL)
        self.assertEqual(json.loads(responses.calls[1].request.body), params)

    @mock.patch('acos_client.v30.slb.virtual_port.VirtualPort.get')
    @responses.activate
    def test_virtual_port_create_with_templates(self, mocked_get):
        responses.add(responses.POST, AUTH_URL, json={'session_id': 'foobar'})
        json_response = {'response': {'status': 'OK'}}
        responses.add(responses.POST, CREATE_URL, json=json_response, status=200)
        protocol = self.client.slb.virtual_server.vport.HTTP
        if protocol.lower() == 'http':
            params = {
                'port':
                {
                    'auto': 1,
                    'extended-stats': 1,
                    'ipinip': 1,
                    'name': 'test1_VPORT',
                    'pool': 'test_nat_pool',
                    'port-number': 80,
                    'protocol': 'http',
                    'service-group': 'pool1',
                    'tcp_template': 'test_tcp_template',
                    'template-persist-cookie': 'test_c_pers_template',
                    'template-persist-source-ip': 'test_s_pers_template',
                    'udp_template': 'test_udp_template',
                    'template-virtual-port': 'template_vp',
                    'template-http': None,
                    'template-policy': 'template_pl',
                }
            }
        else:
            params = {
                'port':
                {
                    'auto': 1,
                    'extended-stats': 1,
                    'ipinip': 1,
                    'name': 'test1_VPORT',
                    'pool': 'test_nat_pool',
                    'port-number': 80,
                    'protocol': 'http',
                    'service-group': 'pool1',
                    'tcp_template': 'test_tcp_template',
                    'template-persist-cookie': 'test_c_pers_template',
                    'template-persist-source-ip': 'test_s_pers_template',
                    'udp_template': 'test_udp_template',
                    'template-virtual-port': 'template_vp',
                    'template-tcp': 'template_tcp',
                    'template-policy': 'template_pl',
                }
            }

        resp = self.client.slb.virtual_server.vport.create(
            virtual_server_name=VSERVER_NAME,
            name='test1_VPORT',
            protocol=self.client.slb.virtual_server.vport.HTTP,
            port='80',
            service_group_name='pool1',
            s_pers_name="test_s_pers_template",
            c_pers_name="test_c_pers_template",
            status=1,
            autosnat=True,
            ipinip=True,
            source_nat_pool="test_nat_pool",
            tcp_template="test_tcp_template",
            udp_template="test_udp_template",
            virtual_port_templates={
                'template-virtual-port': 'template_vp',
                'template-tcp': 'template_tcp',
                'template-policy': 'template_pl',
            },
        )

        self.assertEqual(resp, json_response)
        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(responses.calls[1].request.method, responses.POST)
        self.assertEqual(responses.calls[1].request.url, CREATE_URL)
        self.assertEqual(json.loads(responses.calls[1].request.body), params)

    @mock.patch('acos_client.v30.slb.virtual_port.VirtualPort.get')
    @responses.activate
    def test_virtual_port_create_with_partial_templates(self, mocked_get):
        responses.add(responses.POST, AUTH_URL, json={'session_id': 'foobar'})
        json_response = {'response': {'status': 'OK'}}
        responses.add(responses.POST, CREATE_URL, json=json_response, status=200)
        protocol = self.client.slb.virtual_server.vport.HTTP
        if protocol.lower() == 'http':
            params = {
                'port':
                {
                    'auto': 1,
                    'extended-stats': 1,
                    'ipinip': 1,
                    'name': 'test1_VPORT',
                    'pool': 'test_nat_pool',
                    'port-number': 80,
                    'protocol': 'http',
                    'service-group': 'pool1',
                    'tcp_template': 'test_tcp_template',
                    'template-persist-cookie': 'test_c_pers_template',
                    'template-persist-source-ip': 'test_s_pers_template',
                    'udp_template': 'test_udp_template',
                    'template-virtual-port': 'template_vp',
                    'template-http': None,
                    'template-policy': None,
                }
            }
        else:
            params = {
                'port':
                {
                    'auto': 1,
                    'extended-stats': 1,
                    'ipinip': 1,
                    'name': 'test1_VPORT',
                    'pool': 'test_nat_pool',
                    'port-number': 80,
                    'protocol': 'http',
                    'service-group': 'pool1',
                    'tcp_template': 'test_tcp_template',
                    'template-persist-cookie': 'test_c_pers_template',
                    'template-persist-source-ip': 'test_s_pers_template',
                    'udp_template': 'test_udp_template',
                    'template-virtual-port': 'template_vp',
                    'template-tcp': None,
                    'template-policy': None,
                }
            }

        resp = self.client.slb.virtual_server.vport.create(
            virtual_server_name=VSERVER_NAME,
            name='test1_VPORT',
            protocol=self.client.slb.virtual_server.vport.HTTP,
            port='80',
            service_group_name='pool1',
            s_pers_name="test_s_pers_template",
            c_pers_name="test_c_pers_template",
            status=1,
            autosnat=True,
            ipinip=True,
            source_nat_pool="test_nat_pool",
            tcp_template="test_tcp_template",
            udp_template="test_udp_template",
            virtual_port_templates={
                'template-virtual-port': 'template_vp'
            },
        )

        self.assertEqual(resp, json_response)
        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(responses.calls[1].request.method, responses.POST)
        self.assertEqual(responses.calls[1].request.url, CREATE_URL)
        self.assertEqual(json.loads(responses.calls[1].request.body), params)

    @mock.patch('acos_client.v30.slb.virtual_port.VirtualPort.get')
    @responses.activate
    def test_virtual_port_update_with_params(self, mocked_get):
        mocked_get.return_value = {"foo": "bar"}
        responses.add(responses.POST, AUTH_URL, json={'session_id': 'foobar'})
        json_response = {"foo": "bar"}
        responses.add(responses.POST, OBJECT_URL, json=json_response, status=200)
        params = {
            'port':
            {
                'auto': 1,
                'extended-stats': 1,
                'name': 'test1_VPORT',
                'no-dest-nat': 1,
                'pool': 'test_nat_pool',
                'port-number': 80,
                'protocol': 'http',
                'service-group': 'pool1',
                'ha-conn-mirror': 1,
                'conn-limit': 50000,
                'tcp_template': 'test_tcp_template',
                'template-persist-cookie': 'test_c_pers_template',
                'template-persist-source-ip': 'test_s_pers_template',
                'udp_template': 'test_udp_template'
            }
        }

        resp = self.client.slb.virtual_server.vport.update(
            virtual_server_name=VSERVER_NAME,
            name='test1_VPORT',
            protocol=self.client.slb.virtual_server.vport.HTTP,
            port='80',
            service_group_name='pool1',
            s_pers_name="test_s_pers_template",
            c_pers_name="test_c_pers_template",
            status=1,
            autosnat=True,
            ipinip=True,
            ha_conn_mirror=1,
            no_dest_nat=0,
            conn_limit=50000,
            source_nat_pool="test_nat_pool",
            tcp_template="test_tcp_template",
            udp_template="test_udp_template",
        )
        self.assertEqual(resp, json_response)
        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(responses.calls[1].request.method, responses.POST)
        self.assertEqual(responses.calls[1].request.url, OBJECT_URL)
        self.assertEqual(json.loads(responses.calls[1].request.body), params)

    @mock.patch('acos_client.v30.slb.virtual_port.VirtualPort.get')
    @responses.activate
    def test_virtual_port_update_with_templates(self, mocked_get):
        mocked_get.return_value = {"foo": "bar"}
        responses.add(responses.POST, AUTH_URL, json={'session_id': 'foobar'})
        json_response = {"foo": "bar"}
        responses.add(responses.POST, OBJECT_URL, json=json_response, status=200)
        protocol = self.client.slb.virtual_server.vport.HTTP
        if protocol.lower() == 'http':
            params = {
                'port':
                {
                    'auto': 1,
                    'extended-stats': 1,
                    'name': 'test1_VPORT',
                    'no-dest-nat': 1,
                    'pool': 'test_nat_pool',
                    'port-number': 80,
                    'protocol': 'http',
                    'service-group': 'pool1',
                    'ha-conn-mirror': 1,
                    'conn-limit': 50000,
                    'tcp_template': 'test_tcp_template',
                    'template-persist-cookie': 'test_c_pers_template',
                    'template-persist-source-ip': 'test_s_pers_template',
                    'udp_template': 'test_udp_template',
                    'template-virtual-port': 'template_vp',
                    'template-http': None,
                    'template-policy': None,
                }
            }
        else:
            params = {
                'port':
                {
                    'auto': 1,
                    'extended-stats': 1,
                    'name': 'test1_VPORT',
                    'no-dest-nat': 1,
                    'pool': 'test_nat_pool',
                    'port-number': 80,
                    'protocol': 'http',
                    'service-group': 'pool1',
                    'ha-conn-mirror': 1,
                    'conn-limit': 50000,
                    'tcp_template': 'test_tcp_template',
                    'template-persist-cookie': 'test_c_pers_template',
                    'template-persist-source-ip': 'test_s_pers_template',
                    'udp_template': 'test_udp_template',
                    'template-virtual-port': 'template_vp',
                    'template-tcp': None,
                    'template-policy': None,
                }
            }
        resp = self.client.slb.virtual_server.vport.update(
            virtual_server_name=VSERVER_NAME,
            name='test1_VPORT',
            protocol=self.client.slb.virtual_server.vport.HTTP,
            port='80',
            service_group_name='pool1',
            s_pers_name="test_s_pers_template",
            c_pers_name="test_c_pers_template",
            status=1,
            autosnat=True,
            ipinip=True,
            ha_conn_mirror=1,
            no_dest_nat=0,
            conn_limit=50000,
            source_nat_pool="test_nat_pool",
            tcp_template="test_tcp_template",
            udp_template="test_udp_template",
            virtual_port_templates={
                'template-virtual-port': 'template_vp'
            },
        )
        self.assertEqual(resp, json_response)
        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(responses.calls[1].request.method, responses.POST)
        self.assertEqual(responses.calls[1].request.url, OBJECT_URL)
        self.assertEqual(json.loads(responses.calls[1].request.body), params)

    @responses.activate
    def test_virtual_port_delete(self):
        responses.add(responses.POST, AUTH_URL, json={'session_id': 'foobar'})
        json_response = {
            'response': {'status': 'OK'}
        }
        responses.add(responses.DELETE, OBJECT_URL, json=json_response, status=200)

        resp = self.client.slb.virtual_server.vport.delete(
            VSERVER_NAME, 'test1_VPORT', self.client.slb.virtual_server.vport.HTTP, '80'
        )

        self.assertEqual(resp, json_response)
        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(responses.calls[1].request.method, responses.DELETE)
        self.assertEqual(responses.calls[1].request.url, OBJECT_URL)

    @responses.activate
    def test_virtual_port_delete_not_found(self):
        responses.add(responses.POST, AUTH_URL, json={'session_id': 'foobar'})
        json_response = {
            "response": {"status": "fail", "err": {"code": 1043, "msg": "Can not find the virtual server port"}}
        }
        responses.add(responses.DELETE, OBJECT_URL, json=json_response, status=200)

        with self.assertRaises(acos_errors.ACOSException):
            self.client.slb.virtual_server.vport.delete(
                VSERVER_NAME, 'test1_VPORT', self.client.slb.virtual_server.vport.HTTP, '80'
            )

        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(responses.calls[1].request.method, responses.DELETE)
        self.assertEqual(responses.calls[1].request.url, OBJECT_URL)

    @responses.activate
    def test_virtual_port_search(self):
        responses.add(responses.POST, AUTH_URL, json={'session_id': 'foobar'})
        json_response = {"foo": "bar"}
        responses.add(responses.GET, OBJECT_URL, json=json_response, status=200)

        resp = self.client.slb.virtual_server.vport.get(
            VSERVER_NAME, 'test1_VPORT', protocol=self.client.slb.virtual_server.vport.HTTP, port='80'
        )

        self.assertEqual(resp, json_response)
        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(responses.calls[1].request.method, responses.GET)
        self.assertEqual(responses.calls[1].request.url, OBJECT_URL)

    @responses.activate
    def test_virtual_port_search_not_found(self):
        responses.add(responses.POST, AUTH_URL, json={'session_id': 'foobar'})
        json_response = {
            "response": {"status": "fail", "err": {"code": 1043, "msg": "Can not find the virtual server port"}}
        }
        responses.add(responses.GET, OBJECT_URL, json=json_response, status=200)

        with self.assertRaises(acos_errors.ACOSException):
            self.client.slb.virtual_server.vport.get(
                VSERVER_NAME, 'test1_VPORT', protocol=self.client.slb.virtual_server.vport.HTTP, port='80'
            )

        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(responses.calls[1].request.method, responses.GET)
        self.assertEqual(responses.calls[1].request.url, OBJECT_URL)

    @responses.activate
    def test_virtual_port_all(self):
        responses.add(responses.POST, AUTH_URL, json={'session_id': 'foobar'})
        json_response = {"foo": "bar"}
        responses.add(responses.GET, ALL_URL, json=json_response, status=200)

        resp = self.client.slb.virtual_server.vport.all(VSERVER_NAME)

        self.assertEqual(resp, json_response)
        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(responses.calls[1].request.method, responses.GET)
        self.assertEqual(responses.calls[1].request.url, ALL_URL)
