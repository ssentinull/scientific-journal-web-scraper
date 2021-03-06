import re
from . import text_processing as tp
from langdetect import detect
from pprint import pprint


class Crawler:

    def __init__(self, start_page, end_page, page_limit, base_url, journal_url, separator, sort_by):
        self.start_page = start_page
        self.end_page = end_page
        self.page_limit = page_limit
        self.base_url = base_url
        self.journal_url = journal_url
        self.separator = separator
        self.sort_by = sort_by

    def crawl_specific_journal(self, article_list):
        is_journal_crawled = False
        current_page_num = 1
        sort_by = ''

        soup = tp.get_soup(self.journal_url)
        article_item = soup.find('div', {'class': 'article-item'})

        if article_item is None:
            return is_journal_crawled

        pagination_info_string = soup.find(
            'p', {'class': 'pagination-info'}).string.replace(" ", "")
        max_pages = int(
            re.search('of(.*)\\|', pagination_info_string).group(1))
        journal_title = soup.find(
            'div', {'class': 'j-meta-title'}).string.strip()

        while current_page_num <= max_pages:
            soup = tp.get_soup(self.journal_url)

            for div in soup.findAll('div', {'class': 'article-item'}):
                article_title_div = div.find('a', {'class': 'title-article'})
                article_title = article_title_div.find('xmp').string
                article_abstract = div.find(
                    'xmp', {'class': 'abstract-article'}).string

                if article_abstract is None or article_title is None:
                    continue

                article_abstract = article_abstract.replace("\n", " ")

                is_period_exist = "." in article_abstract

                if is_period_exist is False:
                    continue

                try:
                    article_abstract_sentences = article_abstract.split('.')
                    article_abstract_first_sentence = article_abstract_sentences[0]
                    article_abstract_second_sentence = article_abstract_sentences[1]

                    article_abstract_first_sentence_language = detect(
                        article_abstract_first_sentence)
                    article_abstract_second_sentence_language = detect(
                        article_abstract_second_sentence)
                except:
                    article_abstract_first_sentence_language = 'error'
                    article_abstract_second_sentence_language = 'error'

                if (article_abstract_first_sentence_language != 'id' and
                        article_abstract_second_sentence_language != 'id'):
                    continue

                article = [journal_title, article_title, article_abstract]

                is_article_duplicate = article in article_list

                if is_article_duplicate is True:
                    continue

                article_list.append(article)
                is_journal_crawled = True

            if self.page_limit != 0 and current_page_num >= self.page_limit:
                break

            current_page_num += 1

            self.journal_url = tp.set_new_url_endpoint(
                current_page_num, self.journal_url, self.separator, sort_by)

        if is_journal_crawled is True:
            print('| crawled journal ' + journal_title)
        else:
            print('| skipped journal ' + journal_title)

        return is_journal_crawled

    def crawl_main_page(self, article_list):

        main_page_url = self.base_url + '/journals'
        current_page_num = self.start_page

        while current_page_num <= self.end_page:
            is_main_page_crawled = False

            if self.start_page != 1:
                main_page_url = tp.set_new_url_endpoint(
                    current_page_num, main_page_url, self.separator, self.sort_by)

            soup = tp.get_soup(main_page_url)

            # \t\t
            print('+--------------------------------------------------------------+')
            print('| crawling page ' + main_page_url + '\t|')
            # \t\t
            print('+--------------------------------------------------------------+')

            url_list = list()

            for span in soup.findAll('span', {'class': 'index-val-small'}):
                is_journal_crawled = False
                a_tag = span.find('a', href=True)

                if a_tag is None:
                    continue

                journal_page_url = a_tag['href']
                url_list.append(journal_page_url)

            unique_url_list = list()

            for x in url_list:
                if x not in unique_url_list:
                    unique_url_list.append(x)

            for url in unique_url_list:
                self.journal_url = url
                is_journal_crawled = self.crawl_specific_journal(article_list)

                if is_journal_crawled is True:
                    is_main_page_crawled = True

            current_page_num += 1

            main_page_url = tp.set_new_url_endpoint(
                current_page_num, main_page_url, self.separator, self.sort_by)

        return is_main_page_crawled
