import flet as f

from config.config import carregar_configuracoes
from entity.containerlicenceview_opt import Containerlicenceview
from entity.dialogs import share_clicked


class Adlicenceview(f.View):
    def __init__(self, page: f.Page):
        super().__init__()
        self.route = "/adlicenceview"
        self.page = page
        self.container_licence_forms = Containerlicenceview(page)
        self.bgcolor = "transparent"
        self.decoration = f.BoxDecoration(
            image=f.DecorationImage(src="bg-app.jpg", fit=f.ImageFit.COVER)
        )

        global appbar, title_activation, btn_activation
        self.scroll = "AUTO"
        self.controls = [
            appbar := f.AppBar(
                leading=f.IconButton(
                    icon=f.Icons.ARROW_BACK,
                    icon_color="white",
                    on_click=lambda _: self.reload_app_active(),
                ),
                title=f.Row(
                    spacing=5,
                    width=180,
                    controls=[
                        title_activation := f.Text(
                            "Ativação",
                            size=25,
                            color="#ebebeb",
                            weight="bold",
                            style=f.TextStyle(shadow=f.BoxShadow(2, 8, "green")),
                        ),
                    ],
                ),
                center_title=True,
                bgcolor="black",
                actions=[
                    btn_activation := f.ElevatedButton(
                        text="Continuar teste",
                        icon=f.Icons.APP_SHORTCUT,
                        icon_color="indigo",
                        style=f.ButtonStyle(shape=f.RoundedRectangleBorder(radius=5)),
                        on_click=lambda e: self.reload_app_active(),
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
            f.ResponsiveRow(
                alignment=f.MainAxisAlignment.CENTER,
                vertical_alignment=f.CrossAxisAlignment.CENTER,
                controls=[self.container_licence_forms],
            ),
        ]
        self.reload_app_active()

    def reload_app_active(self):
        device_info = carregar_configuracoes("config/config.xml") or {}
        active = device_info.get("active", "False")

        if active == "True":
            title_activation.value = "Dados do app"
            btn_activation.icon = f.Icons.APP_SHORTCUT
            btn_activation.text = " "
            btn_activation.width = 40
            appbar.bgcolor = "transparent"
        else:
            print("Estado da licença: não ativada")
        self.page.go("/calc")
