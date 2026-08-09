import xml.etree.ElementTree as ET
# Função para carregar configurações do XML
def carregar_configuracoes(arquivo_xml):
    try:
        tree = ET.parse(arquivo_xml)
        root = tree.getroot()

        # Extraindo e convertendo variáveis
        stCd_str = root.find('stCd').text
        stCr_str = root.find('stCr').text
        stRe_str = root.find('stRe').text
        stNq_str = root.find('stNq').text
        app_id = root.find('app_id').text # o padrão é 0

        licence_key = root.find('licence_key').text # o padão é 0
        licence_status = root.find('licence_status/active').text # o padrão é False

        email = root.find('conta/email').text # o padrão é none
        tel = root.find('conta/tel').text # o padrão é none
        empresa = root.find('conta/empresa').text # o padrão é none

        aria_total = root.find('historico/aria_total').text # o padão é 0
        saida = root.find('historico/saida').text # o padão é 0


        # Conversão para os tipos numéricos/booleanos corretos
        # O texto de um elemento XML é sempre uma string, precisa ser convertido explicitamente
        config = {
            "stCd": float(stCd_str),
            "stCr": int(stCr_str),
            "stRe": int(stRe_str),
            "stNq": float(stNq_str),
            "app_id": str(app_id),

            "licence_key": str(licence_key),
            "active": str(licence_status),

            "email": str(email),
            "tel": str(tel),
            "empresa": str(empresa),

            "aria_total": str(aria_total),
            "saida": str(saida),
        }
        return config
    except Exception as e:
        print(f"Erro ao carregar configurações: {e}")
        return None

