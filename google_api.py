#!/bin/env python

import os
import httplib2

from googleapiclient import discovery
from oauth2client import client
from oauth2client import file
from oauth2client import tools

from vlib import conf
from utils import lazyproperty

BACKWARD_COMPAT = 0
BACKWARD_COMPAT_MAP = {'ga:sessions': 'ga:visits',
                       'ga:sessionDuration': 'ga:timeOnSite',
                       'ga:bounces': 'ga:bounce'}

class GoogleAPI(object):
    '''Preside over Google API'''

    max_records = 10000

    def __init__(self, name, version, backward_compat=BACKWARD_COMPAT):
        '''Constructor
             name    - api service name
             version - api service version

             eq. ga = GoogleAPI('analytics', 'v3')
        '''
        self.conf = conf.getInstance()
        self.name = name
        self.version = version
        self.backward_compat = backward_compat

    @lazyproperty
    def profile_id(self):
        '''Return Google Account Profile Id'''
        return self.conf.google_analytics.profile_id

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
        client_secrets = '%s/config/googleanalytics/client.json' \
            % self.conf.base_dir
        scope='https://www.googleapis.com/auth/analytics.readonly'
        flow = client.flow_from_clientsecrets(
            client_secrets,
            scope=scope,
            message=tools.message_if_missing(client_secrets))
        return flow

    def get2(self, dimensions, metrics, filters, start_date, end_date):
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
        if self.backward_compat:
            header2 = []
            for h in header:
                header2.append(BACKWARD_COMPAT_MAP.get(h, h))
            header = header2
        
        data = [header]
        more_records = True
        start_index = 1

        while more_records:
            results = self.service.data().ga().get(
                ids='ga:%s' % self.profile_id,

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

    def get(self, metric, start_date, end_date, filters=None, start_index=1,
            dimensions=None):
        '''DEPRECATED: see get2()'''

        # add ga: prefix to dimensions
        ga_dimensions = []
        if dimensions:
            for d in dimensions.split(','):
                ga_dimensions.append('ga:%s' % d)

        results = self.service.data().ga().get(
            ids='ga:%s' % self.profile_id,
            metrics='ga:%s' % metric,
            dimensions=','.join(ga_dimensions),
            max_results=self.max_records,
            start_date=start_date,
            end_date=end_date,
            filters=filters,
            sort=','.join(ga_dimensions),
            start_index=start_index

            # other possible parameters
            #sort='-ga:visits',
            #filters='ga:medium==organic',
            #start_index='1'
            #max_results='25'

            ).execute()

        data = []
        for row in results.get('rows', []):
            data.append(row)
        return data

if __name__ == '__main__':
    ga = GoogleAPI('analytics', 'v3')
    #results = ga.get(metric='internalPromotionClicks',
    #                 dimensions='internalPromotionPosition',
    #                 start_date='300daysAgo',
    #                 end_date='yesterday')
    '''
    results = ga.get(#metric='internalPromotionClicks',
        #metric='transactions',
        metric='transactionRevenue',
        dimensions='date,internalPromotionPosition',
        start_date='1daysAgo',
        end_date='yesterday')
        '''
    #dimensions='date,country,region,city,hour,minute,daysSinceLastVisit',

    """
    results = ga.get(
        metric='visits,ga:timeOnSite',
        #metric='bounces',
        #metric='timeOnSite',
        #dimensions='date,country,region,city,hour,minute,daysSinceLastVisit',
        dimensions='date,channelGrouping',
        filters='ga:channelGrouping==Direct,ga:channelGrouping==Paid Search,ga:channelGrouping==Organic Search',
        start_date='1daysAgo',
        end_date='yesterday')
        """
    results = ga.get2(
        metrics='ga:visits,ga:goal6Completions',
        dimensions='ga:channelGrouping',
        filters=None,
        start_date='7daysAgo',
        end_date='yesterday')

    for row in results:
        print row
