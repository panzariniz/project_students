from students import r as redis
import json

def delete_all():
  for key in redis.scan_iter():
    redis.delete(key)

def get_all():
  data = []
  for key in redis.scan_iter():
    data.append(json.loads(redis.get(key).decode('utf-8')))

  return data

"""
Desenvolver um cache simples, em memória, para que não seja necessária uma nova
consulta no banco de dados para os alunos recém-acessados. O cache deverá conter no MÁXIMO
10 itens (ou seja, dados de no máximo 10 alunos). O cache também deverá levar em conta dados
recém-cadastrados. Exemplos de comportamento do cache:
1. O endpoint 5 (Buscar aluno) busca por aluno de ra 123. Em seguida, o mesmo endpoint é
acessado também para o aluno de ra 123. Como esse dado já havia sido buscado no banco
recentemente, a aplicação não deve fazer uma nova leitura no banco mas sim ler do cache;
2. O endpoint 4 (Cadastrar aluno) registra aluno de ra 321. Em seguida o endoint 5 (Buscar aluno) é
acessado para o aluno de 321. Como esse aluno acabou de ser registrado, a aplicação não deve fazer
nova leitura no banco mas sim ler do cache.
O critério de evasão (momento em que um dado deve ser removido da cache para dar lugar a
outro mais recente) fica por sua conta.
"""
def get_student(key):
  cache_data = redis.get(key)
  return None if cache_data is None else json.loads(cache_data.decode('utf-8'))

def auto_increment_cache_student(cache_key, data):
  for key in redis.scan_iter('student_*'):
    cache_data_iter = json.loads(redis.get(key).decode('utf-8'))
    increment = int(cache_data_iter['count'])

    if increment == 10:
      redis.delete(key)
      continue

    cache_data_iter = {**cache_data_iter, **{'count': increment+1}}
    redis.set(key, json.dumps(cache_data_iter))

  redis.set(cache_key, json.dumps({'data': data, 'count': 1}))