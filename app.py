import json
import html
import re
from flask import Flask, render_template, request, flash

app = Flask(__name__)
app.secret_key = 'a_very_secret_key_for_pathfinder_v5'

VALID_IDENTIFIER_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def build_clean_html(data, path='$'):
    if isinstance(data, dict):
        html_output = f"<div class='node-wrapper'><span class='toggler'></span><ul class='json-dict'>"
        for key, value in data.items():
            if VALID_IDENTIFIER_RE.match(key):
                current_path = f"{path}.{key}"
            else:
                current_path = f"{path}['{key}']"

            key_html = f"<span class='json-key' data-path=\"{current_path}\">{html.escape(key)}</span>"
            value_html = build_clean_html(value, current_path)
            html_output += f'<li><div class="row-content">{key_html}: {value_html}</div></li>'
        html_output += "</ul></div>"
        return html_output

    elif isinstance(data, list):
        html_output = f"<div class='node-wrapper'><span class='toggler'></span><ol class='json-array'>"
        for i, item in enumerate(data):
            current_path = f"{path}[{i}]"
            index_html = f"<span class='array-index' data-path='{current_path}'>{i}</span>"
            value_html = build_clean_html(item, current_path)
            html_output += f'<li><div class="row-content">{index_html}: {value_html}</div></li>'
        html_output += "</ol></div>"
        return html_output

    else:
        if isinstance(data, str):
            value_str = html.escape(data)
        elif data is None:
            value_str = 'null'
        else:
            value_str = str(data)

        css_class = f'json-value json-{type(data).__name__.lower()}'
        return f'<span class="{css_class}" data-path="{path}">{value_str}</span>'


@app.route('/', methods=['GET', 'POST'])
def index():
    raw_json_text = ''
    interactive_html = ''
    json_data = None

    if request.method == 'POST':
        raw_json_text = request.form.get('json_text', '')
        if raw_json_text:
            try:
                json_data = json.loads(raw_json_text)
                interactive_html = build_clean_html(json_data)
            except json.JSONDecodeError:
                flash('Ошибка: Невалидный JSON. Пожалуйста, проверьте синтаксис.')
                interactive_html = ''
                json_data = None

    return render_template(
        'index.html',
        raw_json_text=raw_json_text,
        interactive_html=interactive_html,
        json_data=json_data
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0')
