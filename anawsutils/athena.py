import time
import re

import boto3

from pandas.io.json import build_table_schema


class Athena(object):

  DATATYPE_MAP = {
    "integer":  "int",
    "number":   "double",
    "datetime": "timestamp"
  }

  def __init__(
    self,
    dbname,
    workgroup,
    default_query_result_bucket=None,
    default_query_result_path=None
  ):

    self.client    = boto3.client('athena')
    self.dbname    = dbname
    self.workgroup = workgroup
    self.query_result_bucket = default_query_result_bucket
    self.query_result_path   = default_query_result_path


  @classmethod
  def _translate_datatypes(cls, s):
    return cls.DATATYPE_MAP[s] if s in cls.DATATYPE_MAP else s


  @classmethod
  def get_schema(cls, dataframe):
    schema = build_table_schema(dataframe)

    c = {}
    for x in schema['fields']:
      c[x['name']] = cls._translate_datatypes(x['type'])

    return c


  @classmethod
  def get_schema_str(cls, dataframe):
    c = cls.get_schema(dataframe)
    return ', '.join(["{} {}".format(k, v) for k, v in c.items() ])


  def get_s3_url(self, is_path=True, **kwargs):
    if "url" in kwargs:
      result = kwargs["url"]

    elif ("bucket" in kwargs and kwargs["bucket"] is not None and
            "path" in kwargs and kwargs["path"]   is not None):

      result = "s3://{bucket}/{keypath}".format(
        bucket  = kwargs["bucket"],
        keypath = kwargs["path"]
      )

    else:
      if self.query_result_bucket is None or self.query_result_path is None:
        raise Exception("No query result store defined")

      result = "s3://{bucket}/{keypath}".format(
        bucket  = self.query_result_bucket,
        keypath = self.query_result_path
      )

    if is_path is True and result[-1] != '/':
      result += '/'

    if not re.match(r"^s3:\/\/", result):
      result = "s3://" + result

    return result


  def drop_table(self, tablename):
    sql = """
      DROP TABLE IF EXISTS {tbl};   
    """.format(
      tbl = tablename
    )

    return self.execute(sql)


  def create_table(self, tablename, dataframe, pq_bucket, pq_path):
    schema = self.get_schema(dataframe)
    fields = ',\n'.join(["`{}` {}".format(k, v) for k, v in schema.items() ])

    sql = """
      CREATE EXTERNAL TABLE {tbl} (
        {fields}
      )
      ROW FORMAT SERDE 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
      WITH SERDEPROPERTIES (
        'serialization.format' = '1'
      ) LOCATION '{s3url}'
      TBLPROPERTIES ('has_encrypted_data'='false');    
    """.format(
      tbl = tablename,
      fields  = fields,
      s3url   = self.get_s3_url(bucket=pq_bucket, path=pq_path)
    )
    return self.execute(sql)


  def execute(self, sql, bucket=None, path=None, max_iterations=60):

    params = {
      "QueryString": sql,
      "ResultConfiguration": {
        'OutputLocation': self.get_s3_url(bucket=bucket, path=path)
      },
      "QueryExecutionContext": {
        'Database': self.dbname
      },
      "WorkGroup": self.workgroup
    }

    exid = self.client.start_query_execution(**params)

    status = 'RUNNING'
    iterations = max_iterations

    while iterations > 0:
      iterations = iterations - 1
      query_details = self.client.get_query_execution(
        QueryExecutionId = exid['QueryExecutionId']
      )
      status = query_details['QueryExecution']['Status']['State']
      print(status)

      if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:

        result = {
          "location": query_details['QueryExecution']['ResultConfiguration']['OutputLocation'],
          "result_data": None,
          "result_status": None,
          "status": status
        }

        if status == 'SUCCEEDED':
          ## Get output results
          query_result = self.client.get_query_results(
              QueryExecutionId = exid['QueryExecutionId']
          )

          result_status = query_details['QueryExecution']['Status']
          result_data = query_result['ResultSet']

          result["result_status"] = result_status
          result["result_data"] = result_data

        else:
          print(query_details['QueryExecution']['Status']['StateChangeReason'])

        return (status == 'SUCCEEDED'), result

      time.sleep(1)

    raise TimeoutException


class TimeoutException(Exception):
  pass
