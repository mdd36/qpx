import sys

DEFAULT_REQUESTS = 25
APU_URL = "https://www.googleapis.com/qpxExpress/v1/trips/search?key="
HEADER = {'Content-type': 'application/json'}
DAY_START = '00:00'
DAY_END = '23:59'

DEFAULT_REQUEST = {'request': {
            'passengers': {
                'adultCount': 1,
                'childCount': 0,
                'seniorCount': 0
            },
            'slice': [
                {
                    'origin': None,
                    'destination': None,
                    'date': None,
                    'maxConnectionDuration': str(sys.maxsize),
                    'preferredCabin': 'COACH',
                    'permittedCarrier': [],
                    'prohibitedCarrier': [],
                    'permittedDepartTime':
                        {
                            'kind': 'qpxexpress#timeOfDayRange',
                            'earliestTime': DAY_START,
                            'latestTime':  DAY_END
                        },
                    'permittedArrivalTime':
                        {
                            'kind': 'qpxexpress#timeOfDayRange',
                            'earliestTime':DAY_START,
                            'latestTime': DAY_END
                        }

            }],
            'maxPrice': sys.maxsize,
            'solutions': DEFAULT_REQUESTS,
            'refundable': 'false'
            }
        }
