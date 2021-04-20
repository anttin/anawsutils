import json

import boto3


class Secretsmanager(object):
  def __init__(self):
    super().__init__()
    self.client = self._get_client()


  def get_secret(self, secret_arn, **kwargs):
    j = self._get_secret(self.client, secret_arn, **kwargs)
    return json.loads(j)


  def get_value(self, secret_arn, key):
    r = self.get_secret(secret_arn)
    return r[key] if key in r else None


  @staticmethod
  def _get_secret(client, secret_arn, version_stage="AWSCURRENT", version_id=None):
    req = {
      "SecretId":     secret_arn,
      "VersionStage": version_stage
    }

    if version_id is not None:
      req["VersionId"] = version_id

    response = client.get_secret_value(**req)
    return response["SecretString"]


  def _get_client(self):
    return boto3.client('secretsmanager')
    