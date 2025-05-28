from typing import LiteralString


def format_line_for_svg(
    label: str,
    value: str,
    colors: dict,
    total_width: int = 62,
) -> str:
    """
    Format a line of text for SVG rendering with styled segments.

    Parameters
    ----------
    label : str
        The label text to display on the left
    value : str
        The value text to display on the right
    colors : dict
        Dictionary containing color values for different elements
    total_width : int, optional
        The total width of the line in characters (controls the number of dots)

    Returns
    -------
    str
        An SVG <tspan> formatted string that includes the label, filler dots, 
        and value, each styled with specific colors.
    """
    dots = f"{'.' * (total_width - len(label) - len(value) - 2)} "
    return (
        f'<tspan fill="{colors["label"]}"> . </tspan>'
        f'<tspan fill="{colors["label"]}">{label}</tspan>'
        f'<tspan fill="{colors["ascii"]}"> {dots}</tspan>'
        f'<tspan fill="{colors["value"]}">{value}</tspan>'
    )


def render_combined_svg(
    ascii_lines: list[LiteralString],
    profile_lines: list[str | tuple[str, str]],
    colors: dict,
    line_height: int = 24,
) -> str:
    """
    Render a combined SVG image with ASCII art on the left and profile lines on 
    the right.

    Parameters
    ----------
    ascii_lines : list of str
        Lines of ASCII art to render on the left side.
    profile_lines : list of str or tuple[str, str]
        Lines of profile information
    colors : dict
        Dictionary containing color values for different elements
    line_height : int, optional
        Vertical spacing between lines in pixels

    Returns
    -------
    str
        A complete SVG string with both ASCII and profile data rendered in a 
        grid layout.
    """
    max_lines = max(len(ascii_lines), len(profile_lines))
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{max_lines * line_height + 40}" style="background-color:{colors["background"]}">',
        '<style> text { font-family: monospace; font-size: 16px; } </style>',
    ]
    char_width, padding = 9, 40
    profile_x_offset = len(ascii_lines[1]) * char_width + padding

    for i in range(max_lines):
        y = 20 + i * line_height

        # Left side ASCII art
        if i < len(ascii_lines):
            ascii = ascii_lines[i]
            svg.append(
                f'<text x="20" y="{y}" fill="{colors["ascii_image"]}" xml:space="preserve">{ascii}</text>'
            )

        # Right side profile
        if i < len(profile_lines):
            line = profile_lines[i]
            if isinstance(line, tuple):
                label, value = line
                styled = format_line_for_svg(label, value, colors)
            else:
                styled = f'<tspan fill="{colors["ascii"]}">{line}</tspan>'
            svg.append(f'<text x="{profile_x_offset}" y="{y}" xml:space="preserve">{styled}</text>')

    svg.append("</svg>")
    return "\n".join(svg)


def generate_profile_lines(
    profile_data: dict,
    total_width: int = 62,
) -> list[str | tuple[str, str]]:
    """
    Generate structured profile lines from nested profile data for SVG 
    rendering.

    Parameters
    ----------
    profile_data : dict
        A dictionary containing the profile structure. Supports nested and 
        flat dicts.
    total_width : int
        The target width of each line in characters for consistent dot padding.
    """
    lines: list[str | tuple[str, str]] = []
    for top_level, sections in profile_data.items():
        lines.append(f" - {top_level}{'-' * (total_width - len(top_level) - 1)} ")
        added_spacer = False  # Track if spacer was already added

        if isinstance(sections, dict):
            for second_level, items in sections.items():
                if isinstance(items, dict):
                    for label, value in items.items():
                        full_label = f"{second_level}.{label}:" if top_level == "alexei@quick" else f"{label}:"
                        lines.append((full_label, f"{value} "))
                    lines.append(" .")  # Spacer after nested group
                    added_spacer = True
                else:
                    full_label = f"{second_level}:"
                    lines.append((full_label, f"{items} "))

            if not added_spacer:
                lines.append(" .")  # Spacer for flat sections
        else:
            lines.append((top_level, f"{sections} "))
            lines.append(" .")  # Fallback in case it's not a dict

    return lines[:-1]
