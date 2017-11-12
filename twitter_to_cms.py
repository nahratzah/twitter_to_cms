#!/usr/bin/env python2
from __future__ import print_function
import twitter
import re


def htmlEscape(s, quoted=False):
  """ Escape text for HTML.

      s: a text to escape.
      quoted: if True, single and double quotes will be converted
              to HTML entities (required for html attributes to work).
  """
  s = s.replace(u'&', u'&amp;')
  s = s.replace(u'<', u'&lt;')
  s = s.replace(u'>', u'&gt;')
  if (quoted):
    s = s.replace(u"\'", u'&apos;')
    s = s.replace(u"\"", u'&quot;')
  return s


def loadChain(api, tweet_id):
  """ Download a tweet thread.

      api: a twitter API instance
      tweet_id: a tweet ID
  """
  result = list()
  try:
    while True:
      print(u'Downloading {}...'.format(tweet_id))
      tweet = api.GetStatus(tweet_id)
      result.append(tweet)
      tweet_id = tweet.AsDict()['in_reply_to_status_id']
  except twitter.error.TwitterError as e:
    print(u'Warning, parent tweet {0} does not exist'.format(tweet_id))
    print(e)
  except KeyError:
    pass # No more tweets
  result.reverse()
  return result


def renderMedia(tweet):
  """ Returns a div with images, based on the tweet media.
      Returns None if the tweet has no media.

      tweet: a tweet from which to extract media.
  """
  if tweet.media is None or len(tweet.media) == 0:
    return None
  images = [
    u'<img class="tweetImage {0.type}" src="{0.media_url_https}" alt="{1}" />'.format(img, htmlEscape(img.ext_alt_text, True))
    for img in tweet.media
    ]
  imageCount = len(images)
  return u'<div class="tweetMedia tweetMediaCount{1}">{0}</div>'.format(u''.join(images), imageCount)


def removeMediaLinks(tweet, txt):
  """ Remove media links from the tweet.

      tweet: a tweet with zero or more media links.
      txt: a text from which to remove media links.
  """
  if tweet.media is None or len(tweet.media) == 0:
    return txt
  for img in tweet.media:
    txt = txt.replace(img.url, u'')
  return txt


def applyHashTags(tweet, txt):
  """ Wraps hashtags inside an appropriate link.
      If the tweet has no hashtags, the text is returned without change.

      tweet: a tweet with zero or more hash tags.
      txt: the text on which to apply replacement.
  """
  if tweet.hashtags is None or len(tweet.hashtags) == 0:
    return txt
  for tag in tweet.hashtags:
    txt = txt.replace(ur'#{0}'.format(tag.text),
        ur'<a class="tweetHashTag" href="https://twitter.com/hashtag/{1}">#{0}</a>'.format(
            htmlEscape(tag.text), htmlEscape(tag.text, True)
        ))
  return txt


def applyMentions(tweet, txt):
  """ Wraps mentions (@-username) inside an appropriate link.
      If the tweet has no mentions, the text is returned without change.

      tweet: a tweet with zero or more mentions.
      txt: the text on which to apply replacement.
  """
  if tweet.user_mentions is None or len(tweet.hashtags) == 0:
    return txt
  for user in tweet.user_mentions:
    txt = re.sub(ur'@{0}'.format(user.screen_name),
        ur'<a title="{2} on twitter" class="tweetMention" href="https://twitter.com/{1}">@{0}</a>'.format(
            htmlEscape(user.screen_name), htmlEscape(user.screen_name, True), htmlEscape(user.name, True)
        ),
        txt,
        flags=re.IGNORECASE)
  return txt


def applyLinks(tweet, txt):
  """ Replaces the short links in a tweet with long links,
      nicely rendered inside an appropriate anchor.

      tweet: a tweet from which to extract links.
      txt: the text in which to replace the links.
  """
  for url in tweet.urls:
    txt = txt.replace(
        url.url,
        u'<a class="tweetLink" href="{0}">{0}</a>'.format(url.expanded_url))
  return txt


def applyRetweet(tweet, txt):
  """ Add a quoted-tweet html fragment to the rendered text.
      If the tweet has no quoted tweet, the original text is returned.

      tweet: a tweet, may or may not have a quoted tweet.
      txt: the text to which to append the quoted tweet HTML.
  """
  if tweet.quoted_status is None:
    return txt
  quoted = formatTextTweet(tweet.quoted_status, tweetClass=u'retweet', nestRetweets=False)
  return u'{0}\n\n{1}'.format(txt, quoted)


def removeRetweetLink(tweet, txt):
  """ Erase all quoted-tweets links from a tweet.
      If the tweet has no quoted tweet, the text is returned without change.

      tweet: a tweet, which may have retweet links.
      txt: a text from which to erase retweet links.
  """
  if tweet.quoted_status is not None:
    re_link = re.compile(ur'^https?://twitter\.\S+/\S+/status/{0.id_str}$'.format(tweet.quoted_status), re.UNICODE)
    for u in tweet.urls:
      if re_link.match(u.expanded_url):
        txt = txt.replace(u.url, u'')
  return txt


def tweetTextToHtml(tweet, nestRetweets=True):
  """ Convert contents of a tweet to HTML.
      The returned text contains a mix of text and HTML.

      tweet: the tweet of which the contents is to be rendered as HTML.
      nextRetweets: if true, retweets will be expanded and their link removed.
  """
  txt = tweet.full_text
  txt = applyMentions(tweet, txt)
  txt = applyHashTags(tweet, txt)
  if nestRetweets:
    txt = applyRetweet(tweet, txt)
    txt = removeRetweetLink(tweet, txt)
  txt = removeMediaLinks(tweet, txt)
  txt = applyLinks(tweet, txt)
  return txt;


def formatTextTweet(tweet, tweetClass=u'tweet', **kw):
  """ Format a tweet into HTML.

      The tweet is nested inside a paragraph and a link to the original tweet will be shown.

      tweet: a tweet to convert to a HTML block.
  """
  media = renderMedia(tweet)
  return u'<div class="{1}"><a class="tweetOriginal" href="https://twitter.com/{0.user.screen_name}/status/{0.id_str}">Original Tweet</a><span class="tweetText">{2}</span>{3}</div>'.format(tweet, tweetClass, tweetTextToHtml(tweet, **kw), media or '')


def buildTwitterApi():
  """ Create the twitter API.
      Handles acquiring authentication token.
  """
  keys = get_access_token(
      consumer_key='KGDRrUHmEJYKWSo5pIDsiVpFt',
      consumer_secret='10FXCOswIKE6Lr5mJwvifcJQ1dyACT2jYAuFppsBkg9H9JypGX')
  return twitter.Api(tweet_mode='extended', sleep_on_rate_limit=True, **keys)


def createTweetDoc(api, tweetId):
  """ Create a unicode string with HTML, representing the tweet document.

      throws: LookupError exception if the thread can not be downloaded.

      api: a twitter API, with tweet_mode='extended'
      tweetId: the numeric ID of the last tweet in the thread that is to be rendered.
  """
  chain = loadChain(api, last_tweet)
  if len(chain) == 0:
    raise LookupError('No tweet found.')
  return (u'<!-- Created at: {0.created_at} -->\n\n'.format(chain[0])
      + u'\n\n'.join(u'<!-- Tweet {0} -->\n{1}'.format(x.id_str, formatTextTweet(x)) for x in chain)
      )


if __name__ == '__main__':
  import sys
  from get_access_token import get_access_token

  try:
    last_tweet = sys.argv[1]
  except IndexError:
    print('Please invoke as: %s tweet_id' % (sys.argv[0],))
    sys.exit(1)

  api = buildTwitterApi()
  try:
    doc = createTweetDoc(api, last_tweet)
  except LookupError as e:
    print(e)
    sys.exit(1)

  sys.stdout.write(doc.encode('utf8'))
  print()
