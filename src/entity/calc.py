import json

import flet as f
import requests

from config.config import carregar_configuracoes
from entity.configview import ConfigView
from entity.containercalc import Containercalc
from entity.dialogs import (
    clear_historic,
    contacts_admin,
    get_listmed,
    hitorico_calculo,
    i_clicked,
    share_clicked,
)


class Calc(f.View):
    def __init__(self, page: f.Page):
        super().__init__()
        self.title = "GalvanOS Calculator"
        self.route = "/calc"
        self.page = page
        self.padding = -3
        self.device_info = carregar_configuracoes("config/config.xml")
        self.bgcolor = "transparent"
        self.decoration = f.BoxDecoration(
            image=f.DecorationImage(src="bgb.jpg", fit=f.ImageFit.COVER)
        )

        self.saved_read = self.page.client_storage.get("read_ids") or []
        self.saved_deleted = self.page.client_storage.get("deleted_ids") or []
        self.ids_comparar_list = list(set(self.saved_deleted) | set(self.saved_read))

        self.pop_menu = f.PopupMenuButton(
            icon=f.Icons.MENU,
            bgcolor="#f1f2f6",
            icon_color="indigo",
            shadow_color="#57606f",
            elevation=15,
            items=[
                f.PopupMenuItem(
                    content=f.Row([f.Icon(f.Icons.HISTORY), f.Text("Histórico", size=16, color="amber")])
                ),
                f.PopupMenuItem(
                    on_click=lambda _: get_listmed(page),
                    content=f.Row([f.Icon(f.Icons.LIST, size=15), f.Text("Lista de medidas", size=14)]),
                ),
                f.PopupMenuItem(
                    on_click=lambda _: hitorico_calculo(page),
                    content=f.Row([f.Icon(f.Icons.CALCULATE, size=15), f.Text("Último cálculo", size=14)]),
                ),
            ],
        )

        self.badge = f.Container(
            content=f.Text("", size=0),
            bgcolor=f.Colors.RED_ACCENT,
            width=10,
            height=10,
            border_radius=5,
            right=8,
            top=8,
            visible=False,
        )
        self.btn_notify = f.IconButton(
            icon=f.Icons.NOTIFICATIONS_ACTIVE,
            icon_color="indigo",
            on_click=lambda _: self.page.go("/notifications"),
        )
        self.bottom_appbar = f.BottomAppBar(
            bgcolor="white",
            shape=f.NotchShape.CIRCULAR,
            content=f.Row(
                controls=[
                    self.pop_menu,
                    f.Container(expand=True),
                    f.IconButton(
                        icon=f.Icons.SUPPORT_AGENT,
                        icon_color="indigo",
                        on_click=lambda e: contacts_admin(page),
                    ),
                    f.Stack([self.btn_notify, self.badge]),
                ]
            ),
        )

        self.floating_action_button = f.FloatingActionButton(
            icon=f.Icons.SETTINGS,
            shape=f.CircleBorder(),
            bgcolor="white",
            on_click=lambda e: self.page.go("/configview"),
        )
        self.floating_action_button_location = f.FloatingActionButtonLocation.CENTER_DOCKED

        self.line_containers = ConfigView(page).line_containers
        self.app_id = self.device_info["app_id"]
        self.scroll = f.ScrollMode.HIDDEN
        self.calc_container = Containercalc(page)

        self.app_activated = f.ElevatedButton(
            text="Conta",
            color="green",
            bgcolor="INDIGO",
            style=f.ButtonStyle(shape=f.RoundedRectangleBorder(radius=5)),
            icon=f.Icons.KEY,
            icon_color="green",
            on_click=lambda e: self.reload_view(),
        )
        self.app_activation = f.ElevatedButton(
            text="Ativar",
            color="amber",
            bgcolor="INDIGO",
            style=f.ButtonStyle(shape=f.RoundedRectangleBorder(radius=5)),
            icon=f.Icons.LOCK_ROUNDED,
            icon_color="red",
            on_click=lambda e: self.reload_view(),
        )

        self.historic_btns = f.Row(
            width=self.page.width,
            controls=[
                f.ElevatedButton(
                    text="Ver último cálculo",
                    color="#FFF5EE",
                    elevation=20,
                    bgcolor="INDIGO",
                    style=f.ButtonStyle(shape=f.RoundedRectangleBorder(radius=5)),
                    icon=f.Icons.HISTORY,
                    icon_color="white",
                    on_click=lambda _: hitorico_calculo(page),
                ),
                f.ElevatedButton(
                    text="Limpar",
                    color="#FFF5EE",
                    elevation=20,
                    bgcolor="INDIGO",
                    style=f.ButtonStyle(shape=f.RoundedRectangleBorder(radius=5)),
                    icon=f.Icons.CLEAR,
                    icon_color="white",
                    on_click=lambda _: self.clean_historic(),
                ),
            ],
        )

        self._pull_refresh = {"distancia": 0, "ativo": False, "atualizando": False}
        self._scroll_top = {"valor": True}
        self.pull_refresh_spinner = f.ProgressRing(
            width=16,
            height=16,
            stroke_width=2,
            color=f.Colors.BLUE_400,
        )
        self.pull_refresh_label = f.Text("Solte para atualizar", size=12, color=f.Colors.BLUE_GREY_400)
        self.pull_refresh_bar = f.Container(
            visible=False,
            alignment=f.alignment.center,
            padding=f.padding.only(top=8, bottom=4),
            content=f.Row(
                [
                    self.pull_refresh_spinner,
                    self.pull_refresh_label,
                ],
                spacing=8,
                alignment=f.MainAxisAlignment.CENTER,
            ),
        )

        def update_pull_indicator(texto, mostrar=True):
            self.pull_refresh_bar.visible = mostrar
            self.pull_refresh_label.value = texto
            self.page.update()

        def reset_pull_indicator():
            self._pull_refresh["distancia"] = 0
            self._pull_refresh["ativo"] = False
            self._pull_refresh["atualizando"] = False
            self.pull_refresh_label.value = "Solte para atualizar"
            self.pull_refresh_bar.visible = False

        def run_pull_refresh():
            if self._pull_refresh["atualizando"]:
                return

            self._pull_refresh["atualizando"] = True
            update_pull_indicator("Atualizando...")
            try:
                self.refresh_remote_status()
            finally:
                reset_pull_indicator()
                self.page.update()

        def track_scroll_position(e):
            pixels = float(getattr(e, "pixels", 0) or 0)
            min_extent = float(getattr(e, "min_scroll_extent", 0) or 0)
            event_type = (getattr(e, "event_type", "") or "").lower()
            overscroll = float(getattr(e, "overscroll", 0) or 0)
            scroll_delta = float(getattr(e, "scroll_delta", 0) or 0)
            direction = (getattr(e, "direction", "") or "").lower()
            is_at_top = pixels <= min_extent + 5
            self._scroll_top["valor"] = is_at_top

            if self._pull_refresh["atualizando"]:
                return

            pulling_down = overscroll != 0 or scroll_delta < 0 or direction in ("forward", "down")
            if is_at_top and pulling_down:
                self._pull_refresh["ativo"] = True
                self._pull_refresh["distancia"] += max(abs(overscroll), abs(scroll_delta), 8)

                if self._pull_refresh["distancia"] > 10 and not self.pull_refresh_bar.visible:
                    update_pull_indicator("Puxe para atualizar")
                elif self._pull_refresh["distancia"] > 24:
                    update_pull_indicator("Solte para atualizar")
                return

            should_refresh = (
                self._pull_refresh["ativo"]
                and self._pull_refresh["distancia"] > 24
                and event_type in ("end", "scrollend", "scroll_end", "idle")
            )

            if not should_refresh:
                if self._pull_refresh["ativo"] and event_type in ("end", "scrollend", "scroll_end", "idle"):
                    reset_pull_indicator()
                    self.page.update()
                return

            run_pull_refresh()

        self.on_scroll_interval = 100
        self.on_scroll = track_scroll_position

        self.controls = [
            f.AppBar(
                title=f.Row(
                    spacing=2,
                    width=80,
                    controls=[
                        f.Text(
                            "G",
                            size=32,
                            color="#ebebeb",
                            weight="bold",
                            style=f.TextStyle(shadow=f.BoxShadow(2, 8, "green")),
                        ),
                        f.Text(
                            "Calc",
                            size=20,
                            color="#ebebeb",
                            weight="bold",
                            style=f.TextStyle(shadow=f.BoxShadow(2, 8, "red")),
                        ),
                    ],
                ),
                center_title=True,
                bgcolor="INDIGO",
                actions=[
                    self.app_activation,
                    self.app_activated,
                    f.IconButton(
                        f.Icons.INFO,
                        bgcolor="",
                        icon_color="#dff9fb",
                        on_click=lambda _: i_clicked(page),
                    ),
                    f.PopupMenuButton(
                        bgcolor="#f1f2f6",
                        icon_color="#f1f2f6",
                        shadow_color="#57606f",
                        elevation=15,
                        items=[
                            f.PopupMenuItem(
                                text="Compartilhe esta ferramenta",
                                icon="share",
                                on_click=lambda _: share_clicked(page),
                            ),
                            f.PopupMenuItem(text="Disponível para iOS", checked=False),
                            f.PopupMenuItem(text="Disponível para Android", checked=False),
                        ],
                    ),
                ],
            ),
            f.Column(
                horizontal_alignment=f.CrossAxisAlignment.CENTER,
                controls=[
                    self.pull_refresh_bar,
                    f.ResponsiveRow(
                        alignment=f.MainAxisAlignment.CENTER,
                        vertical_alignment=f.CrossAxisAlignment.CENTER,
                        controls=[
                            self.historic_btns,
                            self.calc_container,
                            f.Container(
                                padding=f.Padding(15, 0, 15, 15),
                                content=f.Column(
                                    horizontal_alignment=f.CrossAxisAlignment.CENTER,
                                    controls=[self.line_containers],
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        ]

        self._remote_refresh_started = False
        self.connection_reload(check_remote=False)

    def start_background_refresh(self):
        if self._remote_refresh_started:
            return
        self._remote_refresh_started = True
        self.page.run_thread(self.refresh_remote_status)

    def refresh_remote_status(self):
        self.connection_reload()
        self.get_id_notify()

    def get_id_notify(self):
        api_base_url = "https://merotec42.pythonanywhere.com"
        id_notify = []
        try:
            nt = requests.get(f"{api_base_url}/get_notifications", timeout=10)
            dados = json.loads(nt.content)
            for noticia in dados:
                id_notify.append(noticia["id"])

            remote_id = set(int(i) for i in id_notify)
            ids_referencia = set(int(i) for i in self.ids_comparar_list)
            nao_lidos = [i for i in remote_id if i not in ids_referencia]
            self.badge.visible = bool(nao_lidos)
        except Exception:
            print("ID de notificação não carregado.")
            self.badge.visible = False
        self.page.update()

    def clean_historic(self) -> None:
        def confirm_clear(e):
            self.page.close(confirm_dialog)
            clear_historic(self.page)
            self.historic_btns.visible = False
            self.update()

        confirm_dialog = f.AlertDialog(
            content_padding=0,
            shape=f.RoundedRectangleBorder(radius=10),
            bgcolor="#f8fafc",
            title_padding=f.Padding(18, 14, 8, 0),
            title=f.Text("Confirmar limpeza", color="#1f2937", size=18, weight=f.FontWeight.BOLD),
            content=f.Container(
                width=330,
                padding=f.Padding(18, 8, 18, 12),
                content=f.Text(
                    "Deseja apagar o ultimo calculo salvo?",
                    size=15,
                    color="#374151",
                ),
            ),
            actions=[
                f.TextButton("Cancelar", on_click=lambda _: self.page.close(confirm_dialog)),
                f.TextButton("Sim, apagar", on_click=confirm_clear),
            ],
            actions_alignment=f.MainAxisAlignment.END,
        )
        self.page.open(confirm_dialog)

    def reload_view(self):
        self.page.views.clear()
        self.page.go("/")
        self.connection_reload()

    def connection_reload(self, check_remote=True):
        config = carregar_configuracoes("config/config.xml")
        aria_total = config["aria_total"]
        licenca_activate = config["active"]

        self.historic_btns.visible = aria_total != "0"
        print("reload informations")

        api_base_url = "https://rational-nice-akita.ngrok-free.app"
        if licenca_activate == "True":
            self.app_activation.visible = False
            self.app_activated.visible = True
        else:
            self.app_activation.visible = True
            self.app_activated.visible = False

        if check_remote:
            try:
                requests.get(f"{api_base_url}/get_licence_key/{self.app_id}", timeout=10)
                if licenca_activate == "False":
                    self.app_activated.visible = False
                    self.app_activation.visible = True
            except Exception:
                print("Sem conexão com o servidor.")
