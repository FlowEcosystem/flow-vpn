# ruff: noqa: RUF001


def build_admin_promo_create_code_text() -> str:
    return (
        "🏷 <b>Новый промокод — шаг 1/5</b>\n\n"
        "Введите код (латиница, цифры, дефис).\n"
        "Например: <code>FLOW30</code> или <code>PROMO-2026</code>\n\n"
        "Будет автоматически переведён в верхний регистр."
    )


def build_admin_promo_create_title_text(code: str) -> str:
    return (
        f"🏷 <b>Новый промокод — шаг 2/5</b>\n\n"
        f"Код: <code>{code}</code>\n\n"
        "Введите название промокода (отображается пользователям).\n"
        "Например: <i>Стартовый бонус</i>"
    )


def build_admin_promo_create_type_text(code: str, title: str) -> str:
    return (
        f"🏷 <b>Новый промокод — шаг 3/5</b>\n\n"
        f"Код: <code>{code}</code> · {title}\n\n"
        "Выберите тип бонуса:"
    )


def build_admin_promo_create_bonus_text(code: str, title: str) -> str:
    return (
        f"🏷 <b>Новый промокод — шаг 3/5 (бонусные дни)</b>\n\n"
        f"Код: <code>{code}</code> · {title}\n\n"
        "Введите количество бонусных дней (например, <b>30</b>)."
    )


def build_admin_promo_create_scope_text(code: str, title: str, bonus_label: str) -> str:
    return (
        f"🏷 <b>Новый промокод — шаг 4/5</b>\n\n"
        f"Код: <code>{code}</code> · {title} · {bonus_label}\n\n"
        "К каким подпискам применять промокод?"
    )


def build_admin_promo_create_limit_text(
    code: str,
    title: str,
    bonus_label: str,
    scope_label: str,
) -> str:
    return (
        f"🏷 <b>Новый промокод — шаг 5/5</b>\n\n"
        f"Код: <code>{code}</code> · {title}\n"
        f"Бонус: {bonus_label} · Область: {scope_label}\n\n"
        "Введите максимальное число активаций.\n"
        "• <b>0</b> — без лимита"
    )
