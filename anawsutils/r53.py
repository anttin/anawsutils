import time

import boto3


class Route53(object):
  def __init__(self):
    self.client = boto3.client("route53")


  def list_hosted_zones_by_name(self, domain_name):
    r = self.client.list_hosted_zones_by_name(DNSName=domain_name)
    return r


  def get_hosted_zone_id_by_domain(self, domain_name):
    r = self.list_hosted_zones_by_name(domain_name)

    hzid = None

    if domain_name[-1] == '.':
      _dn = domain_name
    else:
      _dn = domain_name + '.'

    for z in r["HostedZones"]:
      print(z["Name"], _dn)
      if z["Name"] == _dn:
        hzid = z["Id"]
        break

    return hzid


  def update_resource_record(self, hostedzoneid, fqdn, record_type, ttl, value, comment):
    if hostedzoneid is None:
      raise ValueError("HostedZoneId is none")

    if fqdn[-1] == '.':
      _fqdn = fqdn
    else:
      _fqdn = fqdn + '.'

    if record_type == "TXT":
      _value = '"{}"'.format(value)
    else:
      _value = value

    r = self.client.change_resource_record_sets(
      HostedZoneId=hzid,
      ChangeBatch={
        'Comment': comment,
        'Changes': [ {
          'Action': 'UPSERT',
          'ResourceRecordSet': {
            'Name': _fqdn,
            'Type': record_type,
            'TTL':  ttl,
            'ResourceRecords': [{ 'Value': _value }],
          }
        }]
      }
    )
    return r["ChangeInfo"]["Id"]


  def wait_for_dns_update(self, change_id, check_interval=10, max_checks=30):
    checknum = 0
    change_finished_ok = False
    while change_finished_ok is False:
      checknum += 1
      status = self.client.get_change(Id=change_id)["ChangeInfo"]["Status"]
      if status == "INSYNC":
        change_finished_ok = True
        break
      if checknum >= max_checks:
        break
      time.sleep(check_interval)

    return change_finished_ok