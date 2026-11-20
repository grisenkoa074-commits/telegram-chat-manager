
from io import BytesIO
from datetime import date, timedelta

from aiogram.types import BufferedInputFile


def create_activity_chart(daily_activity: dict[int, int]):
    """
    daily_activity: словарь, где ключ — день назад (0–6),
    значение — количество сообщений.
    """

    width = 700
    height = 360
    left = 65
    bottom = 55
    top = 35
    chart_height = height - top - bottom
    chart_width = width - left - 25

    max_value = max(daily_activity.values(), default=0)
    max_value = max(max_value, 1)

    bar_width = 48
    gap = (chart_width - 7 * bar_width) / 6

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#17212b"/>',
        '<text x="30" y="25" fill="white" font-size="18">'
        'Активность за 7 дней</text>',
    ]

    for i in range(5):
        y = top + i * chart_height / 4
        value = round(max_value * (4 - i) / 4)

        svg.append(
            f'<line x1="{left}" y1="{y:.1f}" '
            f'x2="{width - 20}" y2="{y:.1f}" '
            f'stroke="#40505f" stroke-width="1"/>'
        )
        svg.append(
            f'<text x="{left - 12}" y="{y + 5:.1f}" '
            f'fill="#b8c7d3" font-size="13" text-anchor="end">'
            f'{value}</text>'
        )

    for i in range(7):
        value = daily_activity.get(i, 0)
        bar_height = value / max_value * chart_height
        x = left + i * (bar_width + gap)
        y = top + chart_height - bar_height

        svg.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" '
            f'width="{bar_width}" height="{bar_height:.1f}" '
            f'rx="7" fill="#4da6ff"/>'
        )

        day = (date.today() - timedelta(days=6 - i)).strftime("%d.%m")
        svg.append(
            f'<text x="{x + bar_width / 2:.1f}" '
            f'y="{height - 20}" fill="#b8c7d3" '
            f'font-size="13" text-anchor="middle">{day}</text>'
        )

    svg.append('</svg>')

    image_data = BytesIO()
    image_data.write("".join(svg).encode("utf-8"))

    return BufferedInputFile(
        image_data.getvalue(),
        filename="activity.svg"
    )
