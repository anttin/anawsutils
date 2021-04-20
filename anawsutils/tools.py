import json
import os

from collections.abc import MutableMapping


def _get_env(key, default=None):
  return os.environ[key] if key in os.environ else default


def get_env(env_var_name, default_value = None, required = False):
  result = _get_env(env_var_name, default_value)

  if required is True and result is default_value:
    raise Exception("Mandatory environment variable missing: " + env_var_name)

  return result


def check_lambda_event_params(event, required_params=None, optional_params=None):
  def init_param(param):
    if param is None:
      return []
    if isinstance(param, (list, tuple)):
      return param
    return [ param ]

  required = init_param(required_params)
  optional = init_param(optional_params)
  missing  = []
  params   = {}

  for x in required:
    if x not in event.keys():
      missing.append(x)

  if len(missing) > 0:
    Exception("Parameter values missing from request: " + ', '.join(missing))

  params = { **event }

  for x in optional:
    if x not in params.keys():
      params[x] = None

  return params


def has_no_dicts(lst):
  for item in lst:
    if isinstance(item, MutableMapping):
      return False
    elif isinstance(item, (tuple, list)):
      r = has_no_dicts(item)
      if r is False:
        return r
  return True


def flatten_dict(d, parent_key='', sep='_'):
  items = []
  for k, v in d.items():
    new_key = parent_key + sep + k if parent_key else k
    if v and isinstance(v, MutableMapping):
      items.extend(flatten_dict(v, new_key, sep=sep).items())
    elif v and isinstance(v, (list, tuple)):
      if has_no_dicts(v):
        items.append((new_key, json.dumps(v)))
      else:
        for i in range(0, len(v)): # pylint: disable=consider-using-enumerate
          _new_key = new_key + sep + str(i)
          if v[i] and isinstance(v[i], MutableMapping):
            items.extend(flatten_dict(v[i], _new_key, sep=sep).items())
          else:
            items.append((_new_key, v[i]))
    else:
      items.append((new_key, v))
  return dict(items)
