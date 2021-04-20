import boto3
from .. import tools


class EC2Flavors(object):
  def __init__(self):
    super().__init__()

    self.ec2_client = boto3.client('ec2')


  def get_ec2_regions(self):
    j = self.ec2_client.describe_regions()
    return [region['RegionName'] for region in j['Regions']]


  @staticmethod
  def _get_ec2_instance_types(client):
    describe_args = {}
    result = {}
    while True:
      describe_result = client.describe_instance_types(**describe_args)
      for i in describe_result['InstanceTypes']:
        result[i['InstanceType']] = i
      if 'NextToken' not in describe_result:
        break
      describe_args['NextToken'] = describe_result['NextToken']

    return result


  def get_data(self, regions=None):
    if regions is None:
      _regions = self.get_ec2_regions()
    else:
      _regions = regions

    data = []
    for region in _regions:
      c = boto3.client('ec2', region_name=region)
      r = self._get_ec2_instance_types(c)
      for v in r.values():
        _v = tools.flatten_dict(v)
        _v["Region"] = region
        data.append(_v)

    return data
