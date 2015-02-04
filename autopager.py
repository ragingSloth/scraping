from functools import partial

import requests
from lxml import etree, html
from lxml.cssselect import CSSSelector

INTEGERS = [str(x) for x in range(10)]


def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def get_links(url):
    raw = requests.get(url).text
    sel = CSSSelector('a')
    return sel(html.fromstring(raw).getroottree()), url


def find_candidates(links, url):
    rs = lambda x: repr(x).strip('\'').lower()
    links = [(rs(link.text_content()), link.text, link.attrib['href'], link) for link in links]
    fltr = partial(heuristics, url)
    links = [l for l in links if fltr(*l)]
    weight = partial(heuristics_weight, url)
    links = [weight(*l) for l in links]
    links = [l for l in links if l]
    return min(links, key=lambda x: x[1])


def heuristics(url, content, text, target, _):
    candidate = False
    lev = levenshtein(url, url + target)
    try:
        text = str(text).lower()
        content = content.lower()
    except:
        pass
    try:
        if all([x in INTEGERS for x in text]):
            candidate = True
    except:
        pass
    try:
        if content in INTEGERS or text in integers:
            candidate = True
    except:
        pass
    try:
        if 'next' in content or 'next' in text:
            candidate = True
    except:
        pass
    try:
        if 'page' in content or 'page' in text or 'page' in target or '?p=' in target:
            #if not ('pages' in content or 'pages' in text or 'pages' in target):
            candidate = True
    except:
        pass
    try:
        if 'prev' in content or 'prev' in text:
            candidate = True
    except:
        pass
    try:
        if 'last' in content or 'last' in text:
            candidate = True
    except:
        pass
    return candidate


def heuristics_weight(url, content, text, target, link):
    bias = .1*(len(text) + len(target))
    weight = 10000
    try:
        text = str(text).lower()
        content = content.lower()
    except:
        pass
    try:
        if all([x in INTEGERS for x in text.strip('\n ')]):
            if not weight<2:
                weight = 2
    except:
        pass
    try:
        if content in INTEGERS or text in integers:
            if not weight<2:
                weight = 1
    except:
        pass
    try:
        if 'next' in content or 'next' in text:
            if 'next' == text.strip(' \n') or 'next' == content.strip('\n '):
                bias = 0
            weight = 0
    except:
        pass
    try:
        if 'page' in content or 'page' in text or 'page' in target or '?p=' in target:
            if not weight<2:
                weight = 3
    except:
        pass
    try:
        if 'prev' in content or 'prev' in text:
            if not weight<2:
                weight = 4
    except:
        pass
    try:
        if 'last' in content or 'last' in text:
            if not weight<2:
                weight = 5
    except:
        pass
    weight += bias
    return (link, weight)

data = get_links('https://cooking.stackexchange.com/questions')
data = [x for x in data[0] if 'href' in x.keys()], data[1]
print find_candidates(*data)[0].attrib['href']
