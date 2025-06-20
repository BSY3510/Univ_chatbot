import scrapy
from university_crawler.items import NoticeItem
from bs4 import BeautifulSoup

class NoticeCrawler(scrapy.Spider):
    name = 'notice_crawler'
    allowed_domains = ['example.com']  # 학교 도메인으로 변경
    start_urls = ['https://example.com/notice']  # 공지사항 페이지 URL

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        notices = soup.select('div.notice-item')  # 공지사항 리스트 셀렉터 (수정 필요)

        for notice in notices:
            item = NoticeItem()
            item['title'] = notice.select_one('.title').text.strip() if notice.select_one('.title') else ''
            item['url'] = response.urljoin(notice.select_one('a')['href']) if notice.select_one('a') else response.url
            yield scrapy.Request(item['url'], callback=self.parse_notice, meta={'item': item})

    def parse_notice(self, response):
        item = response.meta['item']
        soup = BeautifulSoup(response.text, 'html.parser')

        item['content'] = soup.select_one('.content').text.strip() if soup.select_one('.content') else ''
        item['date'] = soup.select_one('.date').text.strip() if soup.select_one('.date') else ''
        item['department'] = soup.select_one('.dept').text.strip() if soup.select_one('.dept') else ''
        item['files'] = []

        yield item