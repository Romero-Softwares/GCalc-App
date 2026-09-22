import flet as f
from entity.txt import txt_sobre
from config.config import carregar_configuracoes
from entity.card_style import card_border, card_shadow
import xml.etree.ElementTree as ET
from decimal import Decimal, InvalidOperation, ROUND_DOWN, ROUND_HALF_UP
from entity.dialogs import reload_app, get_listmed

class Containercalc(f.Container):
    def __init__(self, page: f.Page):
        super().__init__()
        self.itemlist = ""
        self.page = page
        self.col = {'sm': 5.90}
        self.page.scroll = f.ScrollMode.HIDDEN
        self.bgcolor = f.Colors.with_opacity(0.10, 'white')
        self.padding = f.padding.only(
            top=15,
            left=15,
            right=15,
            bottom=20
        )
        global itemlist
        self.border_radius = 8
        self.pi = Decimal("3.141592653589793") / Decimal("10000")
        self.cont = []

        self.calcular = f.ElevatedButton("Calcular medidas", icon=f.Icons.AREA_CHART_SHARP, disabled=False,
                                     style=f.ButtonStyle(shape=f.RoundedRectangleBorder(radius=5)),
                                     on_click=lambda _: processVals(),
                                     elevation=10)
        self.btns_add_calculate = f.Row(
            controls=[
                f.ElevatedButton("Adicionar à lista", icon=f.Icons.ADD_TO_QUEUE, disabled=False,
                                 style=f.ButtonStyle(shape=f.RoundedRectangleBorder(radius=5)),
                                 on_click=lambda _: addListMed(),
                                 elevation=10),
                self.calcular
            ]
        )

        self.btns_listmed = f.Row(
            visible=False,
            controls=[
                f.ElevatedButton("Ver medidas", icon=f.Icons.LIST, disabled=False,
                             style=f.ButtonStyle(shape=f.RoundedRectangleBorder(radius=5)),
                             on_click=lambda _: get_listmed(page),
                             elevation=10),
            f.ElevatedButton("Apagar lista", icon=f.Icons.CLEAR_ALL, disabled=False,
                             style=f.ButtonStyle(shape=f.RoundedRectangleBorder(radius=5)),
                             on_click=lambda _: listmed_clear_confirm(),
                             elevation=10)

        ])

        self.informations = f.Container(
            padding=10,
            bgcolor="#FFFFFF",
            border_radius=10,
            border=card_border(),
            shadow=card_shadow(),
            visible=True,

            content=f.Column([
                f.Text("Sobre esta ferramenta", size=18, color="ORANGE"),
                f.Column([
                    f.Text(value=f"{txt_sobre}", size=16),

                ]),

                f.FilledTonalButton("Ok", bgcolor="INDIGO", elevation=10, color="#FFFFFF",
                                    on_click=self.closeInformations)
            ])

        )

        saved_config = carregar_configuracoes('config/config.xml') or {}
        process_options = {"Cromo", "Cádmio", "Níquel"}
        selected_process = saved_config.get("tipo_processo", "Cromo")
        if selected_process not in process_options:
            selected_process = "Cromo"

        def save_process_selection(e):
            try:
                tree = ET.parse('config/config.xml')
                root = tree.getroot()
                process_element = root.find('tipo_processo')
                if process_element is None:
                    process_element = ET.SubElement(root, 'tipo_processo')
                process_element.text = e.control.value
                tree.write('config/config.xml')
            except Exception as error:
                print(f"Não foi possível salvar o tipo de processo: {error}")

        self.opt = f.Dropdown(
            label="Tipo de processo",
            width=250,
            hint_text="Escolha de processo",
            suffix="Cromo", prefix_icon=f.Icons.TRACK_CHANGES_ROUNDED,
            options=([
                f.dropdown.Option("Cromo"),
                f.dropdown.Option("Cádmio"),
                f.dropdown.Option("Níquel")
            ]),
            autofocus=True,
            options_fill_horizontally=True,
            value=selected_process,
            on_change=save_process_selection,
        )

        # End Dropdown options

        measure_filter = f.InputFilter(regex_string=r"^[0-9]*([,.][0-9]*)?$")
        quantity_filter = f.InputFilter(regex_string=r"^[0-9]*$")

        entry1 = f.TextField(
            label='Comprimento (mm)',
            prefix_icon=f.Icons.PIN,
            text_align=f.TextAlign.LEFT,
            bgcolor='#ffffff',
            color='#006266',
            hint_text="Ex.: 120 ou 120,5",
            input_filter=measure_filter,
            keyboard_type=f.KeyboardType.NUMBER,
        )
        entry2 = f.TextField(
            label='Diâmetro (mm)',
            prefix_icon=f.Icons.PIN,
            text_align=f.TextAlign.LEFT,
            bgcolor='#ffffff',
            color='#006266',
            hint_text="Ex.: 35 ou 35,5",
            input_filter=measure_filter,
            keyboard_type=f.KeyboardType.NUMBER,
        )
        unit_help = f.Text(
            "Conversões e cálculos mantêm quatro casas decimais.",
            size=12,
            color="#4b5563",
        )

        def update_measurement_unit(e):
            if e.control.value == "in":
                entry1.label = "Comprimento (in)"
                entry2.label = "Diâmetro (in)"
                entry1.hint_text = "Ex.: 4,75 ou 4.75"
                entry2.hint_text = "Ex.: 1,38 ou 1.38"
                unit_help.value = "As polegadas são convertidas para milímetros com quatro casas decimais."
            else:
                entry1.label = "Comprimento (mm)"
                entry2.label = "Diâmetro (mm)"
                entry1.hint_text = "Ex.: 120 ou 120,5"
                entry2.hint_text = "Ex.: 35 ou 35,5"
                unit_help.value = "Conversões e cálculos mantêm quatro casas decimais."
            self.page.update()

        measurement_unit = f.RadioGroup(
            value="mm",
            on_change=update_measurement_unit,
            content=f.Row(
                controls=[
                    f.Radio(value="mm", label="Milímetros (mm)"),
                    f.Radio(value="in", label="Polegadas (in)"),
                ],
                spacing=12,
            ),
        )

        self.content = f.Column(
            controls=[
                self.opt,
                f.Text("Unidade de entrada", size=14, weight=f.FontWeight.W_500),
                measurement_unit,
                unit_help,
                entry1,
                entry2,

                entry3 := f.TextField(label='Quantidade', prefix_icon=f.Icons.FORMAT_LIST_NUMBERED,
                                      text_align=f.TextAlign.LEFT, bgcolor='#ffffff', color='#006266',
                                      value="1",
                                      hint_text="Ex.: 1, 5 ou 12",
                                      input_filter=quantity_filter,
                                      keyboard_type=f.KeyboardType.NUMBER),

                self.btns_add_calculate, self.btns_listmed, self.informations
            ])

        def parse_measure(value):
            text = (value or "").strip().replace(",", ".")
            if not text:
                raise ValueError("empty")
            try:
                parsed = Decimal(text)
            except InvalidOperation as error:
                raise ValueError("invalid") from error
            if parsed <= 0:
                raise ValueError("non-positive")
            return calculate(parsed * Decimal("25.4")) if measurement_unit.value == "in" else parsed

        def parse_quantity(value):
            text = (value or "1").strip()
            if not text:
                text = "1"
            parsed = int(text)
            if parsed <= 0:
                raise ValueError("non-positive")
            return parsed

        def calculate(value):
            return Decimal(value).quantize(Decimal("0.0001"), rounding=ROUND_DOWN)

        def fmt_number(value, digits=4):
            return f"{value:.{digits}f}".replace(".", ",")

        def fmt_integer(value):
            return f"{Decimal(value).quantize(Decimal('1'), rounding=ROUND_HALF_UP):.0f}"

        def fmt_amperage(value):
            return f"{Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):.2f}".replace(".", ",")

        def format_total_area(area_dm2):
            area_in2 = calculate(area_dm2 * Decimal("15.500031000062"))
            area_ft2 = calculate(area_dm2 * Decimal("0.107639104167"))
            return (
                f"{fmt_number(area_dm2)} dm²\n"
                f"{fmt_number(area_in2)} in²\n"
                f"{fmt_number(area_ft2)} ft²"
            )

        def update_listmed():
            tree = ET.parse('config/config.xml')
            root = tree.getroot()
            lista = root.findall('listmed/valor')
            cont = len(lista)
            if cont > 0:
                self.btns_listmed.visible = True
        update_listmed()

        def clear_listmed():
            print('Clear listMed')
            try:
                tree = ET.parse('config/config.xml')
                root = tree.getroot()
                for aria in root.findall('listmed'):
                    root.remove(aria)
                    print("Elemento 'aria' removido.")

                tree.write('config/config.xml')
                self.btns_listmed.visible = False
                self.cont = []
            except:
                print('Um erro impediu o processamento.')
            self.page.update()

        def resposta_confirmacao(e):
            if e.control.text == "Sim":
                clear_listmed()
            self.page.close(dlg_confirmacao)

        dlg_confirmacao = f.AlertDialog(
            title=f.Text(" ", size=18, color="amber"),
            content=f.Text(' '),
            shape=f.RoundedRectangleBorder(radius=5),
            actions=[]
        )

        def listmed_clear_confirm():
            dlg_confirmacao.title = f.Text("Por favor, confirme", size=18, color="amber")
            dlg_confirmacao.content = f.Container(
                width=300, height=80, border_radius=4, bgcolor="transparent",
                shadow=card_shadow(),
                image=f.DecorationImage(
                    opacity=0.3, src="paquimetro.webp", fit=f.ImageFit.COVER),
                content=f.Column(
                    controls=[f.Text(value="Tem certeza de que deseja apagar a lista de medidas salvas ?", size=16, weight='bold')]),
                padding=10)
            dlg_confirmacao.actions = [
                f.TextButton("Sim", on_click=resposta_confirmacao),
                f.TextButton("Não", on_click=lambda _: self.page.close(dlg_confirmacao))
            ]
            tree = ET.parse('config/config.xml')
            root = tree.getroot()
            aria = root.findall('listmed')
            if not aria:
                dlg_confirmacao.title = f.Text("dados foram apagados")
                dlg_confirmacao.content = f.Text("a lista está vazia")
                dlg_confirmacao.actions = [f.TextButton("Ok", on_click=lambda _: self.page.close(dlg_confirmacao))]
            self.page.open(dlg_confirmacao)
            self.page.update()

        def addListMed():
            print("addlist")
            try:
                num1 = parse_measure(entry1.value)
                num2 = parse_measure(entry2.value)
                qtd = parse_quantity(entry3.value)
                mp_unit = calculate(num1 * num2)
                mp = calculate(mp_unit * qtd)
                self.pre_aria = f"{calculate(mp * self.pi)}"

                self.cont.append(mp)

            except:
                snackbar = f.SnackBar(
                    f.Text("Preencha comprimento, diâmetro e quantidade com valores maiores que zero.", color=f.Colors.YELLOW_ACCENT_700))
                self.page.controls.append(snackbar)
                snackbar.open = True
                self.alertDialog()

            else:
                try:
                    tree = ET.parse("config/config.xml")
                    root = tree.getroot()

                    listmed = ET.SubElement(root, 'listmed')
                    cont = len(root.findall('listmed'))
                    aria = fmt_number(calculate(mp * self.pi))
                    aria_unit = fmt_number(calculate(mp_unit * self.pi))
                    # Append new data
                    new_item = ET.SubElement(listmed, "aria")
                    ET.SubElement(listmed, "aria_unitaria").text = aria_unit
                    ET.SubElement(listmed, "cumprimento").text = fmt_number(num1)
                    ET.SubElement(listmed, "diametro").text = fmt_number(num2)
                    ET.SubElement(listmed, "quantidade").text = str(qtd)
                    new_value = ET.SubElement(listmed, "valor")
                    new_id = ET.SubElement(listmed, "id")
                    new_id.text = f"{cont}"
                    new_item.text = f"{aria}"
                    new_value.text = f"{mp:.4f}"

                    # Save the changes back to the file
                    tree.write('config/config.xml')
                    self.btns_listmed.visible = True
                    entry1.value = ''
                    entry2.value = ''
                    entry3.value = '1'
                except:
                    print("Erro ao processar a adição na lista!")

                self.pre_aria = "{}x - Comprimento: {} mm - Diâmetro: {} mm\nÁrea unitária: {} dm²\nÁrea total: {} dm²".format(
                    qtd, fmt_integer(num1), fmt_integer(num2), fmt_number(calculate(mp_unit * self.pi)), fmt_number(calculate(mp * self.pi))
                )
                self.results = f.AlertDialog(
                    content_padding=0,
                    shape=f.RoundedRectangleBorder(radius=10),
                    bgcolor="#f8fafc",
                    title_padding=f.Padding(18, 14, 8, 0),
                    title=f.Row(
                        alignment=f.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            f.Text("Medida adicionada", color="#1f2937", size=18, weight=f.FontWeight.BOLD),
                            f.IconButton(
                                f.Icons.CLOSE_ROUNDED,
                                icon_color="#ef4444",
                                on_click=lambda _: self.page.close(self.results),
                            ),
                        ],
                    ),
                    content=f.Container(
                        width=380,
                        padding=f.Padding(18, 8, 18, 12),
                        content=f.Column(
                            tight=True,
                            spacing=12,
                            controls=[
                                f.Container(
                                    padding=12,
                                    border_radius=8,
                                    bgcolor="#ffffff",
                                    border=card_border(),
                                    shadow=card_shadow(),
                                    content=f.Column(
                                        spacing=8,
                                        controls=[
                                            f.Row(
                                                alignment=f.MainAxisAlignment.SPACE_BETWEEN,
                                                controls=[
                                                    f.Text("Quantidade", size=12, color="#6b7280"),
                                                    f.Text(f"{qtd} peça(s)", size=14, color="#111827", weight=f.FontWeight.BOLD),
                                                ],
                                            ),
                                            f.Row(
                                                alignment=f.MainAxisAlignment.SPACE_BETWEEN,
                                                controls=[
                                                    f.Text("Comprimento", size=12, color="#6b7280"),
                                                    f.Text(f"{fmt_integer(num1)} mm", size=14, color="#111827"),
                                                ],
                                            ),
                                            f.Row(
                                                alignment=f.MainAxisAlignment.SPACE_BETWEEN,
                                                controls=[
                                                    f.Text("Diâmetro", size=12, color="#6b7280"),
                                                    f.Text(f"{fmt_integer(num2)} mm", size=14, color="#111827"),
                                                ],
                                            ),
                                        ],
                                    ),
                                ),
                                f.Row(
                                    spacing=10,
                                    controls=[
                                        f.Container(
                                            expand=True,
                                            padding=12,
                                            border_radius=8,
                                            bgcolor="#eef2ff",
                                            border=card_border("#c7d2fe"),
                                            shadow=card_shadow(),
                                            content=f.Column(
                                                spacing=3,
                                                controls=[
                                                    f.Text("Área unitária", size=12, color="#4f46e5"),
                                                    f.Text(f"{fmt_number(calculate(mp_unit * self.pi))} dm²", size=16, color="#1e1b4b", weight=f.FontWeight.BOLD),
                                                ],
                                            ),
                                        ),
                                        f.Container(
                                            expand=True,
                                            padding=12,
                                            border_radius=8,
                                            bgcolor="#ecfdf5",
                                            border=card_border("#a7f3d0"),
                                            shadow=card_shadow(),
                                            content=f.Column(
                                                spacing=3,
                                                controls=[
                                                    f.Text("Área total", size=12, color="#047857"),
                                                    f.Text(format_total_area(calculate(mp * self.pi)), size=16, color="#064e3b", weight=f.FontWeight.BOLD),
                                                ],
                                            ),
                                        ),
                                    ],
                                ),
                                f.Image(
                                    src="paquimetro.webp",
                                    width=344,
                                    height=90,
                                    fit=f.ImageFit.COVER,
                                    border_radius=8,
                                ),
                            ],
                        ),
                    ),
                )
                self.results.open = True
                self.page.overlay.append(self.results)
                self.page.update()

        # End addlistMed

        def processVals():
            print("processVals")
            config = carregar_configuracoes('config/config.xml')
            self.stCd = config['stCd']
            self.stCr = config['stCr']
            self.stRe = config['stRe']
            self.stNq = config['stNq']
            tree = ET.parse('config/config.xml')
            root = tree.getroot()
            list_items = root.findall('listmed')
            lista = root.findall('listmed/valor')
            cont = len(list_items)
            total_qtd = 0
            measurement_entries = []

            def result_metric(label, value, bgcolor, label_color, value_color, expand=True):
                return f.Container(
                    expand=expand,
                    padding=12,
                    border_radius=8,
                    bgcolor=bgcolor,
                    border=card_border(),
                    shadow=card_shadow(),
                    content=f.Column(
                        tight=True,
                        spacing=3,
                        controls=[
                            f.Text(label, size=12, color=label_color),
                            f.Text(value, size=17, color=value_color, weight=f.FontWeight.BOLD),
                        ],
                    ),
                )

            try:
                if cont < 1:
                    num1 = parse_measure(entry1.value)
                    num2 = parse_measure(entry2.value)
                    qtd = parse_quantity(entry3.value)
                    soma = calculate(calculate(num1 * num2) * qtd)
                    total_qtd = qtd
                    cont = 1
                    measurement_entries.append((num1, num2, qtd, calculate(soma * self.pi)))
                    entry1.value = ''
                    entry2.value = ''
                    entry3.value = '1'
                else:
                    listmed = []
                    if cont > 0:
                        for i in lista:
                            listmed.append(i.text)
                        for item in list_items:
                            qtd_item = item.find('quantidade')
                            comprimento_item = item.find('cumprimento')
                            diametro_item = item.find('diametro')
                            qtd_salva = int(qtd_item.text) if qtd_item is not None and qtd_item.text else 1
                            comprimento = Decimal(comprimento_item.text.replace(',', '.')) if comprimento_item is not None and comprimento_item.text else Decimal("0")
                            diametro = Decimal(diametro_item.text.replace(',', '.')) if diametro_item is not None and diametro_item.text else Decimal("0")
                            area_item = calculate(Decimal(item.find('valor').text) * self.pi)
                            total_qtd += qtd_salva
                            measurement_entries.append((comprimento, diametro, qtd_salva, area_item))

                        soma = Decimal(listmed[0])
                        for i in range(1, len(listmed)):
                            soma = calculate(soma + Decimal(listmed[i]))

                print("Área do cálculo: ", soma)
                aria = calculate(soma * self.pi)
                self.cont = []
                measurement_summary = "\n".join(
                    f"Entrada {index}: {fmt_integer(comprimento)} mm x {fmt_integer(diametro)} mm | "
                    f"{quantidade} peça(s) | {fmt_number(area_item)} dm²"
                    for index, (comprimento, diametro, quantidade, area_item) in enumerate(measurement_entries, start=1)
                )
                let = self.opt.value
                total_aria = f"Área total:\n{format_total_area(aria)}"
                area_blocks = [
                    ("dm²", fmt_number(aria)),
                    ("in²", fmt_number(calculate(aria * Decimal("15.500031000062")))),
                    ("ft²", fmt_number(calculate(aria * Decimal("0.107639104167")))),
                ]
                process_name = let or "Cádmio"
                bath_amp = None
                reverse_amp = None
                base_calc = None
                reverse_base = None
                if let == "Cádmio" or let == None:
                    amper = calculate(aria * Decimal(str(self.stCd)))  # para cadmio
                    bath_amp = amper
                    base_calc = Decimal(str(self.stCd))
                    self.saida = ("Processo: (Cádmio) \n" + "Amperagem: [{}]".format(fmt_amperage(amper)) + "\nItens: " + str(
                        cont) + "\nPeças: " + str(total_qtd) + "\nMedidas inseridas:\n" + measurement_summary +
                                  "\nBase de cálculo: ({}) amp por dm²".format(fmt_integer(base_calc)))
                elif let == "Cromo":
                    amper = calculate(aria * Decimal(str(self.stCr)))  # para cromo
                    reverso = calculate(aria * Decimal(str(self.stRe)))
                    bath_amp = amper
                    reverse_amp = reverso
                    base_calc = Decimal(str(self.stCr))
                    reverse_base = Decimal(str(self.stRe))
                    self.saida = ('Processo: (Cromo) \n' + ""
                                                           "Amperagem banho: [{}] \nAmperagem reversão: [{}]"
                                                           "".format(fmt_amperage(amper), fmt_amperage(reverso)) + "\nItens: "
                                  + str(cont) + "\nPeças: " + str(total_qtd) + "\nMedidas inseridas:\n" + measurement_summary +
                                  "\nBase de cálculo: ({}) amp por dm²".format(fmt_integer(base_calc)) +
                                  "\nSet de reversão: ({}) amp por dm² ".format(fmt_integer(reverse_base)))
                else:
                    amper = calculate(aria * Decimal(str(self.stNq)))  # para níquel
                    process_name = "Níquel"
                    bath_amp = amper
                    base_calc = Decimal(str(self.stNq))
                    self.saida = ("Processo: (Níquel) \n" + "Amperagem: {}".format(fmt_amperage(amper)) + "\nItens: " + str(
                        cont) + "\nPeças: " + str(total_qtd) + "\nMedidas inseridas:\n" + measurement_summary +
                                  "\nBase de cálculo: ({}) amp por dm²".format(fmt_integer(base_calc)))
            except:
                snackbar = f.SnackBar(
                    f.Text("Preencha comprimento, diâmetro e quantidade com valores maiores que zero.", size=16,
                           color=f.Colors.YELLOW_ACCENT_700))
                self.page.overlay.append(snackbar)
                snackbar.open = True
                self.alertDialog()
            else:
                if config['active'] == "True":
                    clear_listmed()
                    amp_cards = [
                        result_metric("Amperagem banho", f"{fmt_amperage(bath_amp)} A", "#eef2ff", "#4f46e5", "#1e1b4b"),
                    ]
                    if reverse_amp is not None:
                        amp_cards.append(
                            result_metric("Amperagem reversão", f"{fmt_amperage(reverse_amp)} A", "#fff7ed", "#c2410c", "#7c2d12")
                        )

                    base_cards = [
                        result_metric("Itens", str(cont), "#f9fafb", "#6b7280", "#111827"),
                        result_metric("Peças", str(total_qtd), "#f9fafb", "#6b7280", "#111827"),
                        result_metric("Base banho", f"{fmt_integer(base_calc)} A/dm²", "#f9fafb", "#6b7280", "#111827"),
                    ]
                    if reverse_base is not None:
                        base_cards.append(
                            result_metric("Base reversão", f"{fmt_integer(reverse_base)} A/dm²", "#f9fafb", "#6b7280", "#111827")
                        )

                    measurement_rows = [
                        f.Container(
                            padding=10,
                            border_radius=6,
                            bgcolor="#f8fafc",
                            border=card_border("#e2e8f0"),
                            shadow=card_shadow(),
                            content=f.Column(
                                tight=True,
                                spacing=2,
                                controls=[
                                    f.Text(
                                        f"Entrada {index}: {fmt_integer(comprimento)} mm x {fmt_integer(diametro)} mm",
                                        size=13,
                                        color="#111827",
                                        no_wrap=False,
                                    ),
                                    f.Text(
                                        f"{quantidade} peça(s) · {fmt_number(area_item)} dm²",
                                        size=12,
                                        color="#4b5563",
                                        no_wrap=False,
                                    ),
                                ],
                            ),
                        )
                        for index, (comprimento, diametro, quantidade, area_item) in enumerate(measurement_entries, start=1)
                    ]

                    self.result = f.AlertDialog(
                        content_padding=0,
                        inset_padding=f.Padding(10, 24, 10, 24),
                        shape=f.RoundedRectangleBorder(radius=10),
                        bgcolor="#f8fafc",
                        title_padding=f.Padding(18, 14, 8, 0),
                        title=f.Row(
                            alignment=f.MainAxisAlignment.SPACE_BETWEEN,
                            controls=[
                                f.Text("Resultado do cálculo", color="#1f2937", size=18, weight=f.FontWeight.BOLD),
                                f.IconButton(
                                    f.Icons.CLOSE_ROUNDED,
                                    icon_color="#ef4444",
                                    on_click=lambda _: self.page.close(self.result),
                                ),
                            ],
                        ),
                        content=f.Container(
                            width=420,
                            height=min(560, max(260, (self.page.height or 720) - 140)),
                            padding=f.Padding(18, 8, 18, 14),
                            content=f.Column(
                                expand=True,
                                scroll=f.ScrollMode.HIDDEN,
                                spacing=12,
                                controls=[
                                    f.Container(
                                        padding=14,
                                        border_radius=8,
                                        bgcolor="#ffffff",
                                        border=card_border(),
                                        shadow=card_shadow(),
                                        content=f.Row(
                                            spacing=10,
                                            vertical_alignment=f.CrossAxisAlignment.START,
                                            controls=[
                                                f.Container(
                                                    expand=True,
                                                    height=172,
                                                    padding=12,
                                                    border_radius=7,
                                                    bgcolor="#f8fafc",
                                                    border=card_border("#e2e8f0"),
                                                    shadow=card_shadow(),
                                                    content=f.Column(
                                                        alignment=f.MainAxisAlignment.CENTER,
                                                        tight=True,
                                                        spacing=3,
                                                        controls=[
                                                            f.Text("Processo", size=12, color="#6b7280"),
                                                            f.Text(process_name, size=18, color="#111827", weight=f.FontWeight.BOLD),
                                                        ],
                                                    ),
                                                ),
                                                f.Column(
                                                    tight=True,
                                                    spacing=8,
                                                    controls=[
                                                        f.Container(
                                                            width=150,
                                                            height=52,
                                                            padding=f.Padding(10, 6, 10, 6),
                                                            border_radius=7,
                                                            bgcolor="#eef2ff",
                                                            border=card_border("#c7d2fe"),
                                                            shadow=card_shadow(),
                                                            content=f.Row(
                                                                alignment=f.MainAxisAlignment.SPACE_BETWEEN,
                                                                vertical_alignment=f.CrossAxisAlignment.CENTER,
                                                                controls=[
                                                                    f.Text(f"Área {unit}", size=12, color="#4f46e5"),
                                                                    f.Text(value, size=16, color="#1e1b4b", weight=f.FontWeight.BOLD),
                                                                ],
                                                            ),
                                                        )
                                                        for unit, value in area_blocks
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ),
                                    f.Row(spacing=10, controls=amp_cards),
                                    f.Row(spacing=8, controls=base_cards),
                                    f.Container(
                                        padding=12,
                                        border_radius=8,
                                        bgcolor="#ffffff",
                                        border=card_border(),
                                        shadow=card_shadow(),
                                        content=f.Column(
                                            tight=True,
                                            spacing=8,
                                            controls=[
                                                f.Text(
                                                    f"Medidas inseridas ({cont} entrada(s) / {total_qtd} peça(s))",
                                                    size=14,
                                                    color="#111827",
                                                    weight=f.FontWeight.BOLD,
                                                ),
                                                f.Column(controls=measurement_rows, spacing=6, tight=True),
                                            ],
                                        ),
                                    ),
                                ],
                            ),
                        ),
                    )
                    try:
                        self.XML_FILE = "config/config.xml"
                        tree = ET.parse(self.XML_FILE)
                        root = tree.getroot()
                        root.find('historico/aria_total').text = total_aria
                        root.find('historico/saida').text = self.saida
                        tree.write(self.XML_FILE)
                        print(config['saida'])
                    except:
                        print("não foi possivel armazenar os dados, erro desconhecido!")
                else:
                    self.result = f.AlertDialog(
                        shape=f.RoundedRectangleBorder(radius=5),
                        title=f.Text("Aplicativo em modo de teste", color='amber', size=18),
                        content=f.Text("Ative o aplicativo para liberar todas as funcionalidades!"),
                        actions=[f.TextButton("Fechar", on_click=lambda _: self.page.close(self.result))]
                    )
                self.result.open = True
                self.page.overlay.append(self.result)
            self.page.update()

        #Mensagem sobre os inputs e itens da lista
        self.dlg_list_calc = f.TextButton("Calcular", on_click=lambda _: processVals(), visible=False)
        self.itemlist = f.Text("", size=16, visible=False)
        self.dlg_list = f.AlertDialog(
            shape=f.RoundedRectangleBorder(radius=5),
            icon_color='RED',
            icon=f.Icon(f.Icons.WARNING),
            title=f.Column([f.Text("Preencha todos os campos corretamente! ", size=16), self.itemlist]),
            actions=[
                self.dlg_list_calc,
                f.TextButton("Fechar", on_click=lambda _: self.page.close(self.dlg_list)),
            ],
            open=False,
        )

    def alertDialog(self):  # Alert dialog local message
        tree = ET.parse('config/config.xml')
        root = tree.getroot()
        lista = root.findall('listmed/valor')
        print("alert listmed")
        cont = len(lista)
        if cont == 1:
            self.itemlist.value = "há um dado salvo a ser calculado"
            self.itemlist.visible = True
            self.dlg_list_calc.visible = True

        elif cont > 1:
            self.itemlist.value = f"há {cont} dados salvos a serem calculados"
            self.itemlist.visible = True
            self.dlg_list_calc.visible = True

        elif cont < 1:
            self.itemlist.value = ""
            self.itemlist.visible = True
            self.dlg_list_calc.visible = False
        self.content.controls.append(self.dlg_list)
        self.dlg_list.open = True
        self.page.update()

    def closeInformations(self, e):
        self.informations.visible = False
        self.page.update()

