import datetime
import json
import uuid

import flet as f
import requests

from config.config_manager import ConfigManager
from entity.dialogs import contacts_admin


class Containerlicenceview(f.Container):
    def __init__(self, page: f.Page):
        super().__init__()
        self.page = page
        self.config = ConfigManager(page)
        self.api_url = "https://merotec42.pythonanywhere.com"

        self.col = {"sm": 5.8}
        self.page.scroll = "auto"

        self._setup_ui_components()
        self._initialize_device_identity()
        self.check_status_and_render()

    def _setup_ui_components(self):
        self.loading = f.AlertDialog(
            content=f.Column(
                [
                    f.ProgressRing(width=64, height=64, color="black"),
                    f.Text("Processando...", text_align="center"),
                ],
                tight=True,
                horizontal_alignment="center",
            ),
            bgcolor="white",
        )

        self.key_input = f.TextField(
            label="Chave de ativacao",
            border_color="amber700",
            color="white",
            focused_border_color="amber",
        )
        self.bt_activate = f.ElevatedButton(
            "Ativar licenca",
            icon=f.Icons.LOCK_OUTLINE,
            on_click=self.handle_activate,
        )
        self.bt_success = f.ElevatedButton(
            "Comece a usar",
            color="white",
            icon=f.Icons.APP_SHORTCUT,
            bgcolor="green",
            style=f.ButtonStyle(shape=f.RoundedRectangleBorder(radius=5)),
            on_click=lambda e: self.page.go("/calc"),
            visible=False,
        )

        self.device_id_text = f.Text("", color="white", weight="bold", size=16)
        self.device_id = f.Text("", color="white", weight="normal")

        self.section_activate = f.Container(
            bgcolor=f.Colors.with_opacity(0.5, "black"),
            padding=20,
            border_radius=10,
            content=f.Column(
                [
                    f.Text("Ativacao do Sistema", size=20, weight="bold", color="white"),
                    self.key_input,
                    f.Row([self.bt_activate, self.bt_success]),
                ]
            ),
        )

        self.email_input = f.TextField(
            label="Email",
            label_style=f.TextStyle(color="bluegrey200"),
            border_color="#ebebeb",
            color="white",
        )
        self.tel_input = f.TextField(
            label="Telefone",
            label_style=f.TextStyle(color="bluegrey200"),
            input_filter=f.NumbersOnlyInputFilter(),
            color="white",
        )
        self.empresa_input = f.TextField(
            label="Nome da empresa",
            label_style=f.TextStyle(color="bluegrey200"),
            color="white",
        )
        self.bt_enviar = f.ElevatedButton(
            "SOLICITAR CHAVE",
            icon=f.Icons.SEND,
            on_click=self.handle_request_key,
        )

        self.section_register = f.Container(
            visible=False,
            bgcolor=f.Colors.with_opacity(0.5, "black"),
            padding=20,
            border_radius=10,
            content=f.Column(
                [
                    f.Text("Solicitar Licenca", size=20, weight="bold", color="white"),
                    f.Text("Preencha os dados para receber sua chave.", color="bluegrey200"),
                    self.email_input,
                    self.tel_input,
                    self.empresa_input,
                    self.bt_enviar,
                ]
            ),
        )

        self.status_msg = f.Text("", weight="bold", size=16)
        self.status_id = f.Text("", weight="normal", size=14, visible=False)
        self.nome_conta = f.Text("", color="white", weight="normal")
        self.tel_conta = f.Text("", color="white")
        self.email_conta = f.Text("", color="white")

        self.section_active_conta = f.Container(
            width=300,
            bgcolor=f.Colors.with_opacity(0.5, "black"),
            border_radius=5,
            padding=10,
            visible=False,
            content=f.Column(
                controls=[
                    self.device_id_text,
                    self.device_id,
                    f.Divider(10, 1, "white", 2),
                    self.nome_conta,
                    self.tel_conta,
                    self.email_conta,
                ]
            ),
        )

        self.content = f.Column(
            [
                self.section_activate,
                self.section_register,
                self.status_msg,
                self.status_id,
                self.section_active_conta,
                f.ElevatedButton(
                    "Suporte Tecnico",
                    icon=f.Icons.CONTACT_SUPPORT,
                    on_click=lambda _: contacts_admin(self.page),
                ),
            ],
            spacing=20,
        )

    def _initialize_device_identity(self):
        if not self.page.client_storage.get("app_device_id"):
            self.page.client_storage.set("app_device_id", str(uuid.uuid4()))

        if not self.page.client_storage.get("key_licence"):
            self.page.client_storage.set("key_licence", str(uuid.uuid4()))

        if self.page.client_storage.get("active") in (None, "", "None"):
            self.page.client_storage.set("active", "False")

        self.config.sync_to_xml()

    def check_status_and_render(self):
        data = self.config.get_storage_data()
        active = data.get("active") == "True"
        has_registration = data.get("email") not in (None, "", "none", "None")

        self.status_id.visible = False
        self.section_active_conta.visible = False

        if active:
            self.section_register.visible = False
            self.section_activate.visible = True
            self.bt_activate.visible = False
            self.bt_success.visible = True
            self.key_input.value = "SISTEMA ATIVADO"
            self.key_input.disabled = True
            self.status_msg.value = "Licenca vinculada a:"
            self.status_msg.color = "green"
            self.section_active_conta.visible = True
            self.device_id_text.value = "Dispositivo ID"
            self.device_id.value = str(data.get("device_id") or "")
            self.nome_conta.value = f"Empresa: {data.get('empresa') or ''}"
            self.tel_conta.value = f"Telefone: {data.get('tel') or ''}"
            self.email_conta.value = f"E-mail: {data.get('email') or ''}"
        elif not has_registration:
            self.section_register.visible = True
            self.section_activate.visible = False
            self.status_msg.value = ""
        else:
            self.section_register.visible = False
            self.section_activate.visible = True
            self.bt_activate.visible = True
            self.bt_success.visible = False
            self.key_input.disabled = False
            self.status_msg.value = "Aguardando ativacao da chave vinculada."
            self.status_msg.color = "amber"
            self.status_id.value = f"ID: {data.get('device_id') or ''}"
            self.status_id.visible = True
            self.status_id.color = "white"

        self.page.update()

    def handle_activate(self, e):
        if not self.key_input.value:
            self.show_snack("Por favor, insira a chave!", "red")
            return

        self.set_loading(True)
        app_id = self.page.client_storage.get("app_device_id")
        local_key = self.page.client_storage.get("key_licence")

        try:
            if self.key_input.value != local_key:
                self.show_status("Chave invalida.", "red")
                return

            url = f"{self.api_url}/licence_activate_device/{app_id}"
            licence_data = {
                "chave": self.key_input.value,
                "active": "True",
                "device_id": app_id,
                "expire": (datetime.datetime.now() + datetime.timedelta(days=365)).isoformat(),
            }
            response = requests.put(
                url=url,
                data=json.dumps(json.dumps(licence_data)),
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.ok:
                self.page.client_storage.set("active", "True")
                self.config.sync_to_xml()
                self.check_status_and_render()
                self.show_snack("Ativado com sucesso!", "green")
            else:
                self.show_status("Chave invalida ou erro no servidor.", "red")
        except Exception:
            self.show_status("Erro de conexao com o servidor.", "red")
        finally:
            self.set_loading(False)

    def handle_request_key(self, e):
        if not all([self.email_input.value, self.tel_input.value, self.empresa_input.value]):
            self.show_snack("Preencha todos os campos!", "amber")
            return

        self.set_loading(True)
        app_id = self.page.client_storage.get("app_device_id")
        licence_key = self.page.client_storage.get("key_licence")

        try:
            url = f"{self.api_url}/licence_post/{app_id}"
            licence_data = {
                "chave": licence_key,
                "active": "False",
                "device_id": app_id,
                "expire": "0",
            }
            request_data = {
                "licenca": json.dumps(licence_data),
                "email": self.email_input.value,
                "tel": self.tel_input.value,
                "empresa": self.empresa_input.value,
            }
            response = requests.post(
                url=url,
                data=json.dumps(request_data),
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.ok:
                self.page.client_storage.set("email", self.email_input.value)
                self.page.client_storage.set("tel", self.tel_input.value)
                self.page.client_storage.set("empresa", self.empresa_input.value)
                self.page.client_storage.set("active", "False")
                self.config.sync_to_xml()
                self.show_snack("Dados enviados! Aguarde a ativacao da chave.", "green")
                self.check_status_and_render()
            else:
                self.show_status("Erro ao processar dados no servidor.", "red")
        except Exception:
            self.show_status("Falha na comunicacao com o servidor.", "red")
        finally:
            self.set_loading(False)

    def set_loading(self, state):
        if state:
            self.page.open(self.loading)
        else:
            self.page.close(self.loading)
        self.page.update()

    def show_status(self, text, color):
        self.status_msg.value = text
        self.status_msg.color = color
        self.page.update()

    def show_snack(self, text, color):
        self.page.snack_bar = f.SnackBar(f.Text(text), bgcolor=color)
        self.page.snack_bar.open = True
        self.page.update()
