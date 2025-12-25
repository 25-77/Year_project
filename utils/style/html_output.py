from IPython.display import HTML, display


def print_html(base_text, higlighted_text):
    """
    Выводит текст в одну строку, где higlighted_text оранжевый и жирный.
    Сохраняет все пробелы.
    """

    html_output = f"""
    <b style='white-space: pre;'>{base_text}</b>
    <b style='color:orange;'>{higlighted_text}</b>
    """

    display(HTML(html_output))

def print_multiple_html(*text_pairs, px_margin=1.4):
    html_pairs = []
    for base, highlighted in text_pairs:
        html_pairs.append(
            f"""<div style='margin-bottom: {px_margin}px;'>
                <b style='white-space: pre;'>{base}</b> 
                <b style='color:orange;'>{highlighted}</b>
            </div>""")

    display(HTML("".join(html_pairs)))