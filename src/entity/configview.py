import xml.etree.ElementTree as ET

import flet as f

from config.config import carregar_configuracoes
from entity.dialogs import share_clicked


class ConfigView(f.View):
    def __init__(self, page: f.Page):
        super().__init__()
        self.route = "/configview"
        self.page = page
        config = carregar_configuracoes("config/config.xml")
        self.bgcolor = "transparent"
        self.decoration = f.BoxDecoration(
            image=f.DecorationImage(src="bgb.jpg", fit=f.ImageFit.COVER)
        )
        self.stCd = config["stCd"]
        self.stCr = config["stCr"]
        self.stRe = config["stRe"]
        self.stNq = config["stNq"]

        self.vertical_alignment = f.MainAxisAlignment.SPACE_EVENLY
        self.horizontal_alignment = f.CrossAxisAlignment.CENTER

        self.appbar = f.AppBar(
            leading=f.IconButton(
                f.Icons.ARROW_BACK,
                icon_color="white",
                on_click=lambda e: self.page.go("/calc"),
            ),
            title=f.Text("Configurações", size=18, color="#ffffff"),
            center_title=True,
            bgcolor="INDIGO",
            actions=[
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
                )
            ],
        )

        self.config = f.Container(
            width=700,
            alignment=f.alignment.center,
            padding=10,
            bgcolor="#FFFFFF",
            border_radius=10,
            shadow=f.BoxShadow(blur_radius=5, color="#777777"),
            visible=True,
            content=f.Column(
                width=400,
                alignment=f.MainAxisAlignment.CENTER,
                controls=[
                    f.Text("Parâmetros de processo", size=20, color="INDIGO", weight=f.FontWeight.BOLD),
                    f.Row(
                        [
                            f.Text("Cádmio: amp por dm²", size=14, color="indigo"),
                            stCd_value := f.Text(self.stCd, color="#000000", weight=f.FontWeight.BOLD),
                        ]
                    ),
                    f.Slider(
                        tooltip="CÁDMIO",
                        width=300,
                        value=float(self.stCd),
                        min=1,
                        max=5,
                        divisions=8,
                        label="{value}",
                        inactive_color="#cccccc",
                        on_change=lambda e: changeCd(e),
                    ),
                    f.Row(
                        [
                            f.Text("Cromo: amp por dm²", size=14, color="indigo"),
                            stCr_value := f.Text(self.stCr, color="#000000", weight=f.FontWeight.BOLD),
                        ]
                    ),
                    f.Slider(
                        tooltip="CROMO",
                        width=350,
                        value=int(self.stCr),
                        min=30,
                        max=50,
                        divisions=4,
                        label="{value}",
                        inactive_color="#cccccc",
                        on_change=lambda e: changeCr(e),
                    ),
                    f.Row(
                        [
                            f.Text("Reversão: amp por dm²", size=14, color="indigo"),
                            stRe_value := f.Text(self.stRe, color="#000000", weight=f.FontWeight.BOLD),
                        ]
                    ),
                    f.Slider(
                        tooltip="REVERSÃO",
                        width=300,
                        value=int(self.stRe),
                        min=15,
                        max=25,
                        divisions=2,
                        label="{value}",
                        inactive_color="#cccccc",
                        on_change=lambda e: changeRe(e),
                    ),
                    f.Row(
                        alignment=f.MainAxisAlignment.START,
                        controls=[
                            f.Text("Níquel: amp por dm²", size=14, color="indigo"),
                            stNq_value := f.Text(self.stNq, color="#000000", weight=f.FontWeight.BOLD),
                        ],
                    ),
                    f.Slider(
                        tooltip="NÍQUEL",
                        width=300,
                        value=float(self.stNq),
                        min=1,
                        max=5,
                        divisions=8,
                        label="{value}",
                        inactive_color="#cccccc",
                        on_change=lambda e: changeNq(e),
                    ),
                ],
            ),
        )

        self.line_containers = f.Row(
            scroll=f.ScrollMode.HIDDEN,
            spacing=10,
            width=500,
            controls=[
                f.Container(
                    on_click=lambda _: self.page.go("/notifications"),
                    bgcolor="#FFFFFF",
                    width=150,
                    height=150,
                    padding=10,
                    border_radius=5,
                    content=f.Column(
                        horizontal_alignment=f.CrossAxisAlignment.CENTER,
                        controls=[
                            f.CircleAvatar(
                                content=f.Image(src="../assets/paquimetro.webp", border_radius=50),
                                width=80,
                                height=80,
                            ),
                            f.Text("Facilidade na obtenção de área", font_family="poppins", text_align="center"),
                        ],
                    ),
                ),
                f.Container(
                    on_click=lambda _: self.page.go("/notifications"),
                    bgcolor="#FFFFFF",
                    width=150,
                    height=150,
                    padding=10,
                    border_radius=5,
                    content=f.Column(
                        horizontal_alignment=f.CrossAxisAlignment.CENTER,
                        controls=[
                            f.CircleAvatar(
                                content=f.Image(src="../assets/galvano.jpg", border_radius=50),
                                width=80,
                                height=80,
                            ),
                            f.Text("Aplicável na galvanoplastia", font_family="poppins", text_align="center"),
                        ],
                    ),
                ),
                f.Container(
                    on_click=lambda _: self.page.go("/notifications"),
                    bgcolor="#FFFFFF",
                    width=150,
                    height=150,
                    padding=10,
                    border_radius=5,
                    content=f.Column(
                        horizontal_alignment=f.CrossAxisAlignment.CENTER,
                        controls=[
                            f.CircleAvatar(
                                content=f.Image(src="../assets/metal.jpg", border_radius=50),
                                width=80,
                                height=80,
                            ),
                            f.Text("Também se aplica à metalurgia", font_family="poppins", text_align="center"),
                        ],
                    ),
                ),
            ],
        )

        self.controls = [self.appbar, self.config, self.line_containers]

        def changeCd(cd):
            self.XML_FILE = "config/config.xml"
            tree = ET.parse(self.XML_FILE)
            root = tree.getroot()
            value = round(float(cd.control.value), 1)
            stCd_value.value = f"{value:g}"
            root.find("stCd").text = f"{value:g}"
            self.stCd = stCd_value.value
            tree.write(self.XML_FILE)
            self.page.update()

        def changeCr(cr):
            self.XML_FILE = "config/config.xml"
            tree = ET.parse(self.XML_FILE)
            root = tree.getroot()
            stCr_value.value = int(cr.control.value)
            root.find("stCr").text = str(int(cr.control.value))
            self.stCr = stCr_value.value
            tree.write(self.XML_FILE)
            self.page.update()

        def changeRe(re):
            self.XML_FILE = "config/config.xml"
            tree = ET.parse(self.XML_FILE)
            root = tree.getroot()
            stRe_value.value = int(re.control.value)
            root.find("stRe").text = str(int(re.control.value))
            self.stRe = stRe_value.value
            tree.write(self.XML_FILE)
            self.page.update()

        def changeNq(nq):
            self.XML_FILE = "config/config.xml"
            tree = ET.parse(self.XML_FILE)
            root = tree.getroot()
            value = round(float(nq.control.value), 1)
            stNq_value.value = f"{value:g}"
            root.find("stNq").text = f"{value:g}"
            self.stNq = stNq_value.value
            tree.write(self.XML_FILE)
            self.page.update()
