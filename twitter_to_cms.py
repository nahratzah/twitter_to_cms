#!/usr/bin/env python
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


def wxBuildTwitterApi():
    """ Create the twitter API.
        Handles acquiring authentication token.
    """
    from get_access_token import wxGetAccessToken
    import twitter

    keys = wxGetAccessToken(
        consumer_key='KGDRrUHmEJYKWSo5pIDsiVpFt',
        consumer_secret='10FXCOswIKE6Lr5mJwvifcJQ1dyACT2jYAuFppsBkg9H9JypGX',
        parent=None,
        title='Twitter to CMS: twitter authorization')
    if keys is None:
        return None
    return twitter.Api(tweet_mode='extended', sleep_on_rate_limit=True, **keys)


if __name__ == '__main__':
    import sys
    import wx
    import doc

    app = wx.App()
    api = wxBuildTwitterApi()
    if api is None:
        sys.exit(1) # User canceled authentication
    frm = doc.ThreadScreen(None, api=api, title='Twitter to CMS')
    frm.Show()
    app.MainLoop()
