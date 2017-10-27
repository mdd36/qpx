#!/usr/bin/env python3
__author__ = "Matthew Dickson"
__license__ = "MIT"
__version__ = "0.8"

import os
import json
import requests
from QPXError import QPXException
import constants

class QPX:

    """
    Create a QPX request object
    @:type data_path: String
    @:param absolute path to json file containing api key and credentials
    """
    def __init__(self, data_path):
        self.data_path = data_path
        self.set_key(self._get_api_key())

    """
    Create a QPX object with a string for the API key
    @:type api_key: String
    @:param api_key: API key to use for all requests until it gets refined
    """
    def __init__(self, api_key):
        self.set_key(api_key)

    """
    Set the API to be used for future requests
    @:type api_key: String
    @:param api_key: API key to use for all requests until it gets refined
    """
    def set_key(self, api_key):
        self._url = constants.APU_URL + api_key

    """
    Make a request of the Google Flights API with the API key of this object.
    @type arrive: String
    @param arrive: Three letter airport code of the destination city, ie SAN, JFK, ORD
    
    @type depart: String
    @param depart: Three letter airport code of the originating city, ie SAN, JFK, ORD
    
    @type date: String 
    @param date: Date the flight is leaving, must be formatted like 'YYYY-MM-DD'
    
    @rtype: Dictionary
    @return: Desirable information sliced out of the received json file, namely ticket price, departure times,
             airlines used, airports used, and flight codes
    """
    def make_request(self, arrive, depart, date, **kwargs):
        self.response = {}
        self._package_request(**locals())
        self._send_requests()
        return self.response

    def _get_api_key(self):
        key_location = os.path.join(self.data_path)
        with open(key_location, 'r') as key_file:
            return key_file.readline()

    def _package_request(self, param_dict):
        self.request = constants.DEFAULT_REQUEST
        for key in param_dict.keys():
            if key in requests:
                self.request[key] = param_dict[key]

    def _send_requests(self):
        reply = self._package_response()
        for trip in range(len(reply)):
            self.response[trip] = {}
            self._add_trip_info(reply, trip)

    def _add_trip_info(self, reply, trip):
        for temp in reply['trips']['tripOption']:
            self._add_root_data(self.response, temp, trip)
            self._create_data_lists(self.response, trip)
            self._add_slice_data(temp, trip)

    def _add_slice_data(self, temp, trip):
        for __slice in temp['slice']:
            for segment in __slice['segment']:
                self._add_flight_data(self.response, segment, trip)

    def _package_response(self):
        x = requests.post(self._url, data=json.dumps(self.request), headers=constants.HEADER)
        if x is not None:
            response = x.json()
            if response.__contains__('Error'):
                raise QPXException("Returned value has errors: are the request fields valid?")
            del response['kind']
            return response

    def _add_flight_data(self, ret, segment, trip):
        ret[trip]['flight_code'].append(segment['flight']['carrier'] + segment['flight']['number'])
        leg = segment['leg'][0]
        ret[trip]['airports'].extend([leg['origin'], leg['destination']])
        ret[trip]['depart_times'].append(leg['departureTime'])

    def _create_data_lists(self, ret, trip):
        ret[trip]['flight_code'] = []
        ret[trip]['airports'] = []
        ret[trip]['depart_times'] = []

    def _add_root_data(self, ret, temp, trip):
        ret[trip]['id'] = temp['id']
        ret[trip]['total'] = temp['saleTotal']