from jinja2 import Environment, FileSystemLoader

class EmailTemplateRenderer:
    def __init__(self, template_dir: str) -> None:
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def render_template(self, template_name: str, recipient_email: str, **kwargs: dict) -> str:
        template = self.env.get_template(template_name)
        rendered_content = template.render(recipient_email=recipient_email, **kwargs)
        return rendered_content


if __name__ == '__main__':

    # You can test template rendering by running this file directly,
    # opening the resulting ./rendered_email.html file in your browser
    # or open with VS Code Live Server extension.

    recipient = "markvanjislaaik@gmail.com"
    mail_context = {
        "sender_name": "Mark van Heeswijk",
        "file_basename": "SSBlitz_20230114_SAST.zip",
        "sender_address": 'mark@example.com',
        "download_link": "https://example.com/download/SSRugby_20230114_SAST.zip",
        "recipent_email": recipient
    }
    
    template_renderer = EmailTemplateRenderer(template_dir='mail_templates')
    rendered_email = template_renderer.render_template('mailer.html', recipient_email=recipient, **mail_context)

    with open('rendered_email.html', 'w') as f:
        f.write(rendered_email)