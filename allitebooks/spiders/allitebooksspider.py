# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
from allitebooks.items import AllitebooksItem
import os, html, re
from os import path


base_url = 'http://www.allitebooks.org'


def get_book_links(soup):
    book_links = []
    title_tags = soup.select("h2.entry-title > a")
    for title_tag in title_tags:
        book_links.append(title_tag['href'])

    return book_links


def get_item_entry(key, value):
    if key == 'Author:':
        return {"key": "author", "value": value}
    if key == 'ISBN-10:':
        return {"key": "isbn10", "value": value}
    if key == 'Year:':
        return {"key": "year", "value": value}
    if key == 'Pages:':
        return {"key": "pages", "value": value}
    if key == 'Language:':
        return {"key": "language", "value": value}
    if key == 'File size:':
        return {"key": "filesize", "value": value}
    if key == 'File format:':
        return {"key": "fileformat", "value": value}
    if key == 'Category:':
        return {"key": "category", "value": value}


class AllitebooksspiderSpider(scrapy.Spider):
    name = 'allitebooksspider'
    # allowed_domains = ['allitebooks.com']
    start_urls = [base_url]

    def parse(self, response):
        soup = BeautifulSoup(response.text, "lxml")

        # page count
        pages = 841
        pages_item = soup.find("a", {"title": "Last Page →"})
        if pages_item:
            pages = pages_item.text.strip()
            pages = int(pages)

        book_links = get_book_links(soup)
        for book_link in book_links:
            yield scrapy.Request(book_link, callback=self.parse_book_page)

        for page in range(pages, 1, -1):
            page_link = "{}/page/{}".format(base_url, page+1)
            yield scrapy.Request(page_link, callback=self.parse_page)


    def parse_page(self, response):
        soup = BeautifulSoup(response.text, "lxml")
        book_links = get_book_links(soup)
        for book_link in book_links:
            yield scrapy.Request(book_link, callback=self.parse_book_page)

        
    def parse_book_page(self, response):
        item = AllitebooksItem()
        soup = BeautifulSoup(response.text, "lxml")

        # title
        title_tag = soup.find("h1", {"class": "single-title"})
        if title_tag == None:
            print ("Error! There isn't title tag")
            return
        item['title'] = title_tag.text.strip()

        # make book directory
        title = re.sub(r"[(\\|\/|\:|\*|\?|\"|\<|\>|\|)+]", '', item['title'])
        book_dir = os.path.join("books", title)
        if not os.path.exists(book_dir):
            os.makedirs(book_dir)

        # book detail
        book_detail_tag = soup.find("div", {"class": "book-detail"})
        if book_detail_tag == None:
            print ("Error! Cannot find book detail")
            return
        
        dt_tags = book_detail_tag.select("dt")
        dd_tags = book_detail_tag.select("dd")
        for dt_tag, dd_tag in zip(dt_tags, dd_tags):
            key = dt_tag.text.strip()
            value = dd_tag.text.strip()
            entry = get_item_entry(key, value)
            if entry:
                item[entry['key']] = entry['value']

        # description
        descriptions = []
        description_tags = soup.select("div.entry-content > p")
        for description_tag in description_tags:
            descriptions.append(description_tag.text.strip())
        item['description'] = '\n'.join(descriptions)

        # image
        image_tag = soup.select_one("div.entry-body-thumbnail > a > img")
        if image_tag:
            image_link = image_tag['src']
            item['image_url'] = image_link
            request = scrapy.Request(image_link, callback=self.download_book_image)
            request.meta['dir'] = book_dir
            yield request

        # download links
        download_links = []
        download_tags = soup.select("span.download-links > a")
        for tag in download_tags:
            download_link = tag['href']
            download_links.append(download_link)
            request = scrapy.Request(download_link, callback=self.download_book)
            request.meta['dir'] = book_dir
            yield request

        item['download_links'] = ','.join(download_links)
        item['url'] = response.url

        yield item

    
    def download_book_image(self, response):
        directory = response.meta['dir']

        path = response.url.split('/')[-1]
        image_path = os.path.join(directory, path)
        with open(image_path, 'wb') as f:
            f.write(response.body)


    def download_book(self, response):
        directory = response.meta['dir']

        path = response.url.split('/')[-1]
        path = html.unescape(path)
        path = path.replace("%20", " ")
        book_path = os.path.join(directory, path)
        with open(book_path, 'wb') as f:
            f.write(response.body)