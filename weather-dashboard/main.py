"""Weather Desk — my FNB App Academy capstone."""

import asyncio

import flet as ft
from weather import City, WeatherClient, WeatherError, condition

INK = "#152C46"
MUTED = "#476078"
BLUE = "#155E9B"
BACKGROUND = "#F3F6FA"


async def main(page: ft.Page):
    page.title = "Weather Desk"
    page.theme = ft.Theme(color_scheme_seed=BLUE)
    page.theme_mode = ft.ThemeMode.LIGHT

    client = WeatherClient()
    selected_city = City("Johannesburg", -26.20227, 28.04363, "South Africa", "Gauteng")
    weather = None
    busy = False
    error_message = ""
    matches = []
    search_message = ""

    city_input = ft.TextField(label="Find a city", hint_text="e.g. Cape Town")
    body = ft.Column(spacing=20, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

    def text(value, size=16, color=INK, bold=False):
        return ft.Text(
            value, size=size, color=color, weight=ft.FontWeight.BOLD if bold else None
        )

    def card(controls, col=12, color="#FFFFFF"):
        return ft.Container(
            content=ft.Column(
                controls, spacing=12, horizontal_alignment=ft.CrossAxisAlignment.STRETCH
            ),
            bgcolor=color,
            padding=24,
            border_radius=20,
            col=col,
        )

    def weather_icon(code):
        if code in (0, 1):
            return ft.Icons.WB_SUNNY_OUTLINED
        if code in (2, 3, 45, 48):
            return ft.Icons.CLOUD_OUTLINED
        return ft.Icons.WATER_DROP_OUTLINED

    async def navigate(e):
        await page.push_route("/forecast" if page.route == "/" else "/")

    async def load_weather(city):
        nonlocal weather, selected_city, busy, error_message, matches, search_message
        if busy:
            return
        busy = True
        error_message = ""
        matches = []
        search_message = ""
        render()
        try:
            result = await asyncio.to_thread(client.get_weather, city)
            weather = result
            selected_city = city
        except WeatherError as error:
            error_message = str(error)
        finally:
            busy = False
            render()

    async def refresh(e):
        await load_weather(selected_city)

    async def search(e):
        nonlocal matches, search_message, busy
        if busy:
            return
        query = (city_input.value or "").strip()
        if len(query) < 2:
            search_message = "Enter at least two letters to search."
            matches = []
            city_input.error_text = search_message
            render()
            return
        city_input.error_text = None
        matches = []
        search_message = ""
        busy = True
        render()
        try:
            matches = await asyncio.to_thread(client.search_cities, query)
            search_message = (
                "Choose your city below."
                if matches
                else "No cities found. Try another spelling."
            )
        except WeatherError as error:
            search_message = str(error)
        finally:
            busy = False
            render()

    def choose_city(city):
        async def choose(e):
            await load_weather(city)

        return choose

    city_input.on_submit = search

    def render():
        forecast_view = page.route == "/forecast"
        city_input.disabled = busy
        controls = [
            ft.Row(
                [
                    ft.Icon(ft.Icons.WB_SUNNY_OUTLINED, color=BLUE, size=30),
                    text("Weather Desk", 28, bold=True),
                ]
            ),
            text(
                "A quick look at the weather, wherever your day takes you.", color=MUTED
            ),
        ]
        if forecast_view:
            controls.append(
                ft.Button("Back to today", icon=ft.Icons.ARROW_BACK, on_click=navigate)
            )
        else:
            controls.append(
                card(
                    [
                        text("Where are you heading?", 20, bold=True),
                        city_input,
                        ft.Button(
                            "Search",
                            icon=ft.Icons.SEARCH,
                            on_click=search,
                            disabled=busy,
                        ),
                        *(
                            [text(search_message, color=MUTED)]
                            if search_message
                            else []
                        ),
                        *[
                            ft.OutlinedButton(
                                city.label,
                                icon=ft.Icons.LOCATION_ON_OUTLINED,
                                on_click=choose_city(city),
                                disabled=busy,
                            )
                            for city in matches
                        ],
                    ]
                )
            )
        controls.extend(
            [
                text(
                    "THREE-DAY FORECAST" if forecast_view else "CURRENT WEATHER",
                    13,
                    MUTED,
                    True,
                ),
                text(selected_city.label, 24, bold=True),
                ft.Row(
                    [
                        ft.Button(
                            "Refresh",
                            icon=ft.Icons.REFRESH,
                            on_click=refresh,
                            disabled=busy,
                        ),
                        *(
                            [
                                ft.ProgressRing(width=22, height=22),
                                text("Loading…", color=MUTED),
                            ]
                            if busy
                            else []
                        ),
                    ],
                    wrap=True,
                ),
            ]
        )
        if error_message:
            controls.append(
                card(
                    [
                        text(error_message, color="#842817", bold=True),
                        text(
                            (
                                "Showing the previous update below."
                                if weather
                                else "No weather loaded yet. Use Refresh to try again."
                            ),
                            color=INK,
                        ),
                    ],
                    color="#FFF0E8",
                )
            )
        if weather:
            controls.append(
                text(
                    f"Weather time: {weather.time:%d %b %Y, %H:%M} • {weather.timezone} (city local time)",
                    14,
                    MUTED,
                )
            )
            if forecast_view:
                controls.append(
                    ft.ResponsiveRow(
                        [
                            card(
                                [
                                    text(day.date.strftime("%A"), 22, bold=True),
                                    text(day.date.strftime("%d %b"), color=MUTED),
                                    ft.Icon(
                                        weather_icon(day.code), size=36, color=BLUE
                                    ),
                                    text(condition(day.code), 18, bold=True),
                                    text(
                                        f"{day.high:.0f}° / {day.low:.0f}°",
                                        30,
                                        bold=True,
                                    ),
                                    text("High / low • °C", 14, MUTED),
                                    text(
                                        f"Rain chance: {day.rain_chance:.0f}%",
                                        color=MUTED,
                                    ),
                                ],
                                col={"xs": 12, "md": 4},
                            )
                            for day in weather.forecast
                        ],
                        spacing=16,
                        run_spacing=16,
                    )
                )
            else:
                controls.extend(
                    [
                        card(
                            [
                                ft.Row(
                                    [
                                        ft.Column(
                                            [
                                                ft.Icon(
                                                    weather_icon(weather.code),
                                                    color=BLUE,
                                                    size=42,
                                                ),
                                                text(
                                                    f"{weather.temperature:.0f}°C",
                                                    68,
                                                    bold=True,
                                                ),
                                            ],
                                            spacing=4,
                                        ),
                                        ft.Column(
                                            [
                                                text(
                                                    condition(weather.code),
                                                    24,
                                                    bold=True,
                                                ),
                                                text(
                                                    f"Feels like {weather.feels_like:.0f}°C",
                                                    color=MUTED,
                                                ),
                                            ]
                                        ),
                                    ],
                                    spacing=32,
                                    wrap=True,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                            ],
                            color="#E4F0FC",
                        ),
                        ft.ResponsiveRow(
                            [
                                card(
                                    [
                                        ft.Icon(
                                            ft.Icons.WATER_DROP_OUTLINED, color=BLUE
                                        ),
                                        text("Humidity", color=MUTED),
                                        text(f"{weather.humidity:.0f}%", 26, bold=True),
                                    ],
                                    col={"xs": 12, "sm": 6},
                                ),
                                card(
                                    [
                                        ft.Icon(ft.Icons.AIR, color=BLUE),
                                        text("Wind", color=MUTED),
                                        text(f"{weather.wind:.0f} km/h", 26, bold=True),
                                    ],
                                    col={"xs": 12, "sm": 6},
                                ),
                            ],
                            spacing=16,
                            run_spacing=16,
                        ),
                        ft.Button(
                            "See three-day forecast",
                            icon=ft.Icons.CALENDAR_TODAY_OUTLINED,
                            on_click=navigate,
                        ),
                    ]
                )
        elif not busy and not error_message:
            controls.append(
                text("Choose a city or refresh to load its weather.", color=MUTED)
            )
        controls.extend(
            [
                ft.Divider(color="#D6E0E9"),
                text(
                    "Forecasts can change. Check again before heading out.", 14, MUTED
                ),
                ft.TextButton(
                    "Weather: Open-Meteo • City search: GeoNames",
                    url="https://open-meteo.com/",
                ),
            ]
        )
        body.controls = controls
        page.update()

    async def route_change():
        if page.route not in ("/", "/forecast"):
            await page.push_route("/")
            return
        page.views.clear()
        page.views.append(
            ft.View(
                route=page.route,
                bgcolor=BACKGROUND,
                padding=20,
                scroll=ft.ScrollMode.AUTO,
                controls=[ft.Container(body, width=940)],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        render()

    async def go_back(e):
        await page.push_route("/")

    page.on_route_change = route_change
    page.on_view_pop = go_back
    await route_change()
    await load_weather(selected_city)


if __name__ == "__main__":
    ft.run(main)
