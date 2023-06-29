# pip install flask
# pip install flask-mysqldb !!!o de baixo é melhor
# pip install mysql-connector-python
# flask doc: https://flask.palletsprojects.com/en/2.3.x/
# endpoint criado: http://localhost:5000
# pra rodar só ir no cmd onde está esse arquivo ,py e dá um 'python api_endpoint.py'

from flask import Flask, json, render_template, request
import mysql.connector
import json


api = Flask(__name__)
db = mysql.connector.connect(
    host='127.0.0.1',   
    user='root',
    passwd='root',
    db='sade', 
    port=3306
)


@api.route('/usuarios', methods = ['GET'])
def usuario():
    cursor = db.cursor(dictionary=True)
    cursor.execute('''SELECT usuario.nome_usuario, usuario.email FROM sade.usuario''')
    usuarios = cursor.fetchall()

    return json.dumps(usuarios)

    
# @api.route('/login', methods = ['POST', 'GET'])
# def login():
#     if request.method == 'GET':
#         return "Login via the login Form"
     
#     if request.method == 'POST':
#         # name = request.form['name']
#         # age = request.form['age']
#         # cursor = mysql.connection.cursor()
#         # cursor.execute(''' INSERT INTO info_table VALUES(%s,%s)''',(name,age))
#         # mysql.connection.commit()
#         # cursor.close()
#         return f"Done!!"

    
@api.route('/', methods=['GET'])
def initial():
  return "Você está no server!"


if __name__ == '__main__':
    api.run()
    