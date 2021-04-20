import time

from datetime import datetime, date

import boto3


class CE(object):
  def __init__(self, credentials=None):
    super().__init__()

    self.credentials = credentials

    c = credentials.get() if credentials is not None else {}
    self.ce_client = boto3.client('ce', **c)


  @staticmethod
  def _get_start_end(period_str):
    dt = datetime.strptime(period_str, '%m/%Y')
    year, month, day = dt.timetuple()[:3]
    return dt, date(year + int(month / 12), ((month+1) % 12) or 12, day)


  def get_month(self, period_str):
    dt_start, dt_end = self._get_start_end(period_str)
    timeperiod = {
      'Start': dt_start.strftime('%Y-%m-%d'),
      'End':   dt_end.strftime('%Y-%m-%d')
    }

    req = {
      'TimePeriod': timeperiod,
      'Dimension': 'LINKED_ACCOUNT',
      'Context':  'COST_AND_USAGE'
    }

    data_dims = []
    while True:
      response = self.ce_client.get_dimension_values(**req)
      data_dims = data_dims + response["DimensionValues"]
      if 'NextPageToken' in response:
        req['NextPageToken'] = response['NextPageToken']
      else:
        break
      # throttle a bit
      time.sleep(0.5)

    linkedaccounts = [ x["Value"] for x in data_dims ]

    req = {
      'TimePeriod': timeperiod,
      'Granularity': 'MONTHLY',
      'Filter': {
        'Dimensions': {
          'Key': 'LINKED_ACCOUNT',
          'Values': []
        }
      },
      'Metrics': [ 'UnblendedCost' ]
    }

    data_cu = {}
    for account in linkedaccounts:
      req['Filter']['Dimensions']['Values'] = [ account ]
      response = self.ce_client.get_cost_and_usage(**req)
      v = None
      for x in response['ResultsByTime']:
        w = x['Total']['UnblendedCost']['Amount']
        v = w if v is None else v + w
      data_cu[account] = v
      # throttle a bit
      time.sleep(0.5)

    return data_cu
        