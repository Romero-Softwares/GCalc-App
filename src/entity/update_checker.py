"""Consulta opcional de novas versões publicadas no GitHub Releases."""

from __future__ import annotations

import re
import threading

import flet as ft
import requests

from app_version import __version__


LATEST_RELEASE_URL = (
    "https://api.github.com/repos/Romero-Softwares/GCalc-App/releases/latest"
)
GOOGLE_PLAY_URL = "https://play.google.com/store/apps/details?id=com.merotecdev.gcalc"


def _version_key(value: str) -> tuple[int, ...] | None:
    """Converte tags como ``v0.1.7`` em uma chave comparável."""
    normalized = str(value).strip().lstrip("vV")
    numbers = re.findall(r"\d+", normalized)
    if not numbers:
        return None
    return tuple(int(number) for number in numbers)


def _is_newer(remote_version: str, local_version: str) -> bool:
    remote_key = _version_key(remote_version)
    local_key = _version_key(local_version)
    if remote_key is None or local_key is None:
        return False

    length = max(len(remote_key), len(local_key))
    remote_key += (0,) * (length - len(remote_key))
    local_key += (0,) * (length - len(local_key))
    return remote_key > local_key


class UpdateChecker:
    """Exibe um aviso quando existir uma GitHub Release mais recente."""

    def __init__(self, page: ft.Page):
        self.page = page
        self._shown = False
        self._lock = threading.Lock()

    def check_in_background(self) -> None:
        """Executa a consulta sem bloquear a tela inicial."""
        try:
            response = requests.get(
                LATEST_RELEASE_URL,
                headers={"Accept": "application/vnd.github+json"},
                timeout=6,
            )
            if response.status_code != 200:
                return

            release = response.json()
            remote_version = str(release.get("tag_name") or "")
            if not _is_newer(remote_version, __version__):
                return

            self._show_update_dialog(remote_version, GOOGLE_PLAY_URL)
        except (requests.RequestException, ValueError, TypeError):
            # A atualização é um recurso auxiliar: modo offline continua normal.
            return

    def _show_update_dialog(self, remote_version: str, release_url: str) -> None:
        with self._lock:
            if self._shown:
                return
            self._shown = True

        def close_dialog(_: ft.ControlEvent) -> None:
            dialog.open = False
            self.page.update()

        def open_release(_: ft.ControlEvent) -> None:
            self.page.launch_url(release_url)
            close_dialog(_)

        dialog = ft.AlertDialog(
            modal=False,
            title=ft.Text("Atualização disponível"),
            content=ft.Text(
                f"A versão {remote_version.lstrip('vV')} do Galvanos Calc está "
                f"disponível. Você está usando a versão {__version__}."
            ),
            actions=[
                ft.TextButton("Agora não", on_click=close_dialog),
                ft.ElevatedButton("Atualizar", on_click=open_release),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
