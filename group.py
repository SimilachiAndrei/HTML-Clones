from readability import Document
from lxml.html import fromstring


def preprocess_html(html):
    try:
        doc = Document(html)
        content = doc.summary()
        tree = fromstring(content)
    except Exception:
        tree = fromstring(html)

    text = ' '.join(tree.text_content().split()).lower()
    tokens = text.split()


    return tokens
