import boto3


class Table(object):
  def __init__(self, tablename, ddb_resource=None):
    super().__init__()

    self.tablename = tablename

    self.dynamodb = boto3.resource('dynamodb') if ddb_resource is None else ddb_resource
    self.table    = self._get_table(self.dynamodb, self.tablename)


  @staticmethod
  def _get_table(ddb_resource, tablename):
    return ddb_resource.Table(tablename)


  def get_item(self, keyname, key):
    return self._get_item(self.table, keyname, key)


  @staticmethod
  def _get_item(table, keyname, key):
    r = table.get_item(Key={ keyname: key })
    return r['Item'] if 'Item' in r else None


  def put_item(self, item):
    return self._put_item(self.table, item)


  @staticmethod
  def _put_item(table, item):
    return table.put_item(Item=item)


  def delete_item(self, keyname, key):
    return self._delete_item(self.table, keyname, key)


  @staticmethod
  def _delete_item(table, keyname, key):
    return table.delete_item(Key={ keyname: key })


  def query(self, key_condition_expression):
    return self._query(self.table, key_condition_expression)


  @staticmethod
  def _query(table, kce):
    result = []
    response = table.query(KeyConditionExpression=kce)

    for i in response['Items']:
      result.append(i)

    while 'LastEvaluatedKey' in response:
      response = table.query(
        KeyConditionExpression=kce,
        ExclusiveStartKey=response['LastEvaluatedKey']
      )

      for i in response['Items']:
        result.append(i)

    return result


  @staticmethod
  def _count_items_in_batch_queue(queue):
    count = 0
    for tablename in queue.keys():
      count += len(queue[tablename]['Keys'])
    return count


  @staticmethod
  def _get_items_from_batch_queue(queue, max_amount=100):
    _amount = min(max_amount, 100)
    result = {}
    count = 0
    for tablename in queue.keys():
      result[tablename] = { 'Keys': [] }
      while len(queue[tablename]['Keys']) > 0 and count <= _amount:
        x = queue[tablename]['Keys'].pop(0)
        result[tablename]['Keys'].append(x)
        count += 1
      if count == _amount:
        break

    return result


  @classmethod
  def _ddb_batch_get(cls, dynamodb, req):
    result = {}
    unprocessed = { **req }

    while cls._count_items_in_batch_queue(unprocessed) > 0:
      _batch_req = cls._get_items_from_batch_queue(unprocessed)
      response = dynamodb.batch_get_item(RequestItems=_batch_req)

      if 'UnprocessedKeys' in response:
        unprocessed = { **unprocessed, **response['UnprocessedKeys'] }

      result = { **result, **response['Responses'] }

    return result


  def scan(self, fe):
    return self._scan(self.table, fe)


  @staticmethod
  def _scan(table, fe):
    result = []
    response = table.scan(FilterExpression=fe)

    for i in response['Items']:
      result.append(i)

    while 'LastEvaluatedKey' in response:
      response = table.scan(
        FilterExpression=fe,
        ExclusiveStartKey=response['LastEvaluatedKey']
      )

      for i in response['Items']:
        result.append(i)

    return result
