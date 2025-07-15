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

    tag_counts = {}
    for el in tree.iter():
        tag = el.tag
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    tokens += [f"tag_{t}:{c}" for t, c in tag_counts.items()]

    class_set = set()
    for el in tree.iter():
        cls = el.get('class')
        if cls:
            for c in cls.split():
                class_set.add(c)
    tokens += [f"cls_{c}" for c in class_set]

    return tokens



    return tokens

