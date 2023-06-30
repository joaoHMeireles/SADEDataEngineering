import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer


def converter_valor(valor_puro, moeda):
    cotacao = 1
    
    if moeda == "DOLAR":
        cotacao = 4.78
    elif moeda == "EURO":
        cotacao = 5.22
    
    return valor_puro * cotacao


def unirDemandaComUsuario(demandas, usuarios):
    tipoSolicitante = []
    cargoSolicitante = [] 
    departamentoSolicitante = []
    nomeSolicitante = []
    setorSolicitante = []

    for index, demanda in demandas.iterrows():
        usuario = usuarios.loc[usuarios['id_usuario'] == demanda.id_usuario]
        index = usuario.index[0]
    
        tipoSolicitante.append(usuarios.at[index, "dtype"])
        cargoSolicitante.append(usuario.at[index, "cargo"])
        departamentoSolicitante.append(usuario.at[index, "departamento"])
        nomeSolicitante.append(usuario.at[index, "nome_usuario"])
        setorSolicitante.append(usuario.at[index, "setor"])
    

    demandas["tipo_solicitante"] = tipoSolicitante
    demandas["cargo_solicitante"] = cargoSolicitante
    demandas["departamento_solicitante"] = departamentoSolicitante
    demandas["nome_solicitante"] = nomeSolicitante
    demandas["setor_solicitante"] = setorSolicitante
    
    demandas.drop(columns=["id_usuario"], inplace=True)
    
    return demandas


def unirDemandaComBeneficio(demandas, beneficiosDemanda):
    qtd_beneficio_real = []
    qtd_beneficio_potencial = []
    qtd_beneficio_qualitativo = []
    valor_total_beneficios_reais = []
    valor_total_beneficios_potenciais = []
    descricao_beneficios = []

    for index, demanda in demandas.iterrows():
        beneficios = beneficiosDemanda.loc[beneficiosDemanda.id_demanda == demanda.id_demanda]
        qtd_real = 0
        qtd_potencial = 0
        qtd_qualitativo = 0
        valor_total_real = 0.0
        valor_total_potencial = 0.0
        descricao_beneficios_demanda = ""
    
        for index, beneficio in beneficios.iterrows():
            tipo = beneficio.tipo_beneficio
        
            if tipo == "QUALITATIVO":
                qtd_qualitativo += 1
            elif tipo == "REAL":
                if np.isnan(beneficio.valor):
                    continue
            
                qtd_real += 1
                valor_total_real += converter_valor(beneficio.valor, beneficio.moeda)
            elif tipo == "POTENCIAL":
                if np.isnan(beneficio.valor):
                    continue
                
                qtd_potencial += 1
                valor_total_potencial += converter_valor(beneficio.valor, beneficio.moeda)
            
            descricao_beneficios_demanda += ". " + beneficio.descricao
        
    
        qtd_beneficio_real.append(qtd_real)
        qtd_beneficio_potencial.append(qtd_potencial)
        qtd_beneficio_qualitativo.append(qtd_qualitativo)
        valor_total_beneficios_reais.append(valor_total_real)
        valor_total_beneficios_potenciais.append(valor_total_potencial)
        descricao_beneficios.append(descricao_beneficios_demanda)
    
    
    demandas["qtd_beneficio_real"] = qtd_beneficio_real
    demandas["qtd_beneficio_potencial"] = qtd_beneficio_potencial
    demandas["qtd_beneficio_qualitativo"] = qtd_beneficio_qualitativo
    demandas["valor_total_beneficios_reais (BRL)"] = valor_total_beneficios_reais
    demandas["valor_total_beneficios_potenciais (BRL)"] = valor_total_beneficios_potenciais   
    demandas["descricao_beneficios"] = descricao_beneficios  
    
    return demandas


def unirDemandaComCCs(demandas, CCs, CCsDemanda):
    quantidade_CC_demanda = []
    nomes_CC_demanda = []

    for index, demanda in demandas.iterrows():
        centros_custo_demanda = CCsDemanda[CCsDemanda.id_demanda == demanda.id_demanda]
        quantidade_CCs = 0
        nomes_CC = ""
    
        for index, centro_custo in centros_custo_demanda.iterrows():
            quantidade_CCs += 1
            nome = CCs.loc[CCs.id_centrocusto == centro_custo.id_centrocusto]
            nomes_CC += ". " + nome.at[nome.index[0], "nome_centro_custo"]
        
        quantidade_CC_demanda.append(quantidade_CCs)
        nomes_CC_demanda.append(nomes_CC)
    
    demandas["quantidade_CC"] = quantidade_CC_demanda
    demandas["nomes_CC"] = nomes_CC_demanda
    
    return demandas

    
def transformarBancoToDataFrame(demandas, usuarios, beneficios, CCs, CCsDemanda):
    df_demandas = pd.DataFrame(demandas)
    df_usuarios = pd.DataFrame(usuarios)
    df_beneficios = pd.DataFrame(beneficios)
    df_CCs = pd.DataFrame(CCs)
    df_CCsDemanda = pd.DataFrame(CCsDemanda)
    
    df_demandas_transformadas = unirDemandaComUsuario(df_demandas, df_usuarios)
    df_demandas_transformadas = unirDemandaComBeneficio(df_demandas_transformadas, df_beneficios)
    df_demandas_transformadas = unirDemandaComCCs(df_demandas_transformadas, df_CCs, df_CCsDemanda)
    
    return df_demandas_transformadas


def adicionarNovaColuna(df_alvo, nome_coluna, df_info):
    X = df_info[nome_coluna].values.astype('U')

    cvec = CountVectorizer().fit(X)
    df_coluna = pd.DataFrame(cvec.transform(X).todense(), columns=cvec.get_feature_names_out())
    
    return df_coluna


def transformarDataFrameToVetorizada(df_demanda):
    df_preparacao_NLP = pd.DataFrame()
    nome_colunas_desejadas = [
        "frequencia_uso", "objetivo", "situacao_atual","titulo_demanda","tipo_solicitante","cargo_solicitante",
        "departamento_solicitante","nome_solicitante", "setor_solicitante","descricao_beneficios","nomes_CC"
    ]

    
    for nome_coluna in df_demanda.columns:
        if nome_coluna in nome_colunas_desejadas:
            df_coluna_nova = adicionarNovaColuna(df_preparacao_NLP, nome_coluna, df_demanda)
            df_preparacao_NLP = pd.concat([df_preparacao_NLP, df_coluna_nova], axis=1)
        
    
    df_preparacao_nao_NLP = df_demanda.drop(columns=nome_colunas_desejadas, axis=1)
    
    df_preparacao_nao_NLP_normalizada=(df_preparacao_nao_NLP-df_preparacao_nao_NLP.min())/(df_preparacao_nao_NLP.max()-df_preparacao_nao_NLP.min())
    df_preparacao_nao_NLP_normalizada.drop("id_demanda", axis=1, inplace=True)
    df_preparacao_nao_NLP = pd.concat([df_preparacao_nao_NLP["id_demanda"], df_preparacao_nao_NLP_normalizada], axis=1)
    
    df_todos_dados = pd.concat([df_preparacao_NLP, df_preparacao_nao_NLP], axis=1)
    
    return df_todos_dados


def adicionarNovaLinha(df_demanda, demandaNova):
    print("adicionar uma linha em demandas ae")
    print(demandaNova)
    
    return df_demanda