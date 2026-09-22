"""Consulta opcional de novas versões no GitHub e na Google Play."""

from __future__ import annotations

import re
import threading

import flet as ft
import requests

from app_version import __build__, __version__


APP_PACKAGE_ID = "com.merotecdev.gcalc"
GOOGLE_PLAY_URL = f"https://play.google.com/store/apps/details?id={APP_PACKAGE_ID}"
GOOGLE_PLAY_DETAILS_URL = f"{GOOGLE_PLAY_URL}&hl=pt_BR&gl=BR"
GITHUB_REPOSITORY = "Romero-Softwares/GCalc-App"
GITHUB_RELEASES_URL = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/releases"
GITHUB_LATEST_RELEASE_URL = f"{GITHUB_RELEASES_URL}/latest"
REQUEST_HEADERS = {
    "Accept-Language": "pt-BR,pt;q=0.9",
    "User-Agent": "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/120 Mobile Safari/537.36",
}
GITHUB_HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "Galvanos-Calc-Updater",
    "X-GitHub-Api-Version": "2022-11-28",
}
_PLAY_VERSION_PATTERN = re.compile(r'"141":\[\[\["([^"\\]+)"\]\]')
_PLAY_BUILD_PATTERN = re.compile(
    rf'\[\["{re.escape(APP_PACKAGE_ID)}",(\d+)\]\]'
)


def _version_key(value: str) -> tuple[int, ...] | None:
    """Converte versões como ``v0.1.7`` em uma chave comparável."""
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


def _build_number(value: object) -> int | None:
    try:
        number = int(str(value))
    except (TypeError, ValueError):
        return None
    return number if number >= 0 else None


def _is_update_available(
    remote_version: str,
    remote_build: object,
    local_version: str,
    local_build: object,
) -> bool:
    """Compara versão e, em caso de empate, o código de build Android."""
    remote_key = _version_key(remote_version)
    local_key = _version_key(local_version)
    if remote_key is None or local_key is None:
        return False

    length = max(len(remote_key), len(local_key))
    remote_key += (0,) * (length - len(remote_key))
    local_key += (0,) * (length - len(local_key))
    if remote_key != local_key:
        return remote_key > local_key

    parsed_remote_build = _build_number(remote_build)
    parsed_local_build = _build_number(local_build)
    return (
        parsed_remote_build is not None
        and parsed_local_build is not None
        and parsed_remote_build > parsed_local_build
    )


def _read_google_play_release(page_html: str) -> tuple[str, int | None] | None:
    """Extrai versão e versionCode da página pública da Google Play."""
    version_match = _PLAY_VERSION_PATTERN.search(page_html)
    if version_match is None:
        return None

    build_match = _PLAY_BUILD_PATTERN.search(page_html)
    build = int(build_match.group(1)) if build_match is not None else None
    return version_match.group(1), build


def _read_github_release(release: object) -> tuple[str, int | None, str] | None:
    """Extrai a versão publicada em uma GitHub Release pública."""
    if not isinstance(release, dict) or release.get("draft"):
        return None

    version = str(release.get("tag_name") or "").strip()
    if _version_key(version) is None:
        return None

    release_text = " ".join(
        str(release.get(field) or "") for field in ("name", "body", "tag_name")
    )
    build_match = re.search(
        r"(?:build|version\s*code|c[oó]digo)\s*[:#-]?\s*(\d+)",
        release_text,
        re.IGNORECASE,
    )
    build = int(build_match.group(1)) if build_match is not None else None
    release_url = str(release.get("html_url") or "").strip()
    if not release_url.startswith("https://github.com/"):
        release_url = f"https://github.com/{GITHUB_REPOSITORY}/releases/latest"
    return version, build, release_url


def _github_release_key(release: tuple[str, int | None, str]) -> tuple[int, ...]:
    """Ordena releases pela versão e, quando disponível, pelo build."""
    version_key = _version_key(release[0])
    assert version_key is not None
    build = _build_number(release[1])
    return (*version_key, build if build is not None else -1)


class UpdateChecker:
    """Exibe um aviso quando existir uma versão nova no GitHub ou na Play."""

    def __init__(self, page: ft.Page):
        self.page = page
        self._shown = False
        self._lock = threading.Lock()

    def check_in_background(self) -> None:
        """Executa a consulta sem bloquear a tela inicial."""
        try:
            release = self._get_github_release()
            if release is None or not _is_update_available(
                release[0], release[1], __version__, __build__
            ):
                release = self._get_google_play_release()
            if release is None:
                return

            remote_version, remote_build, _release_url = release
            if not _is_update_available(
                remote_version, remote_build, __version__, __build__
            ):
                self.page.client_storage.remove("available_update")
                self._refresh_notification_badge()
                return

            # A persistência alimenta a Central de notificações, mas não pode
            # impedir o aviso principal caso o armazenamento local falhe.
            self.page.client_storage.set(
                "available_update",
                {
                    "version": remote_version,
                    "build": remote_build,
                    "url": GOOGLE_PLAY_URL,
                },
            )
            self._refresh_notification_badge()
            self._show_update_dialog(remote_version, remote_build, GOOGLE_PLAY_URL)
        except (requests.RequestException, TypeError, ValueError):
            # A atualização é um recurso auxiliar: modo offline continua normal.
            return

    def _refresh_notification_badge(self) -> None:
        """Atualiza o indicador da tela principal quando ela estiver aberta."""
        refresh_badge = getattr(self.page, "_refresh_notification_badge", None)
        if callable(refresh_badge):
            refresh_badge()

    def _get_github_release(self) -> tuple[str, int | None, str] | None:
        """Inclui pre-releases do GitHub para testar o APK antes da Play."""
        response = requests.get(
            GITHUB_RELEASES_URL,
            headers=GITHUB_HEADERS,
            timeout=10,
        )
        if response.status_code == 200:
            releases = response.json()
            if isinstance(releases, list):
                candidates = [
                    parsed
                    for item in releases
                    if (parsed := _read_github_release(item)) is not None
                ]
                if candidates:
                    return max(candidates, key=_github_release_key)

        # Mantém compatibilidade com repositórios que só expõem a release latest.
        response = requests.get(
            GITHUB_LATEST_RELEASE_URL,
            headers=GITHUB_HEADERS,
            timeout=10,
        )
        if response.status_code == 200:
            return _read_github_release(response.json())
        return None

    def _get_google_play_release(self) -> tuple[str, int | None, str] | None:
        """Usa a Play Store quando ainda não houver release acessível no GitHub."""
        response = requests.get(
            GOOGLE_PLAY_DETAILS_URL,
            headers=REQUEST_HEADERS,
            timeout=10,
        )
        if response.status_code != 200:
            return None

        release = _read_google_play_release(response.text)
        if release is None:
            return None
        version, build = release
        return version, build, GOOGLE_PLAY_URL

    def _show_update_dialog(
        self,
        remote_version: str,
        remote_build: int | None,
        release_url: str,
    ) -> None:
        with self._lock:
            if self._shown:
                return
            self._shown = True

        def close_dialog(_: ft.ControlEvent) -> None:
            self.page.close(dialog)

        def open_release(_: ft.ControlEvent) -> None:
            self.page.launch_url(release_url)
            close_dialog(_)

        remote_label = (
            f"{remote_version} (build {remote_build})"
            if remote_build is not None
            else remote_version
        )
        local_label = f"{__version__} (build {__build__})"
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Atualização disponível"),
            content=ft.Text(
                f"Nova versão: {remote_label}\n"
                f"Versão instalada: {local_label}\n\n"
                "Toque em Atualizar para abrir a Google Play."
            ),
            actions=[
                ft.TextButton("Agora não", on_click=close_dialog),
                ft.ElevatedButton("Atualizar", on_click=open_release),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.open(dialog)
