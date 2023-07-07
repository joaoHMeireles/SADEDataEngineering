from flask import Flask, render_template, request, session
from flask_session import Session
import mysql.connector
import json
import pandas as pd
from utils import transformarBancoToDataFrame, transformarDataFrameToVetorizada, checarSimilaridade

api = Flask(__name__)
SESSION_TYPE = 'filesystem'
api.config.from_object(__name__)
Session(api)

api.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
db = mysql.connector.connect(
    host='127.0.0.1',   
    user='root',
    passwd='root',
    db='sade', 
    port=3306
)


@api.before_request
def _run_on_start():
    db.reconnect()
    cursor = db.cursor(dictionary=True)
    cursor.execute('''
        SELECT 
        demanda.id_demanda, demanda.frequencia_uso, demanda.objetivo, demanda.situacao_atual, demanda.titulo_demanda, demanda.id_usuario 
        FROM sade.demanda
    ''')
    demandas = cursor.fetchall()
    
    cursor.execute('''
        SELECT 
        usuario.dtype, usuario.id_usuario, usuario.cargo, usuario.departamento, usuario.nome_usuario, usuario.numero_cadastro, usuario.setor 
        FROM sade.usuario
    ''')
    usuarios = cursor.fetchall()
    
    cursor.execute('''SELECT * FROM sade.beneficio''')
    beneficios = cursor.fetchall()
    
    cursor.execute('''SELECT * FROM sade.centro_custo''')
    CCs = cursor.fetchall()
    
    cursor.execute('''SELECT * FROM sade.centro_custo_demanda''')
    CCsDemanda = cursor.fetchall()
    cursor.close()
    
    df_demandas = transformarBancoToDataFrame(demandas, usuarios, beneficios, CCs, CCsDemanda)
    session['df_demandas'] = df_demandas.to_dict('records')

    
def getDFDemandas():
    json_demandas = session.get('df_demandas')
    df_demandas = pd.DataFrame.from_dict(json_demandas)

    return df_demandas


@api.route('/', methods = ['GET'])
def checar():
    df_demandas = getDFDemandas()
    return df_demandas.to_json(orient='records')


@api.route('/checar', methods=['POST'])
def check():
    db.reconnect()
    cursor = db.cursor(dictionary=True)
    cursor.execute('''
        SELECT 
        usuario.dtype, usuario.id_usuario, usuario.cargo, usuario.departamento, usuario.nome_usuario, usuario.numero_cadastro, usuario.setor 
        FROM sade.usuario
    ''')
    usuarios = cursor.fetchall()
    
    cursor.execute('''SELECT * FROM sade.centro_custo''')
    CCs = cursor.fetchall()
    cursor.close()
    
    demanda_nova = json.loads(request.data)
    id_demandas_similares = checarSimilaridade(getDFDemandas(), demanda_nova, pd.DataFrame(usuarios), pd.DataFrame(CCs))
    
    return id_demandas_similares


if __name__ == '__main__':
    api.run()
    