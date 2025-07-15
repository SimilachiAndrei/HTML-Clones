import os
import glob
import tempfile
import shutil
from readability import Document
from simhash import Simhash, SimhashIndex
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

def compute_simhash(tokens, f=64):
    return Simhash(tokens, f=f)


def build_similarity_graph(paths, simhashes, sim_k=3):
    graph = {p: set() for p in paths}
    n = len(paths)
    for i in range(n):
        for j in range(i+1, n):
            p1, p2 = paths[i], paths[j]
            d_text = simhashes[p1].distance(simhashes[p2])
            if d_text <= sim_k:
                graph[p1].add(p2)
                graph[p2].add(p1)
    return graph
