from students import collection, http_errors
import csv
from uuid import uuid4
from datetime import datetime

"""
Utilizando a biblioteca pymongo, crie uma base de dados e uma collection, bem como os
indíces que achar pertinente, contendo os dados do arquivo “dataset_estudantes.csv”. As credenciais
da conexão do banco (host, porta, etc) e o nome da base de dados e da collection deverão ser lidas
de variáveis de ambiente. O formato dos dados no banco de dados fica a seu critério, bem como o
nome das variáveis de ambiente. O código gerado deverá estar em um arquivo import_data.py.
Também solicitamos que nos seja enviado um exemplo do arquivo contendo as variáveis de
ambiente como o nome env_file.env (solicitamos esse arquivo apenas para referência, podendo
inclusive ser o que você usou localmente para testar).
"""
def import_students():
  count_documents = collection.count_documents({})
  if count_documents > 0:
    return http_errors.forbidden_error('You already imported the csv database')

  with open('dataset_estudantes.csv', 'r') as csv_file:
    students_csv = csv.reader(csv_file)

    count_success = 0
    count_error = 0

    header = True
    data = []
    for item in students_csv:
      if header:
          header = False
          continue

      try:
          for column in item:
              if len(column) == 0:
                  raise Exception('Empty column')

          name = item[0]
          age = item[1]
          student_id = item[2]
          campus = item[3]
          city = item[4]
          course = item[5]
          modality = item[6]
          course_level = item[7]
          start_date = item[8]

          data.append({
              '_id': str(uuid4()),
              'name': name.strip(),
              'age': int(float(age)),
              'student_id': int(float(student_id)),
              'campus': campus,
              'city': city.strip(),
              'course': course.strip(),
              'modality': modality.strip(),
              'course_level': course_level.strip().replace('.', ''),
              'start_date': datetime.strptime(start_date, '%Y-%m-%d')
          })

          count_success += 1
      except Exception:
          count_error += 1

    collection.insert_many(data)
    return {
      'status': True,
      'items': {
        'count_success': count_success,
        'count_error': count_error
      }
    }