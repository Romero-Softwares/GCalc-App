import os
import xml.etree.ElementTree as ET
def criar_xml(nome_arquivo):
    """
    Cria um novo arquivo XML com parâmetros padrão.
    """
    # Cria o elemento raiz
    raiz = ET.Element("config")

    # Cria elementos e subelementos
    ET.SubElement(raiz, "stCd").text = "2"
    ET.SubElement(raiz, "stCr").text = "50"
    ET.SubElement(raiz, "stRe").text = "20"
    ET.SubElement(raiz, "stNq").text = "1"
    ET.SubElement(raiz, "app_id").text = "0"
    ET.SubElement(raiz, "licence_key").text = "0"

    licence_status = ET.SubElement(raiz, "licence_status")
    ET.SubElement(licence_status, "active").text = "False"

    conta = ET.SubElement(raiz, "conta")
    ET.SubElement(conta, "email").text = "none"
    ET.SubElement(conta, "tel").text = "none"
    ET.SubElement(conta, "empresa").text = "none"

    historico = ET.SubElement(raiz, "historico")
    ET.SubElement(historico, "cumprimento").text = "0"
    ET.SubElement(historico, "diametro").text = "0"
    ET.SubElement(historico, "aria_total").text = "0"
    ET.SubElement(historico, "saida").text = "0"

    # Cria uma árvore XML com os elementos
    arvore = ET.ElementTree(raiz)

    # Escreve o arquivo XML
    try:
        arvore.write(nome_arquivo, encoding="utf-8", xml_declaration=True)
        print(f"Arquivo '{nome_arquivo}' criado com sucesso.")
    except Exception as e:
        print(f"Erro ao escrever o arquivo: {e}")

def verificar_e_criar_xml(nome_arquivo):
    """
    Verifica se um arquivo XML existe. Se não, o cria.
    """
    if not os.path.exists(nome_arquivo):
        print(f"Arquivo '{nome_arquivo}' não encontrado. Criando um novo...")
        criar_xml(nome_arquivo)
    else:
        print(f"Arquivo '{nome_arquivo}' já existe.")

# Nome do arquivo a ser verificado
nome_do_arquivo = "config/config.xml"

# Executa a função
verificar_e_criar_xml(nome_do_arquivo)
