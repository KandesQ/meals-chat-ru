from jinja2 import Environment, FileSystemLoader, select_autoescape

_env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(
        enabled_extensions=("html", "txt"),
    )
)

def render_template(name: str) -> str:
    return _env.get_template(name).render().replace("\n", " ")
