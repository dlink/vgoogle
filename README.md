vgoogle

Command Line Google Analytics Reporting

This project came out of the need to pull Google Analytics data for data warehouse reporting.    It consists of

**A Python GoogleAPI class**

* Which uses Google's *googleapiclient* python library

* Provides python inteface

* *get(metric, start_date, end_date, filters, start_index)*


* Loops thru multiple pages of 10000 records if necessary to get around the 10000 max record limit.

**A google_analytics.py command line interface**

* Exposes the python interfact to the command line

Syntax:

    google_analytics.py <dimensions> <metrics> <filters> <start_date> <end_date>

Examples:

      google_analytics.py ga:date ga:visits,ga:bounces ga:channelGrouping==Direct 2daysAgo 1daysAgo

      google_analytics.py ga:date ga:transactions,ga:transactionRevenue '' 2016-11-01 2016-11-07

      google_analytics.py ga:country,ga:region,ga:city ga:transactions,ga:transactionRevenue 'ga:channelGrouping==Directga:channelGrouping==Paid Search,ga:channelGrouping==Organic Search' 2daysAgo 1daysAgo
