import boto3

class SES(object):
  def __init__(self, region):
    super().__init__()

    self.region = region

    self.client = boto3.client('ses', region_name=self.region)


  def send_raw_email(self, raw):
    response = self.client.send_raw_email(RawMessage={ 'Data': raw })
    return response


  def send_email(self, sender, recipients, subject, body_text, body_html, charset="UTF-8"):
    if isinstance(recipients, list) is False:
      recipients = [recipients]

    return self.client.send_email(
      Destination={
          'ToAddresses': recipients,
      },
      Message={
          'Body': {
              'Html': {
                  'Charset': charset,
                  'Data': body_html,
              },
              'Text': {
                  'Charset': charset,
                  'Data': body_text,
              },
          },
          'Subject': {
              'Charset': charset,
              'Data': subject,
          },
      },
      Source=sender
    )
