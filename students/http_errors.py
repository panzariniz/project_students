def unathorized_error(message):
  return json_error(message, 401)

def forbidden_error(message):
  return json_error(message, 403)

def not_found(message):
  return json_error(message, 404)

def unprocessable_entity(message):
  return json_error(message, 422)

def internal_server_error(error):
  return {
    'status': False,
    'message': 'Internal Server Error',
    'error': str(error)
  }, 500

def json_error(message, code):
  return {
    'status': False,
    'message': message
  }, code