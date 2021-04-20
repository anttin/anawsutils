import boto3

from .table import Table

class DDB(object):
  def __init__(self):

    self.dynamodb = boto3.resource('dynamodb')

    self.tables = {}


  def get_table(self, tablename):
    if tablename not in self.tables:
      self.tables[tablename] = Table(tablename, self.dynamodb)
    return self.tables[tablename]


  def get_item(self, ddb_tablename, keyname, key):
    ddb_table = self.get_table(ddb_tablename)
    return ddb_table.get_item(keyname, key)


  def put_item(self, ddb_tablename, item):
    ddb_table = self.get_table(ddb_tablename)
    return ddb_table.put_item(item)


  def delete_item(self, ddb_tablename, keyname, key):
    ddb_table = self.get_table(ddb_tablename)
    return ddb_table.delete_item(keyname, key)
