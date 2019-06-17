#!/usr/bin/python3
import json
import requests
from time import time
import urllib3
urllib3.disable_warnings()
from ansible.module_utils.pstools.config import Config

class SolidfireUtilError(Exception):
    pass

class SolidFireRawUtil:
    """
    Util class to abstract the details of working with the raw SolidFire API.

    Args:
        host: The hostname or IP of the Solidfire Node API.
        username: Username to use for API connection.
        password: Password to use for API connection.
        version: Minimum API version needed.
        port: SolidFire Cluster API port.
    """

    def __init__(self, host: str, username: str='', password: str='', version: float=Config.SF_API_VERSION, port: int=442):
        print("Connecting to SolidFire Element Raw API")
        self._host = host
        self._version = version
        self._port = port
        self._base_url = "https://" + self._host + ":" + str(self._port) + "/json-rpc/" + str(self._version)
        self._auth = username, password
        self._headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    def _make_url_with_method(self, method: str):
        """str: The URL to the API with the method query param set"""
        return "{}?method={}".format(self._base_url, method)

    def _requests_get(self, method: str, **kwargs) -> dict:
        """Generate a url with the given method to use requests.get and return the response

        Args:
            method (str): Name of the SolidFire API method to call
            kwargs (str): Any query parameters to use when calling the API

        Raises:
            SolidfireUtilError: If the HTTP status code is 404,
                which should mean that the self._version is unsupported by the cluster.
            SolidfireUtilError: If the HTTP status code is not 200.

        Returns:
            dict: The JSON parsed response from the API

        """
        url = self._make_url_with_method(method)

        print("SolidFire raw API HTTP GET {} params={}".format(url, kwargs))
        start_time = time()
        res = requests.get(url, params=kwargs, verify=False, timeout=30, auth=self._auth)
        duration = time() - start_time
        print("Method '{}' took {:0.2f} seconds and returned status code {}".format(method, duration, res.status_code))

        if res.status_code == 404:
            raise SolidfireUtilError("SolidFire cluster does not support API {}".format(self._base_url))

        if not res.status_code == 200:
            msg = 'Unexpected HTTP status code {} connecting to SolidFire API: {}'.format(res.status_code, res.text)
            raise SolidfireUtilError(msg)

        return res.json()

    def get_service_tag(self) -> str:
        """Get the service tag (serial number) of an HCI node

        Returns:
            str: The service tag

        Raises:

        """
        response = self._requests_get("GetHardwareInfo")
        try:
            serial = response["result"]["hardwareInfo"]["serial"]
            return serial
        except Exception as e:
            return None

    def test_ping(self, host, interface="Bond1G", packetSize=1500) -> str:
        """Test ICMP from one node to another

        Returns:
            str: The time for the response or an error

        Raises:

        """
        response = self._requests_get("TestPing", hosts=host, attempts=1, interface=interface)
        if "error" in response:
            result = response["error"]["name"]
            time = -1.0
        else:
            results = response["result"]["details"][host]
            time = results["individualResponseTimes"][0]
            result = results["individualResponseCodes"][0]
        return result, time


