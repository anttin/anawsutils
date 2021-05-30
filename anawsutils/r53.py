import time

import boto3


class Route53(object):
  def __init__(self):
    self.client = boto3.client("route53")
    self.hostedzones = {}


  @staticmethod
  def _ensure_trailing_dot(s):
    if s is None or not isinstance(s, str) or len(s) < 1:
      raise ValueError("Invalid domain name")
    elif s[-1] == '.':
      return s
    else:
      return s + '.'    


  def list_hosted_zones_by_name(self, domain_name):
    r = self.client.list_hosted_zones_by_name(DNSName=domain_name)
    return r


  def get_hosted_zone_id_by_domain(self, domain_name, cache=True):
    _dn = self._ensure_trailing_dot(domain_name)

    if cache is True and _dn in self.hostedzones:
      return self.hostedzones[_dn]

    r = self.list_hosted_zones_by_name(_dn)

    hzid = None

    for z in r["HostedZones"]:
      if cache is True and z["Name"] not in self.hostedzones:
        self.hostedzones[z["Name"]] = z["Id"]
      if z["Name"] == _dn:
        hzid = z["Id"]
        break

    return hzid


  def _modify_resource_record(self, action, hostedzoneid, fqdn, record_type, ttl, value, comment):
    if hostedzoneid is None:
      raise ValueError("HostedZoneId is none")

    _fqdn = self._ensure_trailing_dot(fqdn)

    if record_type == "TXT":
      _value = '"{}"'.format(value)
    else:
      _value = value

    changebatch = {
          'Comment': comment,
          'Changes': [ {
            'Action': action,
            'ResourceRecordSet': {
              'Name': _fqdn,
              'Type': record_type.upper(),
              'TTL':  ttl,
              'ResourceRecords': [{ 'Value': _value }],
            }
          }]
    }

    r = self.client.change_resource_record_sets(
      HostedZoneId=hostedzoneid,
      ChangeBatch=changebatch
    )

    return r


  def update_resource_record(self, hostedzoneid, fqdn, record_type, ttl, value, comment):  
    r = self._modify_resource_record('UPSERT', hostedzoneid, fqdn, record_type, ttl, value, comment)
    return r["ChangeInfo"]["Id"]


  def delete_resource_record(self, hostedzoneid, fqdn, record_type, ttl, value, comment):
    r = self._modify_resource_record('DELETE', hostedzoneid, fqdn, record_type, ttl, value, comment)
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


  def get_resource_record(self, hostedzoneid, fqdn, record_type):
    _fqdn = self._ensure_trailing_dot(fqdn)

    r = self.client.list_resource_record_sets(
      HostedZoneId=hostedzoneid,
      StartRecordName=_fqdn,
      StartRecordType=record_type.upper(),
      MaxItems="1"
    )

    if r["ResourceRecordSets"][0]["Name"] == _fqdn and r["ResourceRecordSets"][0]["Type"] == record_type.upper():
      return r["ResourceRecordSets"][0]
    else:
      return None