#! /usr/bin/env python
import bs4
import json
import urlparse
import os
import requests
import codecs
import logging
import re

logging.basicConfig(level=logging.INFO)

class Person(object):
  """
  Class to define aperson in a movie
  """
  logger = logging.getLogger("Person")

  HTML_DIR = os.path.join(os.path.dirname(__file__), "persons")

  def __init__(self, soup):
    """
    :param soup: beautiful soup object with the link for a single person
    """
    self.url = "http://www.imdb.com" + soup['href']
    self.name = soup.string

  def __unicode__(self):
    return "Name: %s, URL: %s" % (self.name, self.url)

  def __str__(self):
    return unicode(self).encode("utf-8")

  def to_json(self):
    """
    :return: person details as json serializable object
    """
    return {'name': self.name, 'url': self.url}

  @property
  def local_path(self):
    """
     Name of html for each person
    :return: local path + filename.htm
    """
    path_parts = urlparse.urlsplit(self.url).path.split("/")
    assert path_parts[0] == '' and path_parts[1] == 'name'
    filename = path_parts[2] + ".html"
    return os.path.join(self.HTML_DIR, filename)

  def download_html(self):
    """
    Method to download html file for each person
    """
    if not os.path.exists(self.HTML_DIR):
      os.makedirs(self.HTML_DIR)
    if not os.path.exists(self.local_path):
      self.logger.info("Downloading %s", self.name)
      with codecs.open(self.local_path, 'w', encoding='utf-8') as f:
        r = requests.get(self.url)
        f.write(r.text)

  def person_description(self):
    with open(self.local_path) as f:
      soup = bs4.BeautifulSoup(f, 'html.parser')
    description = soup.find(id="name-bio-text")
    print description
    description = description.find(itemprop="description")
    if description:
      description = description.get_text()
    else:
      description = ""
    return description

  def gender(self):
    words = re.findall(r"\w+", self.person_description().lower())
    for word in words:
      if word in ['she', 'her', 'actress']:
        return 'female'
      if word in ['he', 'his', 'him', 'actor']:
        return 'male'
    return 'unknown'

class Movie(object):
  """
  Class for movie details
  """
  def __init__(self, soup):
    """
    :param soup: beautiful soup object with the movie block in html
    """
    self.title = soup.h3.a.string
    self.url = "http://www.imdb.com" + soup.h3.a['href']
    self.genre = soup.find('span', class_="genre").string.strip()
    self.rating = soup.find('div', class_="ratings-imdb-rating").strong.string

    # List of Directors and stars within tags
    people_tags = soup.find_all('p')[2].find_all(['span', 'a'])
    # Find the index of the span separator to break the list
    index = 0
    for tag in people_tags:
      if tag.name != 'span':
        index += 1
      else:
        break

    self.directors = [Person(p) for p in people_tags[0:index]]
    self.stars = [Person(p) for p in people_tags[index + 1:]]

  def __str__(self):
    return "Title: %s" % self.title

  def to_json(self):
    """
    :return: movie details as json serializable object
    """
    return {'title': self.title, 'url': self.url, 'genre': self.genre, 'rating': self.rating,
            'directors': [p.to_json() for p in self.directors], 'stars': [p.to_json() for p in self.stars]}

  def download_htmls(self):
    """
    Method to download html for each director and star
    """
    for person in self.directors:
      person.download_html()
    for person in self.stars:
      person.download_html()


class MovieCollection(object):
  """
  Class to hold a collection of movies
  """
  def __init__(self, filename):
    """
    :param filename: html containing movies records
    Open the html and access movies in the file
    """
    with open(filename) as f:
      soup = bs4.BeautifulSoup(f, 'html.parser')
    items = soup.find_all('div', class_="lister-item")
    self._movies = [Movie(item) for item in items]

  def to_json(self):
    """
    :return: collection as json serializable object
    """
    return {'movies': [movie.to_json() for movie in self._movies]}

  def save_to_json(self, filename):
    """
    :param filename: name of a file for saving movies data in json format
    """
    with open(filename, 'w') as f:
      json.dump(self.to_json(), f, sort_keys=True, indent=4, separators=(",", ": "))

  def __iter__(self):
      return iter(self._movies)

  def download_htmls(self):
    """
    Method to download all the htmls of all the persons in all the movies
    """
    for movie in self:
      movie.download_htmls()

def main():
  movies = MovieCollection('top_movies_2016.html')
  # movies.save_to_json('movies_collection2016.json')
  #person = next(iter(movies)).directors[0]
  persons = movies._movies[2].stars
  for person in persons:
    print person.name
    print person.gender()
    print
  #person.download_html()
  #movies.download_htmls()

if __name__ == '__main__':
  main()
