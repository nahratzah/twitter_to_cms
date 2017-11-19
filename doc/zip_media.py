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
import thread
import zipfile
import re
import urllib2
import os.path


def filenameForUrl(url, subdir=None):
    """ Returns the file name portion of a URL.

        url: a URL containing a file component
        subdir: a subdir path to prepend to the file name

        Example:
        filenameForUrl('http://host/dir1/dir2/file.ext?arg#anchor') -> 'file.ext'
    """
    name = re.sub('[?#].*$', '', url).split('/')[-1]
    if subdir is None:
        return name
    return os.path.join(subdir, name)


class TwitterMediaZipFile(zipfile.ZipFile):
    def __init__(self, file, mode='w'):
        """ Create a zip file for twitter media.
        """
        zipfile.ZipFile.__init__(self, file, mode, zipfile.ZIP_DEFLATED)

    def addTweetMedia(self, tweet, subdir=None, print_fn=print):
        """ Add media from tweet to the current zip file.
        """
        if tweet.media is None:
            return dict()

        # Extract all URLs
        urls = []
        for media in tweet.media:
            if media.type == 'photo':
                urls.append(media.media_url_https)
            elif media.type == 'animated_gif':
                urls.append(media.media_url_https)
                for variant in media.video_info['variants']:
                    urls.append(variant['url'])

        url_name_map = dict()
        url_name_map = { url: filenameForUrl(url, subdir=subdir) for url in urls }

        for url, fname in url_name_map.iteritems():
            print_fn('Downloading {1} from {0}...'.format(url, fname))
            data = urllib2.urlopen(url)
            self.writestr(fname, data.read())
        return url_name_map
