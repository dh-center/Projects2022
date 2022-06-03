import re
from typing import Union, Any, Dict, AnyStr
from xml.etree import ElementTree as ET

import feedparser
from bs4 import BeautifulSoup
from readability import Document
from newspaper import Article

from APPS.stat_monitoring import log_exception_without_stat, log_exception_web, EventName


def decode_bytes_to_html(response: bytes, decode_param: str):
    if decode_param == 'ignore':
        return response.decode('utf-8', errors='ignore')
    return response.decode(decode_param, errors='ignore')


def extract_update_start_link(xml: str, index: int) -> AnyStr:
    tree = ET.fromstring(xml)
    update_link = tree[index][0].text
    return update_link


def extract_links_from_xml(xml: str, all_crawl_links: dict, crawl_data: dict):
    tree = feedparser.parse(xml)
    for item in tree.entries[:100]:
        tags_data = {}
        link = item.get('link')
        tags_data['title'] = item.get('title')
        tags_data['pubDate'] = item.get('published', '')
        tags_data['author'] = item.get('author', '')
        if crawl_data.get('rss_tags'):
            if crawl_data['rss_tags']['content']:
                text = item.get('content')[0].value
                tags_data['content'] = extract_data_without_text_tags(Document(text).summary())
            if crawl_data['rss_tags']['content_tags']:
                tag = crawl_data['rss_tags']['content_tags']
                tags_data['content'] = extract_data_without_text_tags(Document(item.get(tag)).summary())
        all_crawl_links[link] = tags_data
    if not all_crawl_links:
        raise RuntimeError(f"Link data not retrieved!. Check start link!")


def extract_links_from_robots_txt(xml: str, index: list, all_crawl_links: dict):
    tree = ET.fromstring(xml)
    start, stop, step = index
    for item in tree[start: stop: step]:
        link = item[0].text
        all_crawl_links[link] = {}
    if not all_crawl_links:
        raise RuntimeError(f"Link data not retrieved!. Check start link!")


def extract_links_from_html(html: str, all_crawl_links: dict, crawl_data: dict):
    soup = BeautifulSoup(html, 'lxml')
    for tag in soup.select(", ".join(crawl_data['links_tags'])):
        link = tag.get('href')
        if link.startswith('/') or crawl_data.get('relative_links', None):
            link = crawl_data['main_link'] + link
        all_crawl_links[link] = {}
    if not all_crawl_links:
        raise RuntimeError(f"Link data not retrieved!. Check start link!")


def extract_crawl_links(type_page: str, extract_page: str, crawl_data: dict, index: list, all_crawl_links: dict):
    if type_page == 'rss':
        extract_links_from_xml(extract_page, all_crawl_links, crawl_data)
    if type_page == 'robots.txt':
        extract_links_from_robots_txt(extract_page, index, all_crawl_links)
    if type_page == 'start_page':
        extract_links_from_html(extract_page, all_crawl_links, crawl_data)


def extract_data_without_text_tags(body_tag) -> AnyStr:
    if isinstance(body_tag, str):
        body_tag = BeautifulSoup(body_tag, 'lxml')

    semantic_tags = [
        'a', 'em', 'strong', 'small', 's', 'cite', 'q', 'dfn', 'abbr', 'ruby', 'rb', 'rp', 'rt', 'rtc', 'data', 'time',
        'code', 'var', 'samp', 'kbd', 'sub', 'sup', 'i', 'b', 'u', 'mark', 'bdi', 'bdo', 'span', 'br', 'wbr'
    ]

    for match in body_tag.find_all(semantic_tags):
        match.string = match.text if match.string else ""
        try:
            if match.parent == body_tag:
                match.string = "\n~" + match.string + "~\n"
                body_tag.find(match.name).unwrap()
                continue
            if match.parent.string is None:
                match.parent.string = match.parent.text
                match.decompose()
                continue
            match.parent.string = match.parent.text
            match.decompose()
        except Exception:
            continue

    text = '\n'.join([text for text in body_tag.stripped_strings])
    text = re.sub("\n~", " ", text)
    text = re.sub("~\n", " ", text)
    return text


def automate_extract(page_data, crawl_data: dict):
    if crawl_data['autoparser'] == 'readability':
        doc = Document(page_data['html_page'])
        page_data['title'] = doc.title()
        page_data['content'] = extract_data_without_text_tags(BeautifulSoup(doc.summary(), 'lxml'))
    if crawl_data['autoparser'] == 'newspaper3k':
        article = Article(url='_')
        article.download(input_html=page_data['html_page'])
        article.parse()
        page_data['title'] = article.title
        page_data['content'] = article.text


def extract_news_text_from_html(body_tag, crawl_data: dict):
    if crawl_data['decompose_tags']:
        for tag in body_tag.select(', '.join(crawl_data['decompose_tags'])):
            tag.decompose()
    if crawl_data['text_tags']:
        text = '\n'.join([tag.text.strip() for tag in body_tag.select(crawl_data['text_tags'])]).strip()
        return text
    else:
        text = extract_data_without_text_tags(body_tag)
        return text


def extract_author_from_html(soup, crawl_data: dict):
    if crawl_data['author_tags']:
        author = '\n'.join([tag.text.strip() for tag in soup.select(crawl_data['author_tags'])]).strip()
        return author


def extract_title_from_html(soup, html_page: str, crawl_data: dict):
    title = soup.select_one(crawl_data['title_tag'])
    if title:
        return title.text.strip()
    else:
        title = Document(html_page).title()
        return title


def extract_meta_image_from_html(soup) -> Union[str, None]:
    img = soup.find("meta", property="og:image")
    if not img:
        return None
    image_url: str = img.get('content', '')
    if not image_url:
        return None
    if not image_url.startswith('http'):
        if image_url.startswith('//'):
            return f'https:{image_url}'
        else:
            return f'https://{image_url}'
    return image_url


def enrich_data(page_data: Dict[str, Any], crawl_data: Dict[str, Any], channel_name: str, link: str):
    if crawl_data.get('autoparser'):
        automate_extract(page_data, crawl_data)
        return
    soup = BeautifulSoup(page_data['html_page'], 'lxml')
    if crawl_data['title_tag']:
        page_data['title'] = extract_title_from_html(soup, page_data['html_page'], crawl_data)
    if crawl_data['author_tags']:
        page_data['author'] = extract_author_from_html(soup, crawl_data)
    if not page_data.get('content'):
        try:
            body_tag = ''
            for tag in crawl_data['body_tag']:
                body_tag = soup.select_one(tag)
                if body_tag:
                    page_data['content'] = extract_news_text_from_html(body_tag, crawl_data)
                    break
            if not body_tag:
                raise RuntimeError(f"Can not parse!: {link}")
        except Exception as exp:
            page_data['content'] = extract_data_without_text_tags(Document(page_data['html_page']).summary())
            log_exception_web(channel_name, EventName.PARSING_EXCEPTION,
                              msg=f'Unknown parsing result, check the link:{link}', exp=exp)
    try:
        page_data['meta_image'] = extract_meta_image_from_html(soup)
    except Exception as exp:
        log_exception_without_stat(f"enrich_meta() exception {exp} {page_data}")


def content_filter(content: str) -> str:
    # replace nbsp and \n\r+
    content = re.sub("\r", "", content)
    content = re.sub("\n+", "\n", content)
    content = content.replace(u'\xa0', ' ')
    return content


if __name__ == '__main__':
    with open('test_html_lenta_ru.html') as html_lenta_ru_file:
        html = html_lenta_ru_file.read()
        print(extract_meta_image_from_html(html))
