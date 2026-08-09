import xml.etree.ElementTree as ET

import flet as f

from config.config import carregar_configuracoes
from entity.txt import txt_info_calc


result = f.AlertDialog(
    content_padding=10,
    shape=f.RoundedRectangleBorder(radius=5),
    title=f.Text("", color="amber", size=16, weight=f.FontWeight.BOLD),
    content=None,
    actions=[],
)


def contacts_admin(page: f.Page):
    contacts = f.AlertDialog(
        shape=f.RoundedRectangleBorder(radius=5),
        title=f.Text("Suporte técnico", color="amber", size=18),
        content=f.Column(
            height=70,
            controls=[
                f.Row(
                    [
                        f.Icon(f.Icons.CONTACT_PHONE_OUTLINED),
                        f.Text("(21)97382-2425", color="#333333"),
                        f.Image(src="assets/whatsapp.gif", border_radius=50, width=30),
                    ],
                    spacing=10,
                ),
                f.Row(
                    [
                        f.Icon(f.Icons.EMAIL_OUTLINED),
                        f.Text("merotec32@gmail.com", color="#333333"),
                    ],
                    spacing=10,
                ),
            ],
        ),
        actions=[f.TextButton("Fechar", on_click=lambda _: page.close(contacts))],
    )
    page.open(contacts)


def get_listmed(page: f.Page):
    tree = ET.parse("config/config.xml")
    root = tree.getroot()
    from entity.containercalc import Containercalc

    btn = Containercalc(page).calcular
    btn.visible = True

    def child_text(item, name, default=""):
        child = item.find(name)
        return child.text if child is not None and child.text else default

    def measure_card(item):
        qtd = child_text(item, "quantidade", "1")
        area_total = child_text(item, "aria", "0")
        area_unit = child_text(item, "aria_unitaria", area_total)
        item_id = child_text(item, "id", "-")
        comprimento = child_text(item, "cumprimento", "0")
        diametro = child_text(item, "diametro", "0")

        return f.Container(
            padding=12,
            border_radius=8,
            bgcolor="#ffffff",
            border=f.border.all(1, "#e5e7eb"),
            content=f.Column(
                spacing=8,
                controls=[
                    f.Row(
                        alignment=f.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            f.Text(f"{qtd}x", size=18, color="#1f2937", weight=f.FontWeight.BOLD),
                            f.Text(f"Índice {item_id}", size=12, color="#6b7280"),
                        ],
                    ),
                    f.Text(
                        f"Comprimento: {comprimento} mm  |  Diâmetro: {diametro} mm",
                        size=13,
                        color="#374151",
                    ),
                    f.Row(
                        spacing=8,
                        controls=[
                            f.Container(
                                expand=True,
                                padding=10,
                                border_radius=6,
                                bgcolor="#eef2ff",
                                content=f.Column(
                                    spacing=2,
                                    controls=[
                                        f.Text("Unitária", size=11, color="#4f46e5"),
                                        f.Text(f"{area_unit} dm²", size=14, color="#1e1b4b", weight=f.FontWeight.BOLD),
                                    ],
                                ),
                            ),
                            f.Container(
                                expand=True,
                                padding=10,
                                border_radius=6,
                                bgcolor="#ecfdf5",
                                content=f.Column(
                                    spacing=2,
                                    controls=[
                                        f.Text("Total", size=11, color="#047857"),
                                        f.Text(f"{area_total} dm²", size=14, color="#064e3b", weight=f.FontWeight.BOLD),
                                    ],
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        )

    lists = f.AlertDialog(
        content_padding=0,
        shape=f.RoundedRectangleBorder(radius=10),
        bgcolor="#f8fafc",
        title_padding=f.Padding(18, 14, 8, 0),
        title=f.Row(
            alignment=f.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                f.Row(
                    spacing=8,
                    controls=[
                        f.Text("Medidas armazenadas", color="#1f2937", size=18, weight=f.FontWeight.BOLD),
                        f.Text(len(root.findall("listmed/id")), size=14, color="#6b7280", weight="normal"),
                    ],
                ),
                f.IconButton(
                    f.Icons.CLOSE_ROUNDED,
                    icon_color="#ef4444",
                    on_click=lambda _: page.close(lists),
                ),
            ],
        ),
        actions=[btn],
        content=f.Container(
            width=420,
            height=320,
            padding=f.Padding(18, 8, 18, 12),
            content=f.Column(
                scroll=True,
                alignment=f.CrossAxisAlignment.CENTER,
                spacing=12,
                expand=True,
                controls=[measure_card(i) for i in root.findall("listmed")],
            ),
        ),
    )

    if not root.findall("listmed/aria"):
        lists.content = f.Text("A lista está vazia!", size=18)
        lists.content_padding = 40
        btn.visible = False

    page.open(lists)
    page.update()


def reload_app(page: f.Page):
    print("Reload App")
    from main import main

    page.controls.clear()
    main(page)
    page.update()


def clear_historic(page: f.Page):
    # progress = f.AlertDialog(
        # content=f.Column(
            # alignment=f.MainAxisAlignment.CENTER,
            # controls=[f.ProgressRing(width=100, height=100, color="black")],
        # ),
        # content_padding=80,
        # bgcolor="transparent",
        # barrier_color="transparent",
        # open=True,
    # )
    # page.overlay.append(progress)
    # page.update()

    try:
        xml_file = "config/config.xml"
        tree = ET.parse(xml_file)
        root = tree.getroot()
        root.find("historico/aria_total").text = "0"
        root.find("historico/saida").text = "0"
        tree.write(xml_file)
        result.title = f.Text("Histórico apagado", color="amber", size=16, weight=f.FontWeight.BOLD)
        result.content = f.Container(
            width=300,
            height=80,
            border_radius=4,
            bgcolor="transparent",
            image=f.DecorationImage(opacity=0.3, src="paquimetro.webp", fit=f.ImageFit.COVER),
            content=f.Column(
                controls=[f.Text(value="Seu histórico de cálculo está vazio!", size=16, weight="bold")]
            ),
            padding=10,
        )
    except Exception:
        print("Erro ao tentar limpar o histórico.")
        result.title = f.Text("Erro!", color="amber", size=16, weight=f.FontWeight.BOLD)
        result.content = f.Container(
            width=300,
            height=80,
            border_radius=4,
            bgcolor="transparent",
            image=f.DecorationImage(opacity=0.3, src="paquimetro.webp", fit=f.ImageFit.COVER),
            content=f.Column(
                controls=[f.Text(value="Algo deu errado ao tentar limpar o histórico!", size=16, weight="bold")]
            ),
            padding=10,
        )

    result.actions = [f.TextButton("Fechar", on_click=lambda _: page.close(result))]
    page.open(result)
    page.update()


def hitorico_calculo(page: f.Page):
    historico = carregar_configuracoes("config/config.xml")
    if historico["aria_total"] != "0":
        linhas = [linha.strip() for linha in historico["saida"].splitlines() if linha.strip()]
        processo = linhas[0].replace("Processo:", "").strip() if linhas else "Processo"
        detalhes = linhas[1:] if len(linhas) > 1 else []

        result_dialog = f.AlertDialog(
            content_padding=0,
            shape=f.RoundedRectangleBorder(radius=10),
            bgcolor="#f8fafc",
            title_padding=f.Padding(18, 14, 8, 0),
            title=f.Row(
                alignment=f.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    f.Text("Cálculo anterior", color="#1f2937", size=18, weight=f.FontWeight.BOLD),
                    f.IconButton(
                        f.Icons.CLOSE_ROUNDED,
                        icon_color="#ef4444",
                        on_click=lambda _: page.close(result_dialog),
                    ),
                ],
            ),
            content=f.Container(
                width=420,
                padding=f.Padding(18, 8, 18, 14),
                content=f.Column(
                    tight=True,
                    spacing=12,
                    controls=[
                        f.Container(
                            padding=14,
                            border_radius=8,
                            bgcolor="#ffffff",
                            border=f.border.all(1, "#e5e7eb"),
                            content=f.Row(
                                alignment=f.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    f.Column(
                                        tight=True,
                                        spacing=3,
                                        controls=[
                                            f.Text("Processo", size=12, color="#6b7280"),
                                            f.Text(processo, size=18, color="#111827", weight=f.FontWeight.BOLD),
                                        ],
                                    ),
                                    f.Column(
                                        tight=True,
                                        horizontal_alignment=f.CrossAxisAlignment.END,
                                        spacing=3,
                                        controls=[
                                            f.Text("Área total", size=12, color="#4f46e5"),
                                            f.Text(historico["aria_total"].replace("Área total:", "").strip(), size=20, color="#1e1b4b", weight=f.FontWeight.BOLD),
                                        ],
                                    ),
                                ],
                            ),
                        ),
                        f.Container(
                            padding=12,
                            border_radius=8,
                            bgcolor="#ffffff",
                            border=f.border.all(1, "#e5e7eb"),
                            content=f.Column(
                                tight=True,
                                spacing=8,
                                controls=[
                                    f.Row(
                                        alignment=f.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            f.Text(part.split(":", 1)[0].strip(), size=12, color="#6b7280"),
                                            f.Text(part.split(":", 1)[1].strip() if ":" in part else part, size=14, color="#111827", weight=f.FontWeight.BOLD),
                                        ],
                                    )
                                    for part in detalhes
                                ],
                            ),
                        ),
                    ],
                ),
            ),
        )
    else:
        result_dialog = f.AlertDialog(
            content_padding=0,
            shape=f.RoundedRectangleBorder(radius=10),
            bgcolor="#f8fafc",
            title_padding=f.Padding(18, 14, 8, 0),
            title=f.Row(
                alignment=f.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    f.Text("Histórico vazio", color="#1f2937", size=18, weight=f.FontWeight.BOLD),
                    f.IconButton(
                        f.Icons.CLOSE_ROUNDED,
                        icon_color="#ef4444",
                        on_click=lambda _: page.close(result_dialog),
                    ),
                ],
            ),
            content=f.Container(
                width=330,
                padding=f.Padding(18, 8, 18, 18),
                content=f.Column(
                    tight=True,
                    controls=[
                        f.Container(
                            padding=14,
                            border_radius=8,
                            bgcolor="#ffffff",
                            border=f.border.all(1, "#e5e7eb"),
                            content=f.Text(
                                value="Seu histórico de cálculo está vazio!",
                                size=15,
                                color="#374151",
                                weight="bold",
                            ),
                        )
                    ],
                ),
            ),
        )

    page.open(result_dialog)


def share_clicked(page: f.Page):
    dlg = f.AlertDialog(
        shape=f.RoundedRectangleBorder(radius=5),
        icon=f.Icon(f.Icons.SHARE),
        title=f.Text("Compartilhamento em desenvolvimento", size=16),
        actions=[f.TextButton("Fechar", on_click=lambda _: page.close(dlg))],
    )
    page.open(dlg)


def i_clicked(page: f.Page):
    dlg = f.AlertDialog(
        shape=f.RoundedRectangleBorder(radius=5),
        icon=f.Icon(f.Icons.INFO),
        title=f.Text("Como usar a calculadora", size=18, color="#2c2c54", weight=f.FontWeight.BOLD),
        content=f.Text(txt_info_calc, size=16, width=700),
        actions=[f.TextButton("Fechar", on_click=lambda _: page.close(dlg))],
    )
    page.open(dlg)
