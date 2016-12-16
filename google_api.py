#!/bin/env python

import httplib2

from googleapiclient import discovery
from oauth2client import client
from oauth2client import file
from oauth2client import tools

from utils import lazyproperty

class GoogleAPI(object):
    '''Preside over Google API'''

    max_records = 10000

    def __init__(self, name, version):
        '''Constructor
             name    - api service name
             version - api service version

             eq. ga = GoogleAPI('analytics', 'v3')
        '''
        self.name = name
        self.version = version

    def get(self, dimensions, metrics, filters, start_date, end_date):
        '''Call Google API for given parameters
           make multiple calls in blocks of self.max_records

           Return a table as a list of lists.
              Columns = dimension values, then metrics values

           eq.:
                from google_api import GoogleAPI
                self.ga = GoogleAPI('analytics', 'v3')

                results = self.ga.get2(
                    dimensions=\
                        'ga:date,ga:country,ga:region,ga:city,ga:hour,' \
                        'ga:minute,ga:daysSinceLastVisit',
                    metrics=\
                        'ga:sessions,' \
                        'ga:bounces,' \
                        'ga:sessionDuration',
                    filters=\
                        'ga:channelGrouping==Direct,' \
                        'ga:channelGrouping==Paid Search,' \
                        'ga:channelGrouping==Organic Search',
                    start_date='2016-11-03',
                    end_date='2016-11-03')
        '''

        # header
        header = dimensions.split(',')
        header += metrics.split(',')
        
        data = [header]
        more_records = True
        start_index = 1

        while more_records:
            results = self.service.data().ga().get(
                ids='ga:%s' % self.config.profile_id,

                metrics=metrics,
                dimensions=dimensions,
                filters=filters,

                start_date=start_date,
                end_date=end_date,
                sort=dimensions,
                max_results=self.max_records,
                start_index=start_index

                ).execute()

            # move rows into data:
            rows = results.get('rows', [])
            data += rows

            # get another block of rows?
            if len(rows) == self.max_records:
                start_index += self.max_records
            else:
                more_records = False

        return data

    @lazyproperty
    def service(self):
        '''Authenticate and return service connection
           Storage object writes credentials to file.
        '''

        storage = file.Storage('analytics.dat')
        credentials = storage.get()

        if credentials is None or credentials.invalid:
            credentials = tools.run_flow(self.flow, storage)

        http = credentials.authorize(http = httplib2.Http())
        service = discovery.build(self.name, self.version, http=http)
        return service

    @lazyproperty
    def flow(self):
        '''Setup and return Flow Object
           only needed for first time auth
        '''
        client_secrets = self.config.client_json
        scope='https://www.googleapis.com/auth/analytics.readonly'
        flow = client.flow_from_clientsecrets(
            client_secrets,
            scope=scope,
            message=tools.message_if_missing(client_secrets))
        return flow

    @lazyproperty
    def config(self):
        try:
            return __import__('config')
        except ImportError, e:
            print
            print "Problem: Can not find config.py!"
            print "  You need to copy config_template.py to config.py"
            print "  And then update its values"
            print
            import sys
            sys.exit(1)

if __name__ == '__main__':
    ga = GoogleAPI('analytics', 'v3')
    results = ga.get(
        metrics='ga:visits,ga:goal6Completions',
        dimensions='ga:channelGrouping',
        filters=None,
        start_date='7daysAgo',
        end_date='yesterday')

    for row in results:
        print row
