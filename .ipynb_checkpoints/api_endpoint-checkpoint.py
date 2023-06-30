from flask import Flask, json, render_template, request, session
import mysql.connector
import json
import pandas as pd
from utils import transformarBancoToDataFrame, transformarDataFrameToVetorizada, adicionarNovaLinha

api = Flask(__name__)
api.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
db = mysql.connector.connect(
    host='127.0.0.1',   
    user='root',
    passwd='root',
    db='sade', 
    port=3306
)


@api.before_first_request
def _run_on_start():
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
    
    df_demandas = transformarBancoToDataFrame(demandas, usuarios, beneficios, CCs, CCsDemanda)
    df_dados_finais = transformarDataFrameToVetorizada(df_demandas) 
    
    session['df_demandas'] = df_dados_finais.to_dict('records')
    
    print("---------- DataFrame de demandas feito -----------")

    
def pegarDFDemandas():
    json_demandas = session.get('df_demandas')
    df_demandas = pd.DataFrame.from_dict(json_demandas)
    
    return df_demandas


@api.route('/', methods = ['GET'])
def checar():
    df_demandas = pegarDFDemandas()
    return df_demandas.to_json(orient='records')


@api.route('/checar', methods=['POST'])
def check():
    print("aaaaaaaaaaa")
    print(request.data)
    
    json_demanda_nova = request.data
    demanda_nova = json.loads(json_demanda_nova) # dicionário
    
    print(demanda_nova)
    
    return "Tudo certo"






if __name__ == '__main__':
    api.run()
    