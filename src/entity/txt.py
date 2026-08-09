# [ MODULO TXT ]
# [ VERSION 0.1.2 ]
# [ CREATED BY Romero Souza ] DATE: 26/05/2025

from pydoc import TextDoc

set_language = "pt-br"

# Textos gerais da interface
title = """REPARO EXTERNO DE COMPONENTES AERONÁUTICOS"""
title_container_one = """MANUAIS DE MANUTENÇÃO"""
description_container_one = """Acessos recentes"""
title_container_two = """GALVANOPLASTIA E ELETRODEPOSIÇÃO"""

description_container_two = """
A. The main landing gear leg has a sliding tube subassembly that operates in a main fitting subassembly. The sliding tube subassembly operates through a lower bearing subassembly. The lower bearing subassembly also seals the sliding tube subassembly in the main fitting subassembly.
B. An upper torque link subassembly attaches to the main fitting subassembly. A lower torque link subassembly attaches to the sliding tube subassembly. A damper attaches to the upper torque link subassembly. A pin installs through the damper and connects the upper and lower torque link subassemblies.
C. A slave link subassembly and a lower slave link subassembly attach opposite the upper and lower torque link subassemblies.
D. A rod and a cylinder install in the sliding tube subassembly. A piston installs in the cylinder. An upper diaphragm tube subassembly installs in the main fitting subassembly. A baffle, a compression orifice plate and a diaphragm install in the upper diaphragm tube subassembly. The rod goes through the baffle.
E. An upper bearing housing installs between the top of the sliding tube subassembly and the main fitting subassembly. A recoil orifice plate operates in the upper bearing housing.
"""

txt_info_use_program = """Informações importantes de uso do aplicativo."""
veri_cadastro = """Verificação dos dados do cadastro. Use os botões ao lado para editar ou sair."""

# Textos da pesquisa
search_text = """Veja detalhes do componente a ser reparado pelo seu PN"""
txt_validate_no = """Não há resultados a exibir para:"""
txt_validate_ok = """Existe um cadastro no banco de dados com o resultado:"""
txt_validate_ok_pre = """Ao digitar no campo de pesquisa, observe as sugestões trazidas do banco de dados e toque para visualizar."""
txt_hint_text = "Pesquise por Part Number..."
txt_btn_list = "Listar todos"
txt_tootip_list = "Exibe a lista de todos os componentes"
txt_exit_window = "Sair desta janela"
txt_save_pdf = "Gerar PDF"

# Textos da calculadora
txt_info_calc = """Escolha o tipo de processo antes de calcular. O padrão é Cromo.

Informe o comprimento, o diâmetro e a quantidade de peças. Comprimento e diâmetro devem estar em milímetros. Você pode usar números inteiros ou decimais com vírgula ou ponto, como 12,5 ou 12.5.

Use [Adicionar à lista] quando quiser somar várias medidas antes do cálculo. Se houver peças iguais, digite a medida uma vez e informe a quantidade. Ao finalizar a lista, toque em [Calcular medidas] para obter a área total em dm² e a amperagem indicada.

Para calcular uma única medida, preencha os campos e toque diretamente em [Calcular medidas]."""

txt_sobre = "O GCalc facilita o cálculo de área em dm² para processos galvânicos, mostrando a área total e a amperagem indicada conforme os parâmetros configurados para cada processo."

# Textos da pesquisa de manuais
txt_hint_text_manual = "Pesquise por número de manual..."
search_text_manual = "Resultados encontrados para esta pesquisa"


class SetTranslateStr(TextDoc):
    def __init__(self, translate: str):
        self.translate = translate


def set_language_all(e):
    if set_language != "pt-br":
        print("language set 'english'")
        SetTranslateStr(e)
    else:
        print("language 'Português-br'")
