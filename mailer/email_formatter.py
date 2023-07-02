from jinja2 import Environment, FileSystemLoader

class EmailTemplateRenderer:
    def __init__(self, template_dir: str) -> None:
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def render_template(self, template_name: str, **kwargs: dict) -> str:
        template = self.env.get_template(template_name)
        rendered_content = template.render(**kwargs)
        return rendered_content
