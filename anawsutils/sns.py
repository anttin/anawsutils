import boto3

class SNS(object):
  def __init__(self):
    super().__init__()

    self.client = boto3.client('sns')


  def send_sns(self, arn, subject, message):
    response = self.client.publish(
      TopicArn=arn,
      Message=message,
      Subject=subject
    )
    return response
