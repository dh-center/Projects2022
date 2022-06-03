#Web Crawler

Web Crawler состоит из:

* Конфигурационных файлов:

  [Пример:](APPS/web_crawler/data_for_crawling/www.foxnews.com/www.foxnews.com.json)
````json
{
  "name": "www.foxnews.com",
  "link": "https://www.foxnews.com",
  "source_meta": {
    "type": null,
    "license": null,
    "founders": null,
    "address": null,
    "language": null
  },
  "crawl_data": {
    "update_period": 300,
    "is_debug": false,
    "connector": {
      "connector_type": "SOCKS5",
      "connector_params": {
        "limit": 1000,
        "limit_per_host": 0,
        "force_close": false,
        "enable_cleanup_closed": false,
        "loop": null,
        "verify_ssl": true,
        "fingerprint": null,
        "use_dns_cache": true,
        "ttl_dns_cache": 10,
        "ssl_context": null,
        "local_addr": null
      }
    },
    "requests_data": {
      "headers": {},
      "start_link": "https://feeds.feedburner.com/foxnews/latest",
      "type": "rss",
      "allow_redirects": true,
      "update_start": false,
      "index": []
    },
    "main_link": "https://www.foxnews.com",
    "autoparser": "readability",
    "links_tags": [],
    "title_tag": "",
    "author_tags": "",
    "body_tag": [],
    "decompose_tags": [],
    "text_tags": ""
  }
}
````
* [Асинхронный веб-краулер](crawlers/start_crawler.py)
  
* Вспомогательный [программы для извлечения](utils/html_xml_utils.py) и [взаимодействия с хранилищем](utils/db_utils.py)