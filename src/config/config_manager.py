from config.createconfig import verificar_e_criar_xml
import xml.etree.ElementTree as ET
import flet as ft
import os, requests, json

class ConfigManager:
    def __init__(self, page: ft.Page, xml_path="config/config.xml"):
        self.page = page
        self.xml_path = xml_path
        verificar_e_criar_xml(self.xml_path)
        self.seed_storage_from_xml()

        # 1. Configurações da API
        self.url_base = "https://merotec42.pythonanywhere.com/get_all_licences_from_server"

    @staticmethod
    def _is_empty(value, treat_zero_as_empty=False):
        if value is None:
            return True
        text = str(value).strip()
        if text in ("", "None", "none", "NULL", "null"):
            return True
        return treat_zero_as_empty and text == "0"

    def _xml_value(self, path):
        try:
            tree = ET.parse(self.xml_path)
            root = tree.getroot()
            element = root.find(path)
            return element.text if element is not None else None
        except Exception:
            return None

    def seed_storage_from_xml(self):
        """
        Reaproveita dados validos do XML quando o client_storage ainda esta vazio.
        """
        mapping = {
            "active": ("licence_status/active", False),
            "email": ("conta/email", True),
            "tel": ("conta/tel", True),
            "empresa": ("conta/empresa", True),
            "app_device_id": ("app_id", True),
            "key_licence": ("licence_key", True),
        }

        for storage_key, (xml_path, zero_is_empty) in mapping.items():
            if not self._is_empty(self.page.client_storage.get(storage_key)):
                continue

            value = self._xml_value(xml_path)
            if self._is_empty(value, treat_zero_as_empty=zero_is_empty):
                continue

            self.page.client_storage.set(storage_key, str(value))

        if self._is_empty(self.page.client_storage.get("active")):
            self.page.client_storage.set("active", "False")

    def sincronizar_status_licenca(self):
        try:
            # Faz a requisição GET
            data = self.get_storage_data()
            meu_id = data.get("device_id")
            if not meu_id:
                return

            resposta = requests.get(self.url_base, timeout=10)
            print("Meu ID: ", meu_id)
            # Verifica se deu certo (status 200)
            if resposta.status_code == 200:
                lista_de_dados = resposta.json()  # Aqui está sua lista!

                for item in lista_de_dados:
                    lic = item.get('licenca')
                    if isinstance(lic, str): lic = json.loads(lic)
                    is_active = lic.get('active') if isinstance(lic, dict) else None
                    if item.get("device_id") == meu_id and is_active is not None:
                        self.page.client_storage.set("active", is_active)
            else:
                print(f"Erro na API: {resposta.status_code}")

        except Exception as e:
            print(f"Erro ao conectar: {e}")

    def get_storage_data(self):
        """
        Recupera todos os dados do armazenamento local de uma vez.
        Funciona como a 'Fonte da Verdade' para a interface durante a execução.
        """
        active = self.page.client_storage.get("active")
        if self._is_empty(active):
            active = "False"

        return {
            "device_id": self.page.client_storage.get("app_device_id"),
            "licence_key": self.page.client_storage.get("key_licence"),
            "active": str(active),
            "email": self.page.client_storage.get("email"),
            "tel": self.page.client_storage.get("tel"),
            "empresa": self.page.client_storage.get("empresa")
        }

    def sync_to_xml(self):
        """
        Sincroniza os dados do storage local para o ficheiro XML.
        Garante persistência física dos dados caso o storage seja limpo.
        """
        data = self.get_storage_data()

        if not os.path.exists(self.xml_path):
            print(f"Aviso: Ficheiro {self.xml_path} não encontrado. Operação abortada.")
            return

        try:
            tree = ET.parse(self.xml_path)
            root = tree.getroot()

            # Mapeamento: (Caminho da tag no XML, Valor vindo do Storage)

            mapping = {
                'licence_status/active': data.get("active"),
                'conta/email': data.get("email"),
                'conta/tel': data.get("tel"),
                'conta/empresa': data.get("empresa"),
                'app_id': data.get("device_id"),
                'licence_key': data.get("licence_key")
            }

            for path, value in mapping.items():
                if self._is_empty(value):
                    continue
                element = root.find(path)
                if element is not None:
                    element.text = str(value)

            tree.write(self.xml_path, encoding="utf-8", xml_declaration=True)
            print(f"Configuração XML sincronizada com sucesso. {mapping.get('licence_status/active')}")
        except Exception as e:
            print(f"Erro ao atualizar XML: {e}")

    def is_licence_active(self):
        """
        Verifica rapidamente se a licença está ativa.
        Prioriza o storage local para maior velocidade de resposta na UI.
        """
        active_status = self.page.client_storage.get("active")
        return active_status == "True"

    def save_licence_data(self, active=None, email=None, tel=None, empresa=None):
        """
        Método utilitário para salvar vários campos ao mesmo tempo no storage
        e disparar a sincronização com o ficheiro XML.
        """
        if active is not None: self.page.client_storage.set("active", str(active))
        if email is not None: self.page.client_storage.set("email", email)
        if tel is not None: self.page.client_storage.set("tel", tel)
        if empresa is not None: self.page.client_storage.set("empresa", empresa)

        # Sincroniza imediatamente após salvar no storage
        self.sync_to_xml()
