import flet as ft
import time
from entity.adlicenceview import Adlicenceview
from entity.calc import Calc
from entity.configview import ConfigView
from entity.notifications import Notifications
from config.config import carregar_configuracoes
from config.config_manager import ConfigManager


def build_splash():
    return ft.Container(
        expand=True,
        alignment=ft.alignment.center,
        bgcolor="#f8fafc",
        content=ft.Column(
            tight=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=18,
            controls=[
                ft.Container(
                    width=132,
                    height=132,
                    padding=16,
                    border_radius=28,
                    bgcolor="#ffffff",
                    shadow=ft.BoxShadow(blur_radius=18, color="#9ca3af"),
                    content=ft.Image(src="icon.png", fit=ft.ImageFit.CONTAIN),
                ),
                ft.Column(
                    tight=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                    controls=[
                        ft.Text("Galvanos Calc", size=24, weight=ft.FontWeight.BOLD, color="#1f2937"),
                        ft.Text("Preparando sua calculadora", size=13, color="#6b7280"),
                    ],
                ),
                ft.ProgressRing(width=28, height=28, stroke_width=3, color="INDIGO"),
            ],
        ),
    )


def reload_app(page: ft.Page):
    #Recarrega tudo
    print("Reload App")
    if page.route == "/refresh_view":
        page.route = "/calc"
    page.controls.clear()  # Limpa todos os controles da página
    main(page) # Chama a função principal para reconstruir a UI
    page.update()  # Atualiza a página para exibir as mudanças

def main(page: ft.Page):
    #page.client_storage.clear()
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.bgcolor = ft.Colors.TRANSPARENT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.decoration = ft.BoxDecoration(
        image=ft.DecorationImage(
            src="bgb.jpg",
            fit=ft.ImageFit.COVER,
        )
    )

    splash = build_splash()
    page.add(splash)
    page.update()
    time.sleep(1.2)

    config = ConfigManager(page)

    # Sincroniza dados persistentes
    config.sync_to_xml()

    page.controls.clear()
    views = {}

    def sync_remote_config():
        config.sincronizar_status_licenca()
        config.sync_to_xml()

    def newpage_route(route):
        page.views.clear()
        calc_view = None
        notifications_view = None

        if page.route == "/":
            adlicencepage = views.get("adlicencepage")
            if adlicencepage is None:
                adlicencepage = Adlicenceview(page)
                views["adlicencepage"] = adlicencepage
            page.views.append(adlicencepage)

        elif page.route == "/calc":
            calc = views.get("calc")
            if calc is None:
                calc = Calc(page)
                views["calc"] = calc
            calc_view = calc
            page.views.append(calc)

        elif page.route == "/configview":
            configview = views.get("configview")
            if configview is None:
                configview = ConfigView(page)
                views["configview"] = configview
            page.views.append(configview)

        elif page.route == "/refresh_view":
            calc = views.get("calc")
            if calc is None:
                calc = Calc(page)
                views["calc"] = calc
            calc_view = calc
            page.views.append(calc)
            reload_app(page)

        elif page.route == "/notifications":
            notifications_view = Notifications(page)
            page.views.append(notifications_view)
        page.update()

        if calc_view is not None:
            calc_view.start_background_refresh()
        elif notifications_view is not None:
            notifications_view.start_background_load()

    def new_view(e):
        if len(page.views) > 1:
            page.views.pop()
            page.go(page.views[-1].route)

    page.on_route_change = newpage_route
    page.on_view_pop = new_view
    page.go(page.route)
    page.run_thread(sync_remote_config)


if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")

