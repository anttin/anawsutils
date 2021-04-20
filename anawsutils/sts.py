import boto3

class STS(object):
  def __init__(self):
    super().__init__()

    self.sts_client = boto3.client('sts')
    self._assumed_roles = {}


  def assume_role(self, role_arn, session_name):
    assumed_role_object = self.sts_client.assume_role(
      RoleArn         = role_arn,
      RoleSessionName = session_name
    )

    self._assumed_roles["session_name"] = assumed_role_object

    return Credentials(assumed_role_object['Credentials'])


class Credentials(object):
  def __init__(self, credential_dict):
    super().__init__()

    self.creds = {
      "aws_access_key_id":     credential_dict['AccessKeyId'],
      "aws_secret_access_key": credential_dict['SecretAccessKey'],
      "aws_session_token":     credential_dict['SessionToken']
    }

  def get(self):
    return self.creds
