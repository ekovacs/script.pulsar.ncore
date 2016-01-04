from pulsar import provider
import sys, os
import threading
import base64
import hashlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'site-packages'))

import cookielib
import mechanize
import bencode
from bs4 import BeautifulSoup
import re
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

LOCAL_TORRENT_CFG = {
  "host": 'localhost',
  "port": 41282,
  "status": 0
}

try:
  import StorageServer
except:
  import storageserverdummy as StorageServer

cache = StorageServer.StorageServer("script.pulsar.ncore", 1)
cache.table_name = "script.pulsar.ncore"


#This class will handles any incoming request
class torrentHandler(BaseHTTPRequestHandler):

  #Handler for the GET requests
  def do_GET(self):
    global cache

    self.send_response(200)

    torrent_id = self.path.replace('/', '').replace('.torrent', '')

    self.send_header('Content-type','application/x-bittorrent')
    self.end_headers()
    self.wfile.write(base64.b64decode(cache.get("torrent_" + torrent_id)))

    return


def runLocalTorrent():
  global LOCAL_TORRENT_CFG
  try:
    server = HTTPServer(('', LOCAL_TORRENT_CFG['port']), torrentHandler)
    thread = threading.Thread(target = server.serve_forever)
    thread.daemon = True
    thread.start()
    LOCAL_TORRENT_CFG['status'] = 1

  except KeyboardInterrupt:
    server.socket.close()

def ncore():
  # Browser
  br = mechanize.Browser()

  # Cookie Jar
  cj = cookielib.LWPCookieJar()
  br.set_cookiejar(cj)

  # Browser options
  br.set_handle_equiv(True)
  br.set_handle_redirect(True)
  br.set_handle_referer(True)
  br.set_handle_robots(False)
  br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

  br.addheaders = [('User-agent', 'Chrome')]

  br.open('https://ncore.cc')

  br.select_form(name='login')

  br['nev'] = provider.ADDON.getSetting('username')
  br['pass'] = provider.ADDON.getSetting('password')

  br.submit()
  return br

def ncore_search(title, search_type='movie'):
  global cache

  search_id = hashlib.sha224(title + search_type).hexdigest()

  cached_search = cache.get('search_'+ search_id)

  if cached_search:
    return eval(cached_search)

  ncore_browser = ncore()
  ncore_browser.open('https://ncore.cc/torrents.php')
  ncore_browser.select_form(name='kereses_mezo')
  ncore_browser.form['mire'] = title
  ncore_browser.form['miben'] = ["name",]
  ncore_browser.form['tipus'] = ["kivalasztottak_kozott",]

  movie_filters = ['xvid_hun', 'xvid', 'hd', 'hd_hun']
  serial_filters = ['xvidser_hun', 'xvidser', 'hdser', 'hdser_hun']

  if search_type == 'movie+serial':
    filters = movie_filters + serial_filters
  elif search_type == 'movie':
    filters = movie_filters
  elif search_type == 'serial':
    filters = serial_filters

  ncore_browser.form['kivalasztott_tipus[]'] = filters
  ncore_browser.submit()
  html = ncore_browser.response().read()

  results = ncore_extract_data(html)
  cache.set('search_' + search_id, repr(results))
  return results

def extract_torrent_info(data):
  metadata = bencode.bdecode(data)
  hashcontents = bencode.bencode(metadata['info'])
  digest = hashlib.sha1(hashcontents).hexdigest()
  trackers = [metadata["announce"]]

  return {
    'info_hash': digest,
    'trackers': trackers
  }


def ncore_extract_data(html):
  global cache
  global LOCAL_TORRENT_CFG

  ncore_browser = ncore()
  soup = BeautifulSoup(html, 'html.parser')
  torrent_anchors = soup.findAll('a', href=re.compile(('^torrents.php\?action=details(.*)\d$')))
  results = []

  count = 0
  max_results = 5

  for item in torrent_anchors:
    torrent_id = item['href'].split('=')[2]
    download_link = 'https://ncore.cc/torrents.php?action=download&id=' + torrent_id
    data = ncore_browser.open(download_link).read()
    torrent_title = item['title'].encode('utf8').replace(' ', '.').replace('-', '.').replace('+', '.').replace('\'', '.')
    cache.set('torrent_' + torrent_id, base64.b64encode(data))
    torrent_info = extract_torrent_info(data)
    local_torrent_url = "http://"+ LOCAL_TORRENT_CFG['host'] + ":" + str(LOCAL_TORRENT_CFG['port']) +  "/" + str(torrent_id) + ".torrent"
    count += 1

    results.append({
      "uri": local_torrent_url,
      "name": torrent_title,
      "info_hash": torrent_info['info_hash'],
      "is_private": True,
      "trackers": torrent_info['trackers']
    })

    if count == max_results:
      break;

  return results

def search(query, search_type='movie+serial'):
  global LOCAL_TORRENT_CFG

  if LOCAL_TORRENT_CFG['status'] == 0:
    runLocalTorrent()

  return ncore_search(query, search_type)

def search_episode(episode):
  results = search("%(title)s S0%(season)02d E0%(episode)02d" % episode, 'serial')

  if not results:
    results = search("%(title)s S0%(season)02d E%(episode)02d" % episode, 'serial')

  if not results:
    results = search("%(title)s S%(season)02d E%(episode)02d" % episode, 'serial')

  if not results:
    results = search("%(title)s S%(season)02d E0%(episode)02d" % episode, 'serial')

  return results

def search_movie(movie):
  return search("%(title)s %(year)d" % movie, 'movie')

provider.register(search, search_movie, search_episode)
