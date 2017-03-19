#! /usr/bin/env python
import bs4
import json

class Person(object):
  """
  Class to define aperson in a movie
  """
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


def main():
  movies = MovieCollection('top_movies_2016.html')
  movies.save_to_json('movies_collection2016.json')

if __name__ == '__main__':
  main()
