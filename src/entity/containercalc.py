import flet as f
from entity.txt import txt_sobre
from config.config import carregar_configuracoes
import xml.etree.ElementTree as ET
from entity.dialogs import reload_app, get_listmed

class Containercalc(f.Container):
    def __init__(self, page: f.Page):
        super().__init__()
        self.itemlist = ""
        self.page = page
        self.col = {'sm': 5.90}
        self.page.scroll = True
        self.bgcolor = f.Colors.with_opacity(0.10, 'white')
        self.padding = f.padding.only(
            top=15,
            left=15,
            right=15,
            bottom=20
        )
        global itemlist
        self.border_radius = 8
        self.pi = 3.141592653589793 / 10000
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
            shadow=f.BoxShadow(blur_radius=5, color="#777777"),
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
            value="Cromo",
        )

        # End Dropdown options

        measure_filter = f.InputFilter(regex_string=r"^[0-9]*([,.][0-9]*)?$")
        quantity_filter = f.InputFilter(regex_string=r"^[0-9]*$")

        self.content = f.Column(
            controls=[
                self.opt,
                entry1 := f.TextField(label='Comprimento (mm)', prefix_icon=f.Icons.PIN,
                                      text_align=f.TextAlign.LEFT, bgcolor='#ffffff', color='#006266',
                                      hint_text="Ex.: 120 ou 120,5",
                                      input_filter=measure_filter,
                                      keyboard_type=f.KeyboardType.NUMBER),

                entry2 := f.TextField(label='Diâmetro (mm)', prefix_icon=f.Icons.PIN,
                                      text_align=f.TextAlign.LEFT, bgcolor='#ffffff', color='#006266',
                                      hint_text="Ex.: 35 ou 35,5",
                                      input_filter=measure_filter,
                                      keyboard_type=f.KeyboardType.NUMBER),

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
            parsed = float(text)
            if parsed <= 0:
                raise ValueError("non-positive")
            return parsed

        def parse_quantity(value):
            text = (value or "1").strip()
            if not text:
                text = "1"
            parsed = int(text)
            if parsed <= 0:
                raise ValueError("non-positive")
            return parsed

        def fmt_number(value, digits=2):
            return f"{value:.{digits}f}".replace(".", ",")

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
                mp_unit = num1 * num2
                mp = mp_unit * qtd
                self.pre_aria = f"{mp * self.pi}"

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
                    aria = fmt_number(mp * self.pi)
                    aria_unit = fmt_number(mp_unit * self.pi)
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
                    new_value.text = f"{mp}"

                    # Save the changes back to the file
                    tree.write('config/config.xml')
                    self.btns_listmed.visible = True
                    entry1.value = ''
                    entry2.value = ''
                    entry3.value = '1'
                except:
                    print("Erro ao processar a adição na lista!")

                self.pre_aria = "{}x - Comprimento: {} mm - Diâmetro: {} mm\nÁrea unitária: {} dm²\nÁrea total: {} dm²".format(
                    qtd, fmt_number(num1), fmt_number(num2), fmt_number(mp_unit * self.pi), fmt_number(mp * self.pi)
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
                                    border=f.border.all(1, "#e5e7eb"),
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
                                                    f.Text(f"{fmt_number(num1)} mm", size=14, color="#111827"),
                                                ],
                                            ),
                                            f.Row(
                                                alignment=f.MainAxisAlignment.SPACE_BETWEEN,
                                                controls=[
                                                    f.Text("Diâmetro", size=12, color="#6b7280"),
                                                    f.Text(f"{fmt_number(num2)} mm", size=14, color="#111827"),
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
                                            content=f.Column(
                                                spacing=3,
                                                controls=[
                                                    f.Text("Área unitária", size=12, color="#4f46e5"),
                                                    f.Text(f"{fmt_number(mp_unit * self.pi)} dm²", size=16, color="#1e1b4b", weight=f.FontWeight.BOLD),
                                                ],
                                            ),
                                        ),
                                        f.Container(
                                            expand=True,
                                            padding=12,
                                            border_radius=8,
                                            bgcolor="#ecfdf5",
                                            content=f.Column(
                                                spacing=3,
                                                controls=[
                                                    f.Text("Área total", size=12, color="#047857"),
                                                    f.Text(f"{fmt_number(mp * self.pi)} dm²", size=16, color="#064e3b", weight=f.FontWeight.BOLD),
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

            def result_metric(label, value, bgcolor, label_color, value_color, expand=True):
                return f.Container(
                    expand=expand,
                    padding=12,
                    border_radius=8,
                    bgcolor=bgcolor,
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
                    soma = (num1 * num2 * qtd)
                    total_qtd = qtd
                    cont = 1
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
                            total_qtd += int(qtd_item.text) if qtd_item is not None and qtd_item.text else 1

                        soma = float(listmed[0])
                        for i in range(1, len(listmed)):
                            soma = soma + float(listmed[i])

                print("Área do cálculo: ", soma)
                aria = soma * self.pi
                self.cont = []
                let = self.opt.value
                total_aria = "Área total: {} dm²".format(fmt_number(aria))
                process_name = let or "Cádmio"
                bath_amp = None
                reverse_amp = None
                base_calc = None
                reverse_base = None
                if let == "Cádmio" or let == None:
                    amper = aria * float(self.stCd)  # para cadmio
                    bath_amp = amper
                    base_calc = float(self.stCd)
                    self.saida = ("Processo: (Cádmio) \n" + "Amperagem: [{}]".format(fmt_number(amper)) + "\nItens: " + str(
                        cont) + "\nPeças: " + str(total_qtd) +
                                  "\nBase de cálculo: ({}) amp por dm²".format(fmt_number(float(self.stCd))))
                elif let == "Cromo":
                    amper = aria * int(self.stCr)  # para cromo
                    reverso = aria * int(self.stRe)
                    bath_amp = amper
                    reverse_amp = reverso
                    base_calc = int(self.stCr)
                    reverse_base = int(self.stRe)
                    self.saida = ('Processo: (Cromo) \n' + ""
                                                           "Amperagem banho: [{}] \nAmperagem reversão: [{}]"
                                                           "".format(fmt_number(amper), fmt_number(reverso)) + "\nItens: "
                                  + str(cont) + "\nPeças: " + str(total_qtd) +
                                  "\nBase de cálculo: ({}) amp por dm²".format(int(self.stCr)) +
                                  "\nSet de reversão: ({}) amp por dm² ".format(int(self.stRe)))
                else:
                    amper = aria * float(self.stNq)  # para níquel
                    process_name = "Níquel"
                    bath_amp = amper
                    base_calc = float(self.stNq)
                    self.saida = ("Processo: (Níquel) \n" + "Amperagem: {}".format(fmt_number(amper)) + "\nItens: " + str(
                        cont) + "\nPeças: " + str(total_qtd) +
                                  "\nBase de cálculo: ({}) amp por dm²".format(fmt_number(float(self.stNq))))
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
                        result_metric("Amperagem banho", f"{fmt_number(bath_amp)} A", "#eef2ff", "#4f46e5", "#1e1b4b"),
                    ]
                    if reverse_amp is not None:
                        amp_cards.append(
                            result_metric("Amperagem reversão", f"{fmt_number(reverse_amp)} A", "#fff7ed", "#c2410c", "#7c2d12")
                        )

                    base_cards = [
                        result_metric("Itens", str(cont), "#f9fafb", "#6b7280", "#111827"),
                        result_metric("Peças", str(total_qtd), "#f9fafb", "#6b7280", "#111827"),
                        result_metric("Base banho", f"{base_calc} A/dm²", "#f9fafb", "#6b7280", "#111827"),
                    ]
                    if reverse_base is not None:
                        base_cards.append(
                            result_metric("Base reversão", f"{reverse_base} A/dm²", "#f9fafb", "#6b7280", "#111827")
                        )

                    self.result = f.AlertDialog(
                        content_padding=0,
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
                                                        f.Text(process_name, size=18, color="#111827", weight=f.FontWeight.BOLD),
                                                    ],
                                                ),
                                                f.Column(
                                                    tight=True,
                                                    horizontal_alignment=f.CrossAxisAlignment.END,
                                                    spacing=3,
                                                    controls=[
                                                        f.Text("Área total", size=12, color="#4f46e5"),
                                                        f.Text(f"{fmt_number(aria)} dm²", size=20, color="#1e1b4b", weight=f.FontWeight.BOLD),
                                                    ],
                                                ),
                                            ],
                                        ),
                                    ),
                                    f.Row(spacing=10, controls=amp_cards),
                                    f.Row(spacing=8, controls=base_cards),
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

