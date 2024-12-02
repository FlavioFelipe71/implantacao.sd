import xml.etree.ElementTree as ET
import pandas as pd
import streamlit as st
import os
import locale
import base64

# Configurar a largura da página para "wide" ao fechar a sidebar
st.set_page_config(page_title="CSVSEI901", layout="wide", page_icon="🌲")

# Novo código SVG para o ícone desejado (um exemplo simples de um círculo)
new_svg_icon = """
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
    <circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red" />
</svg>
"""

# CSS para ocultar o badge original da Streamlit
hide_st_style = """
<style>
._container_gzau3_1._viewerBadge_nim44_23 {
    display: none !important;
}
</style>
"""

# Aplicando o CSS para ocultar o badge original
st.markdown(hide_st_style, unsafe_allow_html=True)

# Exibindo o novo ícone em vez do original
st.markdown(new_svg_icon, unsafe_allow_html=True)

# Aplicando o CSS para ocultar o badge original
st.markdown(hide_st_style, unsafe_allow_html=True)

# Adicionando o novo ícone em vez do original
st.markdown(new_svg_icon, unsafe_allow_html=True)

# CSS para ocultar o ícone do GitHub no canto superior direito
st.markdown(
    """
    <style>
        /* Ocultar o ícone do GitHub ou outros botões da barra de ferramentas */
        .stToolbarActionButton {
            display: none;
        }
    </style>
    """, 
    unsafe_allow_html=True
)

# CSS para ocultar o elemento <header>
st.markdown(
    """
    <style>
        /* Ocultar o header completo */
        .stAppHeader {
            display: none;
        }
    </style>
    """, 
    unsafe_allow_html=True
)

##### Oculta o botão Deploy do Streamilit
st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
""", unsafe_allow_html=True
)

# Faixa no cabeçalho
st.markdown("""
<div style='display: flex; justify-content: flex-end; align-items: center; background-color: gainsboro; padding:2px 0;margin-top: -40px;'>
    <span style='color: black; margin-right:10px;'>Alterar Tags xml</span>
</div>
""", unsafe_allow_html=True)

# Função para ler a imagem e convertê-la para base64
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return encoded_string
# Obtém o diretório do script
current_dir = os.path.dirname(os.path.abspath(__file__))
# Constrói o caminho completo para a imagem
image_path = os.path.join(current_dir, "fundo_softdib.jpg")

# Codificação da imagem em base64
base64_image = get_base64_image(image_path)

st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.9)), url('data:image/png;base64,{base64_image}') no-repeat center center fixed;
        background-size: cover;
    }}
    </style>
    """,
    unsafe_allow_html=True
)
###### CSS para definir a imagem de fundo [Fim]

# Função para ler o XML
def ler_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    return tree, root


def buscar_peso_no_packinglist(produto, packinglist_df):
    # Verificar se o produto existe no dataframe
    produto = produto.strip()  # Remover espaços em branco
    matching_row = packinglist_df[packinglist_df['produto'] == produto]
    
    if not matching_row.empty:
        return matching_row['peso'].values[0]  # Retorna o peso correspondente
    else:
        return None  # Retorna None se não encontrar correspondência

# Configura o locale para o padrão brasileiro
#locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def formatar_valor(valor):
    if pd.notna(valor):  # Verifica se o valor não é NaN
        return locale.format_string('%.2f', valor, grouping=True)
    return valor  # Retorna o valor original caso seja NaN

def processar_xml(root):
    data = {
        "DI": [],
        "FORNECEDOR": [],
        "ORDEM COMPRA": [],
        "PRODUTO": [],
        "NCM": [],
        "QUANTIDADE": [],
        "VALOR UNITARIO": [],
        "VALOR TOTAL": [],
        "PESO ITEM": [],  # Coluna PESO ITEM
        "LETRA": []  # Coluna LETRA associada ao <numeroAdicao>
    }

    di_global = None  # Variável para armazenar o número DI
    letra_atual = None  # Variável para armazenar o número de adição atual
    ncm_atual = None  # Variável para armazenar o NCM atual

    # Capturar o valor de DI no início do XML
    for elem in root.iter("numeroDI"):
        di_global = elem.text.strip() if elem.text else None
        break  # Como há apenas um DI global, paramos após encontrá-lo

    # Iterar pelos elementos do XML
    produtos_temp = []  # Lista temporária para armazenar produtos antes de associar o número de adição
    for elem in root.iter():
        # Quando encontrar a descrição do produto
        if elem.tag == "descricaoMercadoria":
            produto = elem.text.strip() if elem.text else ""
            produto_codigo = produto.split("-")[0] if "-" in produto else produto
            produtos_temp.append(produto_codigo)

        # Quando encontrar o número de adição
        elif elem.tag == "numeroAdicao":
            letra_atual = elem.text.strip() if elem.text else ""

            # Associar produtos temporários ao número de adição
            for produto in produtos_temp:
                data["PRODUTO"].append(produto)
                data["LETRA"].append(letra_atual)
                data["DI"].append(di_global if di_global else "N/A")  # Associar DI
                data["NCM"].append(ncm_atual if ncm_atual else "N/A")  # Associar NCM ou N/A

            produtos_temp = []  # Limpar lista de produtos temporários

        # Quando encontrar o código NCM
        elif elem.tag == "dadosMercadoriaCodigoNcm":
            ncm_atual = elem.text.strip() if elem.text else ""

        # Preenchendo outras informações
        elif elem.tag == "quantidade":
            data["QUANTIDADE"].append(float(elem.text.strip()) if elem.text else 0)
        elif elem.tag == "valorUnitario":
            data["VALOR UNITARIO"].append(float(elem.text.strip()) if elem.text else 0)

    # Calcular o VALOR TOTAL e adicionar o PESO ITEM
    for i in range(len(data["QUANTIDADE"])):
        data["VALOR TOTAL"].append(data["QUANTIDADE"][i] * data["VALOR UNITARIO"][i])
        data["PESO ITEM"].append(None)  # Inicializando com None para preenchimento posterior

    # Layout de 3 colunas
    col1, col2, col3 = st.columns([2, 2, 5])

# Coluna 1: Campo de entrada para o código do FORNECEDOR (6 caracteres)
    with col1:
        fornecedor_input = st.text_input("Informe o COD do FORNECEDOR (6 caracteres):", max_chars=6)

    # Coluna 2: Campo de entrada para o Nro da Ordem de Compra
    with col2:
        ordem_compra_input = st.text_input("Informe o NRO da Ordem de Compra:", max_chars=15)  # Adicionando o campo para Ordem de Compra

    # Estilo do botão e dos campos de entrada (o mesmo que você forneceu)
    st.markdown("""<style>
        .stButton button {
            background-color: #999999;  /* Cor CINZA */
            color: white;
            border: none;
            border-radius: 10px;
            padding: 12px 20px;  /* Ajustando o padding para maior altura */
            font-size: 16px;
            cursor: pointer;
            width: 100%;  /* Tamanho do botão */
            height: 50px;  /* Altura do botão */
        }
        .stButton button:hover {
            background-color: #999999;  /* CINZA mais escuro ao passar o mouse */
        }
    </style>""", unsafe_allow_html=True)

    # Estilo para o campo de texto (para ambos os campos de entrada)
    st.markdown("""<style>
    .stTextInput > div > div > input {
        background-color: #f0f8ff; /* Cor de fundo amarela clara */
        border: 2px solid #999999; /* Borda */
        border-radius: 10px; /* Bordas arredondadas */
        padding: 12px; /* Espaçamento interno */
        font-weight: bold; /* Texto em negrito */
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); /* Sombra suave */
    }
    </style>""", unsafe_allow_html=True)

    # Botão para incluir FORNECEDOR e ORDEM DE COMPRA
    if st.button("Incluir Fornecedor e Ordem de Compra"):
        # Verificação de entradas
        if not fornecedor_input or not ordem_compra_input:
            st.error("Ambos os campos 'FORNECEDOR' e 'ORDEM DE COMPRA' devem ser preenchidos!")
        elif len(fornecedor_input) != 6:
            st.error("O código do fornecedor deve ter exatamente 6 caracteres.")
        else:
            # Atualizar a coluna "FORNECEDOR" com o código informado
            data["FORNECEDOR"] = [fornecedor_input] * len(data["DI"])
            
            # Atualizar a coluna "ORDEM DE COMPRA" com o número informado
            data["ORDEM COMPRA"] = [ordem_compra_input] * len(data["DI"])

            st.success(f"Código do fornecedor '{fornecedor_input}' e Ordem de Compra '{ordem_compra_input}' incluídos em todas as linhas!")

    # Ajustar comprimento das listas para consistência
    max_len = max(len(data[key]) for key in data)
    for key in data:
        while len(data[key]) < max_len:
            data[key].append(None)

    return data

# Função para ajustar valores e formatar no padrão brasileiro
def ajustar_e_formatar(valor, divisor):
    if pd.notna(valor):  # Verifica se o valor não é NaN
        valor_ajustado = valor / divisor
        return locale.format_string('%.2f', valor_ajustado, grouping=True)
    return valor  # Retorna o valor original caso seja NaN



def gerar_csv(data, filename):
    # Converter o dicionário 'data' em um DataFrame do pandas
    df = pd.DataFrame(data)
    # Divisores específicos para cada coluna
    df['QUANTIDADE'] = df['QUANTIDADE'].apply(lambda x: ajustar_e_formatar(x, 1_000_00))
    df['VALOR UNITARIO'] = df['VALOR UNITARIO'].apply(lambda x: ajustar_e_formatar(x, 1_000_0000))
    df['VALOR TOTAL'] = df['VALOR TOTAL'].apply(lambda x: ajustar_e_formatar(x, 1_000_000_000_000))
        
    st.dataframe(df)

    # Criar o caminho completo para o arquivo CSV
    csv_path = os.path.join(os.getcwd(), filename)

    # Salvar o DataFrame como um arquivo CSV
    df.to_csv(csv_path, index=False, sep=";", encoding="utf-8")

    return csv_path


# Função principal
def main():
    # Adicionar a logo ao topo
    # Obtém o diretório atual do script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Constrói o caminho da imagem dinamicamente
    logo_path = os.path.join(current_dir, "Logo_sd.png")
    # Exibe a logo
    st.image(logo_path, width=200)

    # Titulo do Programa
    st.markdown(
        """
        <h1 style="text-align: center; font-size: 40px; color: #4CAF50;">
            Gerar SEI901CSV a partir de XML
        </h1>
        """,
        unsafe_allow_html=True,
    )
            
    st.markdown(f"<div style='font-size: 25px; font-weight: bold; color: #1E90FF;margin-top: 30px'>1º Passo: Importar arquivo XML</div>", unsafe_allow_html=True)
        #st.title("Editar o XML Tags: < descricaoMercadoria >, < numeroDI >, < fornecedorNome > com Base no CSV")
    st.markdown("""
    <div style="text-align: left; padding: 20px;">
        <p><strong>O objetivo é ler o XMl e montar uma Planilha base para importação do ITENS-DI-SEI901CSV </p>
        <p>Prepare uma planilha com a relação dos produtos e o peso líquido unitário de cada um deles..<strong></p>
  
    
    </div>
    """, unsafe_allow_html=True)    
    # Inserindo o estilo CSS para customizar a borda
    # Definir o CSS personalizado
# Definir o CSS personalizado
    css = """
    <style>
        /* Estiliza o container do file_uploader */
        [data-testid='stFileUploader'] {
            width: max-content;
        }

        /* Estiliza a seção interna do file_uploader */
        [data-testid='stFileUploader'] section {
            padding: 0;
            float: left;
        }

        /* Esconde o ícone e o texto padrão do botão */
        [data-testid='stFileUploader'] section > input + div {
            display: none;
        }

        /* Estiliza a parte visível do botão */
        [data-testid='stFileUploader'] section + div {
            float: right;
            padding-top: 0;
        }

        /* Altera a cor de fundo do botão */
        [data-testid='stFileUploader'] label {
            background-color: #999999;  /* Cor de fundo do botão */
            color: white;  /* Cor do texto */
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }

        /* Altera a cor do botão ao passar o mouse (hover) */
        [data-testid='stFileUploader'] label:hover {
            background-color: #45a049; /* Cor do botão ao passar o mouse */
        }
    </style>
    """

    # Adicionar o CSS ao app Streamlit
    st.markdown(css, unsafe_allow_html=True)
    # Upload do arquivo XML
    uploaded_file_xml = st.file_uploader("Envie o arquivo XML", type="xml")

    if uploaded_file_xml:
        tree, root = ler_xml(uploaded_file_xml)

        # Processar o XML para extrair os dados
        data = processar_xml(root)

        st.subheader("2º Passo: Envie o arquivo packinglist.csv")
        st.markdown("""
            <div style="text-align: left; padding: 20px;">
                <p>Criar arquivo packinglist.csv contendo 2 colunas: <strong>produto;peso</strong></p>
                <p>A leitura desse arquivo é obrigatório para gerar as informações em tela do CSVSEI901.</p>
            </div>
            """, unsafe_allow_html=True)

        
        # Upload do arquivo packinglist.csv
        uploaded_file_packinglist = st.file_uploader("Leitura packinglist.csv", type="csv")
        if uploaded_file_packinglist:
            # Ler o packinglist.csv
            packinglist_df = pd.read_csv(uploaded_file_packinglist, sep=";", encoding="utf-8")
            packinglist_df['produto'] = packinglist_df['produto'].astype(str).str.zfill(7)  # Ajuste para ter 7 dígitos com zeros à esquerda

            # Atualizar os pesos para cada produto
            for i in range(len(data["PRODUTO"])):
                produto = data["PRODUTO"][i]
                peso = buscar_peso_no_packinglist(produto, packinglist_df)
                data["PESO ITEM"][i] = peso
                        # Exibir os dados com a coluna PESO ITEM preenchida
    
    
            st.subheader("Espelho do SEI901CSV")
            #st.write(pd.DataFrame(data))  # Exibe os dados com a coluna PESO ITEM preenchida    
            # Definir o CSS personalizado
            css = """
            <style>
                /* Altera o estilo do botão de download */
                [data-testid='stDownloadButton'] {
                    background-color: #999999;  /* Cor de fundo do botão (verde) */
                    color: Green;  /* Cor do texto */
                    padding: 12px 25px;  /* Aumenta o tamanho do botão */
                    border-radius: 10px;  /* Borda arredondada */
                    font-size: 18px;  /* Tamanho da fonte */
                    font-weight: bold;  /* Peso da fonte */
                    cursor: pointer;  /* Cursor de mão */
                    text-align: center;  /* Alinha o texto ao centro */
                    border: none;  /* Remove a borda padrão */
                }

                /* Efeito hover do botão */
                [data-testid='stDownloadButton']:hover {
                    background-color: #28a745;  /* Cor de fundo mais escura ao passar o mouse */
                }
            </style>
            """

            # Adicionar o CSS ao app Streamlit
            st.markdown(css, unsafe_allow_html=True)
            # Gerar o CSV
            csv_filename = "ITENS-DI-SEI901CSV.csv"
            csv_path = gerar_csv(data, csv_filename)

            # Exibir sucesso e link para download
            st.success(f"CSV gerado com sucesso! Clique abaixo para baixar:")
            with open(csv_path, "r", encoding="utf-8") as f:
                st.download_button(
                    label="Baixar CSV Gerado",
                    data=f,
                    file_name=csv_filename,
                    mime="text/csv"
                )

if __name__ == "__main__":
    main()
