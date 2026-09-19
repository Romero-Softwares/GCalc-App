import flet as f


def card_shadow():
    """Relevo discreto e consistente para os cartões claros do aplicativo."""
    return [
        f.BoxShadow(
            blur_radius=2,
            spread_radius=0.5,
            color=f.Colors.with_opacity(0.75, "#ffffff"),
            offset=f.Offset(0, -1),
        ),
        f.BoxShadow(
            blur_radius=12,
            spread_radius=0.5,
            color=f.Colors.with_opacity(0.22, "#334155"),
            offset=f.Offset(0, 5),
        ),
    ]


def card_border(color="#dbe4ee"):
    return f.border.all(1, color)


def dark_card_shadow():
    return [
        f.BoxShadow(
            blur_radius=2,
            color=f.Colors.with_opacity(0.25, "#ffffff"),
            offset=f.Offset(0, -1),
        ),
        f.BoxShadow(
            blur_radius=14,
            spread_radius=1,
            color=f.Colors.with_opacity(0.55, "#020617"),
            offset=f.Offset(0, 6),
        ),
    ]


def dark_card_border():
    return f.border.all(1, f.Colors.with_opacity(0.22, "#ffffff"))
