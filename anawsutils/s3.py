import boto3

from botocore.exceptions import ClientError


class S3(object):
  def __init__(self):
    super().__init__()

    self.s3_client = boto3.client('s3')


  def upload_file(self, local_filename, bucket, object_key, catch_exceptions=True):
    if catch_exceptions is True:
      try:
        response = self.s3_client.upload_file(local_filename, bucket, object_key)
      except ClientError:
        return False
      return True
    response = self.s3_client.upload_file(local_filename, bucket, object_key)
    return response


  def get_obj(self, bucket, key, client_params=None):
    _client_params = {} if client_params is None else client_params
    return self.s3_client.get_object(Bucket=bucket, Key=key, **_client_params)


  def get_file(self, bucket, key, client_params=None):
    _client_params = {} if client_params is None else client_params
    obj = self.get_obj(bucket, key, _client_params)
    return obj['Body'].read()


  def get_string(self, bucket, key, client_params=None):
    _client_params = {} if client_params is None else client_params
    return self.get_file(bucket, key, _client_params).decode('utf-8')


  def put_data(self, bucket, key, data, client_params=None):
    _client_params = {} if client_params is None else client_params
    self.s3_client.put_object(
      Body=data,
      Bucket=bucket,
      Key=key,
      **_client_params
    )


  @staticmethod
  def get_bucket_and_key_from_url(url):
    a = url.split('/')
    return a[2], '/'.join(a[3:])


  def create_presigned_url(self, bucket_name, object_key, expiration_seconds = 900):
    try:
      response = self.s3_client.generate_presigned_url(
        'get_object',
        Params = {
          'Bucket': bucket_name,
          'Key':    object_key
        },
        ExpiresIn = expiration_seconds
      )
    except ClientError:
      return None

    # The response contains the presigned URL
    return response
