import os
import glob
import tempfile
import shutil
import imagehash
from PIL import Image
from playwright.sync_api import sync_playwright
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

def render_html_to_image(html_path, image_path, width=1024, height=768):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto('file://' + os.path.abspath(html_path))
        page.screenshot(path=image_path, full_page=True)
        browser.close()

def compute_simhash(tokens, f=64):
    return Simhash(tokens, f=f)

def compute_phash(image_path, hash_size=16):
    img = Image.open(image_path).convert('L').resize((256, 256))
    return imagehash.phash(img, hash_size=hash_size)

def build_similarity_graph(paths, simhashes, phashes, sim_k=3, phash_thresh=8):
    graph = {p: set() for p in paths}
    n = len(paths)
    for i in range(n):
        for j in range(i+1, n):
            p1, p2 = paths[i], paths[j]
            d_text = simhashes[p1].distance(simhashes[p2])
            d_vis = phashes[p1] - phashes[p2]
            if d_text <= sim_k or d_vis <= phash_thresh:
                graph[p1].add(p2)
                graph[p2].add(p1)
    return graph


def extract_clusters(graph):
    visited = set()
    clusters = []
    for node in graph:
        if node not in visited:
            stack = [node]
            visited.add(node)
            cluster = []
            while stack:
                u = stack.pop()
                cluster.append(os.path.basename(u))
                for v in graph[u]:
                    if v not in visited:
                        visited.add(v)
                        stack.append(v)
            clusters.append(sorted(cluster))
    clusters.sort(key=lambda c: c[0])
    return clusters

def cluster_html_directory(
    directory,
    sim_k=3,
    phash_thresh=8,
    fbits=64,
    tmpdir=None
):
    html_paths = glob.glob(os.path.join(directory, '*.html'))
    if tmpdir is None:
        tmpdir = tempfile.mkdtemp(prefix='screenshots_')

    simhashes = {}
    phashes = {}

    for html in html_paths:
        html_text = open(html, encoding='utf-8').read()
        tokens = preprocess_html(html_text)
        simhashes[html] = compute_simhash(tokens, f=fbits)

        img_path = os.path.join(tmpdir, os.path.basename(html) + '.png')
        render_html_to_image(html, img_path)
        phashes[html] = compute_phash(img_path)

    graph = build_similarity_graph(html_paths, simhashes, phashes, sim_k, phash_thresh)
    clusters = extract_clusters(graph)

    shutil.rmtree(tmpdir)
    return clusters

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Cluster similar HTML pages')
    parser.add_argument('directory', help='Path to HTML directory')
    parser.add_argument('--sim_k', type=int, default=3, help='Max SimHash distance')
    parser.add_argument('--phash_thresh', type=int, default=8, help='Max pHash distance')
    args = parser.parse_args()

    result = cluster_html_directory(
        args.directory,
        sim_k=args.sim_k,
        phash_thresh=args.phash_thresh
    )
    for grp in result:
        print(grp)
