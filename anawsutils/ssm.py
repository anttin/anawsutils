
import boto3


class SSM(object):
  def __init__(self):
    self.client = boto3.client("ssm")


  def _put_parameter(self, name, value, paramtype="String", keyid=None, tier="Intelligent-Tiering", overwrite=True):
    kw = {
      "Name":      name,
      "Value":     value,
      "Type":      paramtype,
      "Overwrite": overwrite,
      "Tier":      tier,
      "DataType":  "text"
    }

    if keyid is not None:
      kw["KeyId"] = keyid

    response = self.client.put_parameter(**kw)
    return response


  def put_parameter(self, name, value, paramtype="String", tier="Intelligent-Tiering", overwrite=True):
    return self._put_parameter(
      name,
      value,
      paramtype=paramtype,
      tier=tier,
      overwrite=overwrite
    )


  def put_secure_parameter(self, name, value, keyid, tier="Intelligent-Tiering", overwrite=True):
    return self._put_parameter(
      name,
      value,
      paramtype="SecureString",
      keyid=keyid,
      tier=tier,
      overwrite=overwrite
    )
    return response


  def _get_parameter(self, name, decrypt):
    return self.client.get_parameter(Name=name, WithDecryption=decrypt)


  def get_parameter(self, name):
    r = self._get_parameter(name, False)
    return r["Value"]


  def get_secure_parameter(self, name):
    r = self._get_parameter(name, True)
    return r["Value"]