from telethon import Button

BUTTON_MANAGE_SUBSCRIPTIONS: str = "Подписки"
BUTTON_SEARCH: str = "Поиск"
BUTTON_REPORT: str = "Отчёты"
BUTTON_MANAGE_CHANNELS: str = "Каналы"
BUTTON_MANAGE_QUERIES: str = "Запросы"
BUTTON_USER_PROFILE: str = "Мой профиль"
BUTTON_ABOUT: str = "About"

MENU_BUTTONS_TEXTS = [
    BUTTON_MANAGE_SUBSCRIPTIONS,
    BUTTON_SEARCH,
    BUTTON_REPORT,
    BUTTON_MANAGE_QUERIES,
    BUTTON_MANAGE_CHANNELS,
    BUTTON_USER_PROFILE,
    BUTTON_ABOUT,
]

MENU_BUTTONS_REGEXP = "|".join(MENU_BUTTONS_TEXTS)

MAIN_MENU_BUTTONS = [
    [
        Button.text(BUTTON_MANAGE_SUBSCRIPTIONS, resize=True),
        Button.text(BUTTON_REPORT, resize=True),
        Button.text(BUTTON_SEARCH, resize=True),
        Button.text(BUTTON_MANAGE_QUERIES, resize=True),
    ],
    [
        Button.text(BUTTON_MANAGE_CHANNELS, resize=True),
        Button.text(BUTTON_USER_PROFILE, resize=True),
        Button.text(BUTTON_ABOUT, resize=True),
    ]
]


def get_main_menu_buttons():
    return MAIN_MENU_BUTTONS


def get_start_description() -> str:
    return "Меню активировано."
