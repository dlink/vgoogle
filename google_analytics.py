#!/usr/bin/env python

import copy, sys, os

from utils import pretty, validate_num_args

from google_api import GoogleAPI

class GoogleAnalyticsError(Exception): pass

class GoogleAnalytics(object):
    '''Google Analytics Command Line functionality'''


    def process(self, *args):
        '''Process all Incoming Requests
        '''

        args = list(copy.copy(sys.argv[1:]))
        try:
            validate_num_args('google_analytics', 5, args)
        except Exception,e :
            syntax('%s: %s' % (e.__class__.__name__, e))

        dimensions, metrics, filters, start_date, end_date =\
            [x if x else None for x in args]

        print 'Query:'
        print '   dimensions:', dimensions
        print '   metrics   :', metrics
        print '   filters   :', filters
        print '   start_date:', start_date
        print '   end_date  :', end_date
        print

        ga = GoogleAPI('analytics', 'v3')
        results = ga.get(dimensions, metrics, filters, start_date, end_date)
        
        return results

def syntax(emsg=None):

    prog = os.path.basename(sys.argv[0])
    ws = ' '*len(prog)
    if emsg:
        print emsg
                  
    print
    print '  %s <dimensions> <metrics> <filters> <start_date> <end_date>' \
        % prog
    print
    print '  Eq.:'
    print 
    print '      %s ga:date ga:visits,ga:bounces ga:channelGrouping==Direct 2daysAgo 1daysAgo' % prog
    print
    print "      %s ga:date ga:transactions,ga:transactionRevenue '' 2016-11-01 2016-11-07" % prog
    print
    print "      %s ga:country,ga:region,ga:city ga:transactions,ga:transactionRevenue 'ga:channelGrouping==Directga:channelGrouping==Paid Search,ga:channelGrouping==Organic Search' 2daysAgo 1daysAgo" % prog
    print

    sys.exit(1)


if __name__ == '__main__':
    print pretty(GoogleAnalytics().process())
