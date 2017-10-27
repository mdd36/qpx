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
        self._url = constants.api_url + self._get_api_key()

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
        self._url = constants.api_url + api_key

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
    def make_request(self, arrive, depart, date, adultcount=str(1), childcount=str(0), seniorcount=str(0),
                     earliestdepart = '00:00', latestdepart = '23:59', earliestarrive='00:00', latestarrive='23:59',
                     maxprice='1000000', solutions='25', permittedcarriers=[], forbiddencarriers=[],
                     refundable=False, preferredcabin='coach', maxstops=100, maxconndur=240):
        self._package_request(**locals())
        return self._send_requests()

    def _get_api_key(self):
        key_location = os.path.join(self.data_path)
        with open(key_location, 'r') as key_file:
            return key_file.readline()

    def _package_request(self, param_dict):
        self.request = {'request': {
            'passengers': {
                'adultCount': param_dict['adultcount'],
                'childCount': param_dict['childcount'],
                'seniorCount': param_dict['senoircount']
            },
            'slice': [
                {
                    'origin': param_dict['depart'],
                    'destination': param_dict['arrive'],
                    'date': param_dict['date'],
                    'maxConnectionDuration': param_dict['maxconntdur'],
                    'preferredCabin': param_dict['preferredcabin'].upper(),
                    'permittedCarrier': param_dict['permittedcarriers'],
                    'prohibitedCarrier': param_dict['forbiddenCarriers'],
                    'permittedDepartTime':
                        {
                            'kind': 'qpxexpress#timeOfDayRange',
                            'earliestTime': param_dict['earliestdepart'],
                            'latestTime':  param_dict['latestdepart']
                        },
                    'permittedArrivalTime':
                        {
                            'kind': 'qpxexpress#timeOfDayRange',
                            'earliestTime': param_dict['earliestarrive'],
                            'latestTime': param_dict['latestarrive']
                        }

            }],
            'maxPrice': param_dict['maxprice'],
            'solutions': param_dict['solutions'],
            'refundable': param_dict['solutions']
            }
        }

    def _send_requests(self):
        response = self._package_response()
        ret = {}
        for trip in range(len(response)):
            ret[trip] = {}
            for temp in response['trips']['tripOption']:
                self._add_root_data(ret, temp, trip)
                self._create_data_lists(ret, trip)
                for __slice in temp['slice']:
                    for segment in __slice['segment']:
                        self._add_flight_data(ret, segment, trip)
        return ret

    def _package_response(self):
        x = requests.post(self._url, data=json.dumps(self.request), headers=constants.header)
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