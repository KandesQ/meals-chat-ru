from jinja2 import Environment, FileSystemLoader, select_autoescape

_env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(
        enabled_extensions=("html", "txt"),
    )
)

def render_template(name: str, **kwargs) -> str:
    rendered = _env.get_template(name).render(**kwargs)

    # Адекватный способ экранировать newline не встретил
    rendered = rendered.replace("\n", " ")
    # Тг не поддерживает тег <br>
    rendered = rendered.replace("<br>", "\n")
    rendered = "\n".join(line.strip() for line in rendered.split("\n"))

    return rendered
