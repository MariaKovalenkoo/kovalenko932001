import bs4
import requests
import time
import sys
import queue
import threading


class News:
    def __init__(self, title="", date="", annotation="", author="", resource=""):
        self.title = title
        self.date = date
        self.annotation = annotation
        self.author = author
        self.resource = resource

    def __str__(self):
        return ' '.join([self.resource, self.date, self.author]) + '\n' + self.title + '\n' + self.annotation


def get_kpru_news():
    url = 'https://www.kp.ru/sports/tennis/'
    html = requests.get(url).text
    soup = bs4.BeautifulSoup(html, features='html.parser')
    news_section = soup.find('div', id='show-more-from-981-container')
    news_divs = news_section.find_all('div', class_='small-12')
    news_list = []
    for div in news_divs:
        tag = div.find('div', class_='block-large')
        if tag is not None:
            container = tag.find('div', class_='block-large__left')
            title = container.find('h3').text.strip()
            annotation = container.find('a', class_='block-large__excerpt').text.strip()
            date = container.find('a', class_='block-large__date').text.strip()
            news_list.append(
                News(title=title, annotation=annotation, date=date, resource='kp.ru')
            )
        else:
            tag = div.find('div', class_='block-vertical')
            container = tag.find('div', class_='block-vertical__bottom')
            title = container.find('h3').text.strip()
            annotation = container.find('a', class_='block-vertical__excerpt').text.strip()
            date = container.find('a', class_='block-vertical__date').text.strip()
            news_list.append(
                News(
                    title=title,
                    annotation=annotation,
                    date=date,
                    resource='kp.ru')
            )
    return news_list


def get_riatomsk_news():
    url = 'https://www.riatomsk.ru/novosti'
    html = requests.get(url).text
    soup = bs4.BeautifulSoup(html, features='html.parser')
    news_divs = soup.find_all('div', class_='rubNewAbout')
    news_list = []
    for div in news_divs:
        inner = div.find_all('div', recursive=False)
        title = inner[0].text.strip().replace('\n', ' ')
        date = inner[1].find('span').text.strip() + ' ' + inner[1].find('div').text.strip()
        annotation = inner[2].text.strip().replace('\n', ' ')
        news_list.append(
            News(
                title,
                date,
                annotation,
                resource='riatomsk.ru'
            )
        )
    return news_list


def get_plainnews_news():
    url = 'https://plainnews.ru/parizh'
    html = requests.get(url).text
    soup = bs4.BeautifulSoup(html, features='html.parser')
    news_divs = soup.find_all('div', class_='feed__item')
    news_list = []

    for div in news_divs:
        title = div.find('h2').text.strip()
        annotation = ""
        try:
            annotation = div.find('div', class_='feed__text').text.strip()
        except:
            pass
        source = div.find('div', class_='feed__source')
        date = source.find('span')['title'].strip()
        resource = source.find('a').text.strip() + "@plainnews.ru"
        news_list.append(
            News(
                title, date, annotation, "", resource
            )
        )

    return news_list


def get_all_news():
    return [*get_kpru_news(), *get_riatomsk_news(), *get_plainnews_news()]


def background_task(q):
    timeout = 60 * 5
    while True:
        news = get_all_news()
        for i in news:
            q.put(i)
        time.sleep(timeout)


if __name__ == '__main__':
    q = queue.Queue()
    background_thread = threading.Thread(target=background_task, args=[q], daemon=True)
    shown_news = set()
    try:
        background_thread.start()
        while True:
            if not q.empty():
                a = q.get()
                if a.title not in shown_news:
                    shown_news.add(a.title)
                    print(a)
                    print(flush=True)
            else:
                time.sleep(0.5)
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
