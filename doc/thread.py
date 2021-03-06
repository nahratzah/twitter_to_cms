# BSD 2-Clause License
#
# Copyright (c) 2017, Ariane van der Steldt
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from __future__ import print_function
import twitter
import re
import tzlocal
from twitter_time import twitterTimestampToDatetime


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


def loadChain(api, tweet_id, print_fn=None):
    """ Download a tweet thread.

        api: a twitter API instance
        tweet_id: a tweet ID
        print_fn: a print function that accepts log messages
    """
    if print_fn is None:
        def print_fn_impl_(*args, **kwargs):
            print(*args, **kwargs)
        print_fn = print_fn_impl_

    result = list()
    try:
        while True:
            print_fn(u'Downloading {}...'.format(tweet_id))
            tweet = api.GetStatus(tweet_id)
            result.append(tweet)
            tweet_id = tweet.AsDict()['in_reply_to_status_id']
    except twitter.error.TwitterError as e:
        print_fn(u'Warning, parent tweet {0} does not exist'.format(tweet_id))
        print_fn(e)
    except KeyError:
        pass # No more tweets
    result.reverse()
    return result


def renderMediaPhotos(tweet):
    """ Returns a div with images, based on the tweet media.
        Returns None if the tweet has no image media.

        tweet: a tweet from which to extract media.
    """
    media_images = [x for x in tweet.media if x.type == 'photo']
    if len(media_images) == 0:
        return None
    images = [
        u'<img class="tweetImage {0.type}" src="{0.media_url_https}" alt="{1}" />'.format(img, htmlEscape(img.ext_alt_text, True))
        for img in media_images
        ]
    return u'<div class="tweetMedia tweetMediaPhoto tweetMediaCount{1}">{0}</div>'.format(u''.join(images), len(images))


def renderMediaAnimatedGif(tweet):
    """ Returns a div with a HTML5 video, based on the tweet media.
        Returns None if the tweet has no animated gif media.

        tweet: a tweet from which to extract media.
    """
    media_gifs = [x for x in tweet.media if x.type == 'animated_gif']
    if len(media_gifs) == 0:
        return None
    template = (u'<video class="tweetGif {0.type}" controls poster="{0.media_url_https}">'
        + u'<source type="{1[content_type]}" src="{1[url]}" />'
        + u'</video>')
    gifs = [
        template.format(img, img.video_info['variants'][0])
        for img in media_gifs
        ]
    return u'<div class="tweetMedia tweetMediaGif tweetMediaCount{1}">{0}</div>'.format(u''.join(gifs), len(gifs))


def renderMedia(tweet):
    """ Returns a div with images, based on the tweet media.
        Returns None if the tweet has no media.

        tweet: a tweet from which to extract media.
    """
    if tweet.media is None or len(tweet.media) == 0:
        return None
    return ((renderMediaPhotos(tweet) or u'')
        + (renderMediaAnimatedGif(tweet) or u''))


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


def applyParagraphs(tweet, txt):
    """ Apply <p> html tags to the text, to create paragraphs.
    """
    txt = re.sub(
        u'\n\n+',
        '</p>\n\n<p>',
        txt.strip(u'\n'),
        flags=re.IGNORECASE)
    return ur'<p>{0}</p>'.format(txt)


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
        txt = removeRetweetLink(tweet, txt)
    txt = removeMediaLinks(tweet, txt)

    # Apply paragraphs *after* media/retweet links have been erased.
    # Otherwise, we'll get empty paragraphs.
    txt = applyParagraphs(tweet, txt)

    # Apply retweets late after paragraphs, to prevent nesing <p> tags.
    if nestRetweets:
        txt = applyRetweet(tweet, txt)
    txt = applyLinks(tweet, txt)

    return txt;


def formatTextTweet(tweet, tweetClass=u'tweet', **kw):
    """ Format a tweet into HTML.

        The tweet is nested inside a paragraph and a link to the original tweet will be shown.

        tweet: a tweet to convert to a HTML block.
    """
    media = renderMedia(tweet)
    return u'<div class="{1}"><a class="tweetOriginal" href="https://twitter.com/{0.user.screen_name}/status/{0.id_str}">Original Tweet</a><div class="tweetText">{2}</div>{3}</div>'.format(tweet, tweetClass, tweetTextToHtml(tweet, **kw), media or '')


class ThreadDoc:
    def __init__(self, api, tweetId, *args, **kwargs):
        self.chain = loadChain(api, tweetId, *args, **kwargs)

    def unicode(self, print_fn=None):
        if print_fn is None:
            def print_fn_impl_(*args, **kwargs):
                print(*args, **kwargs)
            print_fn = print_fn_impl_

        if len(self.chain) == 0:
            print_fn(u'No data.')
            return u'<!-- No data. -->'

        created_at = twitterTimestampToDatetime(self.chain[0].created_at)
        print_fn(u'Thread timestamp looks like {0}.'.format(created_at))
        ltz = tzlocal.get_localzone()
        local_created_at = ltz.normalize(created_at.astimezone(ltz))
        print_fn(u'Local time zone looks like {0}, timestamp in localtime thus is {1}.'.format(ltz, local_created_at))

        return (u'<!-- Created at: {0} -->\n\n'.format(local_created_at)
            + u'\n\n'.join(u'<!-- Tweet {0} -->\n{1}'.format(x.id_str, formatTextTweet(x)) for x in self.chain)
            )
