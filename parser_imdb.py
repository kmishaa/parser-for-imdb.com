import requests
from bs4 import BeautifulSoup
import re
import csv
import os
import subprocess

URL = 'https://www.imdb.com/chart/top'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 YaBrowser/21.11.1.932 Yowser/2.5 Safari/537.36',
               'accept': '*/*'}
FILE = 'results_imdb1.csv'
HOST = 'https://www.imdb.com'

def get_html(url):
    r = requests.get(url, headers=HEADERS)
    return r

def get_countries(soup):
    country = ''
    countries = soup.find_all('a', class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link')
    for c in countries:
        country += c.get_text() + ', '
    return country[:len(country)-2]

def get_genres(soup):
    genre = ''
    genres = soup.find_all('li', class_='ipc-inline-list__item')
    for g in genres:
        genre += g.find('a', class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link').get_text()
        genre += ', '
    return genre[:len(genre)-2]

def make_reviews(review):
    cifre = 0
    zeroes = 0
    parts = review.split('.', 2)
    if (len(parts) > 1):
        for char in parts[1]:
            if (char.isdigit()):
                cifre += 1
    if 'K' in review:
        for i in range(1, 4 - cifre):
            zeroes += 1
    zeroes_str = ''
    for i in range (0, zeroes):
        zeroes_str += '0'
    review = review.replace('.', '')
    review = review.replace('K', f'{zeroes_str}')
    return review
    
def get_directors(soup):
    director = ''
    directors = soup.find_all('a', class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link')
    for direct in directors:
        director += direct.get_text() + ', '
    return director[:len(director) - 2]

def check_director(string):
    string = string.replace('É', 'E')
    string = string.replace('é', 'e')
    string = string.replace('á', 'a')
    string = string.replace('í', 'i')
    string = string.replace('ó', 'o')
    string = string.replace('ô', 'o')
    string = string.replace('ö', 'o')
    string = string.replace('ç', 'c')
    string = string.replace('ñ', 'n')
    return string
    
def get_movie_content(html):
    soup_movie = BeautifulSoup(html, 'html.parser')

    title = soup_movie.find('h1', class_='TitleHeader__TitleText-sc-1wu6n3d-0 dxSWFG')
    if title:
        title = title.get_text()
    else:
        title = soup_movie.find('h1', class_='TitleHeader__TitleText-sc-1wu6n3d-0 gxLYZW')
        if title:
            title = title.get_text()
        else:
            title = soup_movie.find('h1', class_='TitleHeader__TitleText-sc-1wu6n3d-0 cLNRlG')
            if title:
                title = title.get_text()

    director = ''
    country = ''
    countries = False
    genre = ''
    genres = False
    metadatas = soup_movie.find_all('li', class_='ipc-metadata-list__item')
    country_number = 0
    genre_number = 0
    for meta in range (0, len(metadatas)):
        directic = metadatas[meta].find('span', class_='ipc-metadata-list-item__label')
        if directic:
            directic = directic.get_text()
        else:
            directic = ''            
        if (directic == 'Director'):
            director = metadatas[meta].find('a', class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link').get_text()
        elif (directic == 'Directors'):
            director = get_directors(metadatas[meta])
        
        if (not((metadatas[meta].get_text().find('Country of origin')) == -1)):
            country_number = meta
        elif (not((metadatas[meta].get_text().find('Countries of origin')) == -1)):
            countries = True
            country_number = meta
        elif (not((metadatas[meta].get_text().find('Genres')) == -1)):
            genres = True
            genre_number = meta
        elif (not((metadatas[meta].get_text().find('Genre')) == -1)):
            genre_number = meta    
        
    if (not(countries)):
        country = metadatas[country_number].find('a', class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link').get_text()
    else:
        country = get_countries(metadatas[country_number])
    
    if (not(genres)):
        genre = metadatas[genre_number].find('a', class_='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link').get_text()
    else:
        genre = get_genres(metadatas[genre_number])

    year = soup_movie.find('span', class_='TitleBlockMetaData__ListItemText-sc-12ein40-2 jedhex')
    if year:
        year = year.get_text()
    else:
        year = '0'

    rating = soup_movie.find('a', class_='ipc-link ipc-link--base ipc-link--inherit-color top-rated-link')

    if rating:
        rating = rating.get_text()
    else:
        rating = '0'

    mark = soup_movie.find('span', class_='AggregateRatingButton__RatingScore-sc-1ll29m0-1 iTLWoV')

    if mark:
        mark = mark.get_text()
    else:
        mark = '0'

    reviews = soup_movie.find('div', class_='UserReviewsHeader__Header-k61aee-0 egCnbs')

    if reviews:
        reviews = reviews.find('span', class_='ipc-title__subtext')
        if reviews:
            reviews = reviews.get_text()
        else:
            reviews = '0'
    else:
        reviews = '0'
    title = check_director(title)
    director = check_director(director)
    movie = [{
        'title': title,
        'director': director,
        'country': country,
        'genre': genre,
        'year': int(year),
        'rating': int((re.findall("\d+", rating))[0]),
        'mark': float(mark),
        'reviews': make_reviews(reviews),
    }]

    return movie

def get_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    all_movies = soup.find_all('td', class_='titleColumn')
    movies = []
    counter = 1
    while (counter <= 5):
        movie = all_movies[counter]
    #for movie in all_movies:
        if (counter % 1 == 0):
            print (f'Обработано {counter} фильмов из {len(all_movies)}')
        counter += 1
        link = HOST + movie.find('a').get('href')
        html_movie = get_html(link)
        movies.extend(get_movie_content(html_movie.text))
    return movies

def save_file(items, path):
    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Название', 'Режиссёр', 'Страна производства', 'Жанр', 'Год выхода', 'Место в рейтинге', 'Средняя оценка пользователей сайта', 'Количество отзывов'])
        for item in items:
            print('rating:', item['mark'])
            writer.writerow([item['title'], item['director'], item['country'], item['genre'], item['year'], item['rating'], item['mark'], item['reviews']])


def parse():
    print ('Установка соединения...')
    html = get_html(URL)
    if (html.status_code == 200):
        print ('Парсинг страницы 1 из 1...')
        movies = get_content(html.text)
        save_file(movies, FILE)
        print (f'Всего обработано {len(movies)} фильмов')

        os.startfile(FILE) #запуск созданного excel-файла для Windows

        #subprocess.call(['open', FILE]) #запуск созданного excel-файла для Mac os
    else:
        print ('Ошибка соединения(')

parse()
