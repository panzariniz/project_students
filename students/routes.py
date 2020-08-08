from students import app, collection, cache, http_errors, csv_importer
from flask import request, Response
from bson.json_util import dumps
from datetime import datetime
import uuid

@app.route('/import-students', methods=['POST'])
def import_students():
  return csv_importer.import_students()

""""
1. Listar todos os itens de uma modalidade em um período ordenados por data
  a. Tipo da requisição: GET
  b. Parâmetros: modalidade, data de início e data de fim
  c. Retorno: lista de todos os itens com modalidade, filtrando pelo período
  passado e ordenando de forma decrescente pela data dos
  documentos.
"""
@app.route('/modality/<modality>', methods=['GET'])
def modality(modality):
  queries = request.args.to_dict()
  try:
    start_date = queries['start_date']
    end_date = queries['end_date']
  except KeyError:
    return http_errors.forbidden_error('Query params are not filled')

  try:
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
  except ValueError:
    return http_errors.forbidden_error('Dates are not in correct format')

  query = {
    'modality': modality,
    'start_date': {'$gte': start_date, '$lt': end_date }
  }
  result = collection.find(query).sort('start_date', 1)
  data = []
  for item in result:
    start_date_item = item['start_date'].strftime('%Y-%m-%d')
    data.append({**item, **{'start_date': start_date_item}})

  return Response(dumps({'status': True, 'items': data}), mimetype='application/json')

"""
2. Listar todos os cursos de um campus
  a. Tipo da requisição: GET
  b. Parâmetros: campus
  c. Retorno: lista de cursos do campus
"""
@app.route('/courses/<campus>', methods=['GET'])
def courses(campus):
  pipeline = [
    {'$match': {'campus': campus}},
    {'$group': {'_id': "$course"}}
  ]

  result = collection.aggregate(pipeline)
  data = []
  for item in result:
    data.append(item['_id'])

  return Response(dumps({'status': True, 'items': data}), mimetype='application/json')

"""
3. Descobrir número total de alunos num campus em um dado período
  a. Tipo de requisição: GET
  b. Parâmetros: campus, data de início e data de fim
  c. Retorno: número de alunos do campus no período
"""
@app.route('/total-students', methods=['GET'])
def total_students():
  queries = request.args.to_dict()
  try:
    start_date = queries['start_date']
    end_date = queries['end_date']
  except KeyError:
    return http_errors.forbidden_error('Query params are not filled')

  try:
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
  except ValueError:
    return http_errors.forbidden_error('Dates are not in correct format')

  query = {
    'start_date': {'$gte': start_date, '$lt': end_date }
  }
  count = collection.count_documents(query)
  return Response(dumps({'status': True, 'items': count}), mimetype='application/json')

"""
4. Cadastrar alunos
a. Tipo da requisição: POST
b. Parâmetros: nome, idade_ate_31_12_2016, ra, campus, município, curso, modalidade,
nivel_do_curso, data_inicio
c. Retorno: sucesso/erro
"""
@app.route('/students', methods=['POST'])
def new_student():
  post = request.get_json()
  if post is None or len(post) == 0:
    return http_errors.forbidden_error('Content body is empty')

  required_fields = [
    'name', 'age', 'id',
    'campus', 'city', 'course',
    'modality', 'course_level',
    'start_date'
  ]

  for item in required_fields:
    if item not in post or len(str(post[item])) == 0:
        return http_errors.forbidden_error(f'Required field [{item}] not filled')

  try:
    start_date = datetime.strptime(post['start_date'], '%Y-%m-%d')
  except ValueError:
    return http_errors.unathorized_error('Started date is not a valid date')

  student = collection.find_one({'student_id': int(post['id'])})
  if student:
    return http_errors.unprocessable_entity('Student already registered')

  try:
    unique_id = str(uuid.uuid4())
    student_id = int(post['id'])
    data = {
      '_id': unique_id,
      'name': post['name'].upper(),
      'age': int(post['age']),
      'student_id': student_id,
      'campus': post['campus'].upper(),
      'city': post['city'],
      'course': post['course'],
      'modality': post['modality'],
      'course_level': post['course_level'],
      'start_date': start_date
    }
    collection.insert_one(data)

    data['start_date'] = post['start_date']
    cache.auto_increment_cache_student(f'student_id_{student_id}', data)

    return {
      'status': True,
      'message': 'Success! Student registered',
      'id': unique_id
    }
  except Exception as e:
    return http_errors.internal_server_error(e)
  

"""
5. Buscar aluno
a. Tipo da requisição: GET
b. Parâmetro: ra
c. Retorno: todos os dados do aluno
"""
@app.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
  cache_key = f'student_{student_id}'
  payload = cache.get_student(cache_key)
  if payload:
    print('Cache active')
    return {
      'status': True,
      'data': payload['data']
    }

  student = collection.find_one({'student_id': student_id})
  if student is None:
    return http_errors.not_found('Student not found')    

  start_date = student['start_date'].strftime('%Y-%m-%d')
  data = {**student, **{'start_date': start_date}}

  cache.auto_increment_cache_student(cache_key, data)
  
  return {
    'status': True,
    'data': data
  }

"""
 6. Remover aluno do banco
  a. Tipo da requisição: DELETE
  b. Parâmetros: ra, campus
  c. Retorno: sucesso/erro
"""
@app.route('/students/<int:student_id>/campus/<campus>', methods=['DELETE'])
def remove_student(student_id, campus):
  student = collection.find_one({'student_id': student_id, 'campus': campus})

  if student is None:
    return http_errors.not_found('Student not found')

  collection.delete_one({'_id': student['_id']})
  return {
    'status': True
  }

@app.route('/cache', methods=['GET', 'DELETE'])
def reset_cache():
  if request.method == 'DELETE':
    cache.delete_all()
    return {}

  data = cache.get_all()
  return {
    'count': len(data),
    'data': data
  }
  