import json

import flet as f
import requests

from app_version import __build__, __version__
from config.config import carregar_configuracoes
from entity.update_checker import GOOGLE_PLAY_URL, _is_update_available


class Notifications(f.View):
    def __init__(self, page):
        super().__init__()
        self.page = page
        saved_deleted = self.page.client_storage.get("deleted_ids") or []
        saved_read = self.page.client_storage.get("read_ids") or []
        self.horizontal_alignment = f.CrossAxisAlignment.CENTER
        self.local_deleted_ids = set(saved_deleted)
        self.local_read_ids = set(saved_read)
        self.text_no_notify = f.Text(size=16)
        self.text_no_notify.visible = True
        self.text_no_notify.value = "Carregando notificações..."
        self.status = carregar_configuracoes("config/config.xml")
        self.list_view = f.ListView(expand=2, spacing=10, padding=10)

        self.route = "/notifications"
        self.bgcolor = "transparent"
        self.decoration = f.BoxDecoration(
            image=f.DecorationImage(src="bgb.jpg", fit=f.ImageFit.COVER)
        )
        self.API_BASE_URL = "https://merotec42.pythonanywhere.com"

        self.controls = [
            f.AppBar(
                leading=f.IconButton(
                    icon=f.Icons.ARROW_BACK,
                    icon_color="white",
                    on_click=lambda _: self.page.go("/calc"),
                ),
                title=f.Row(
                    width=220,
                    spacing=5,
                    controls=[
                        f.Text(
                            "Central",
                            size=20,
                            color="#ebebeb",
                            weight="bold",
                            style=f.TextStyle(shadow=f.BoxShadow(2, 8, "green")),
                        ),
                        f.Text(
                            "de",
                            size=22,
                            color="#ebebeb",
                            weight="bold",
                            style=f.TextStyle(shadow=f.BoxShadow(2, 8, "red")),
                        ),
                        f.Text(
                            "Notificações",
                            size=20,
                            color="#ebebeb",
                            weight="bold",
                            style=f.TextStyle(shadow=f.BoxShadow(2, 8, "blue")),
                        ),
                    ],
                ),
                center_title=True,
                bgcolor="INDIGO",
                actions=[
                    f.IconButton(
                        f.Icons.REFRESH,
                        bgcolor="",
                        icon_color="#dff9fb",
                        on_click=lambda _: self.load_notifications(),
                        padding=20,
                    )
                ],
            ),
            self.text_no_notify,
            self.list_view,
        ]

    def start_background_load(self):
        self.page.run_thread(self.load_notifications)

    def load_notifications(self):
        self.list_view.controls.clear()
        self.API_BASE_URL = "https://merotec42.pythonanywhere.com"
        self.add_update_notification()
        try:
            retorno = requests.get(f"{self.API_BASE_URL}/get_notifications", timeout=10)
            data = json.loads(retorno.content)

            for item in data:
                item_id = str(item["id"])
                if item_id in self.local_deleted_ids:
                    continue

                is_read = item_id in self.local_read_ids
                self.list_view.controls.append(self.build_notification_card(item, is_read))
        except Exception:
            self.text_no_notify.visible = True
            self.text_no_notify.value = "Não há notificações a exibir no momento."

        if not self.list_view.controls:
            self.text_no_notify.visible = True
            self.text_no_notify.value = "Não há notificações a exibir no momento."
        else:
            self.text_no_notify.visible = False
        self.page.update()

    def add_update_notification(self):
        """Inclui na central a atualiza\u00e7\u00e3o identificada na abertura do app."""
        update = self.page.client_storage.get("available_update") or {}
        version = str(update.get("version") or "")
        build = update.get("build")
        if not version or not _is_update_available(version, build, __version__, __build__):
            return

        build_label = f" (build {build})" if build is not None else ""

        item = {
            "id": f"system-update-{version}-{build or 'unknown'}",
            "icon_noticia": f.Icons.SYSTEM_UPDATE,
            "titulo_noticia": "Atualiza\u00e7\u00e3o dispon\u00edvel",
            "txt_noticia": (
                f"A vers\u00e3o {version}{build_label} do Galvanos Calc est\u00e1 dispon\u00edvel "
                "na Google Play."
            ),
            "action_url": GOOGLE_PLAY_URL,
        }
        item_id = item["id"]
        if item_id not in self.local_deleted_ids:
            self.list_view.controls.append(
                self.build_notification_card(item, item_id in self.local_read_ids)
            )

    def build_notification_card(self, item, is_read):
        item_id = str(item["id"])
        action_url = item.get("action_url")
        is_update_notification = bool(action_url)
        return f.Card(
            content=f.Container(
                padding=15,
                border_radius=10,
                bgcolor=f.Colors.GREY_100 if is_read else f.Colors.WHITE,
                content=f.Column(
                    [
                        f.ListTile(
                            leading=f.Icon(
                                f.Icons.CHECK_SHARP if is_read else item["icon_noticia"],
                                color=f.Colors.GREY_400 if is_read else f.Colors.BLUE_ACCENT,
                            ),
                            title=f.Text(item["titulo_noticia"], weight="bold" if not is_read else "normal"),
                            subtitle=f.Text(item["txt_noticia"]),
                            on_click=(
                                lambda _: self.open_notification_link(item_id, action_url)
                                if is_update_notification
                                else lambda _: self.as_read_e_go(item_id)
                                if self.status["active"] == "False"
                                else None
                            ),
                        ),
                        f.Row(
                            [
                                f.TextButton(
                                    "Marcar como lida",
                                    icon=f.Icons.CHECK_CIRCLE_OUTLINE,
                                    visible=not is_read and not is_update_notification,
                                    on_click=lambda _: self.mark_as_read(item_id),
                                ),
                                f.TextButton(
                                    "Atualizar",
                                    icon=f.Icons.SYSTEM_UPDATE,
                                    visible=is_update_notification,
                                    on_click=lambda _: self.open_notification_link(item_id, action_url),
                                ),
                                f.TextButton(
                                    "Apagar",
                                    icon=f.Icons.DELETE_SWEEP,
                                    icon_color=f.Colors.RED_ACCENT,
                                    on_click=lambda _: self.delete_local(item_id),
                                ),
                            ],
                            alignment=f.MainAxisAlignment.END,
                        ),
                    ]
                ),
            ),
            elevation=6 if is_read else 10,
            shadow_color=f.Colors.with_opacity(0.35, "#334155"),
            shape=f.RoundedRectangleBorder(radius=10),
        )

    def mark_as_read(self, n_id):
        self.local_read_ids.add(n_id)
        self.page.client_storage.set("read_ids", list(self.local_read_ids))
        self.load_notifications()

    def as_read_e_go(self, n_id):
        self.mark_as_read(n_id)
        self.page.go("/")

    def open_notification_link(self, n_id, url):
        self.mark_as_read(n_id)
        self.page.launch_url(url)

    def delete_local(self, n_id):
        self.local_deleted_ids.add(n_id)
        self.page.client_storage.set("deleted_ids", list(self.local_deleted_ids))
        self.load_notifications()
