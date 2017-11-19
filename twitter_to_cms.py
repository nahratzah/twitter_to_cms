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


# Keyring constants.
# The system is the subsystem of this application.
# Since the twitter authentication uses opaque keys, we "fake" a username.
# All keys are in the password field.
KEYRING_SYSTEM_NAME = u'TwitterToCms.twitter'
KEYRING_SYSTEM_USERNAME = u'twitter'


def getKeyringAccessToken(consumer_key, consumer_secret):
    import keyring

    password = keyring.get_password(KEYRING_SYSTEM_NAME, KEYRING_SYSTEM_USERNAME)
    if password is None:
        return None
    try:
        (access_token_key, access_token_secret) = password.split('\n')
        return { 'consumer_key': consumer_key,
                 'consumer_secret': consumer_secret,
                 'access_token_key': access_token_key,
                 'access_token_secret': access_token_secret
               }
    except StandardError:
        return None


def setKeyringAccessToken(access_token_key, access_token_secret, **ignored):
    import keyring

    password = '\n'.join([access_token_key, access_token_secret])
    keyring.set_password(KEYRING_SYSTEM_NAME, KEYRING_SYSTEM_USERNAME, password)


def wxBuildTwitterApi(consumer_key, consumer_secret):
    """ Create the twitter API.
        Handles acquiring authentication token.
    """
    from get_access_token import wxGetAccessToken

    return wxGetAccessToken(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        parent=None,
        title='Twitter to CMS: twitter authorization')


def buildTwitterApi():
    import twitter

    methods = [ getKeyringAccessToken, wxBuildTwitterApi ]
    consumer_key='KGDRrUHmEJYKWSo5pIDsiVpFt'
    consumer_secret='10FXCOswIKE6Lr5mJwvifcJQ1dyACT2jYAuFppsBkg9H9JypGX'

    for method in methods:
        # Try to acquire keys using method.
        keys = method(consumer_key=consumer_key, consumer_secret=consumer_secret)
        if keys is not None:
            # If key store is present, take it out of the keys
            try:
                store = keys['store']
                del keys['store']
            except KeyError:
                store = False

            # Use keys to create API
            api = twitter.Api(tweet_mode='extended', sleep_on_rate_limit=True, **keys)
            # Verify keys are valid
            verify = api.VerifyCredentials()
            if verify is not None:
                # Valid API instance
                if store:
                    setKeyringAccessToken(**keys)
                return api
    # Give up
    return None


if __name__ == '__main__':
    import sys
    import wx
    import doc

    app = wx.App()
    api = buildTwitterApi()
    if api is None:
        sys.exit(1) # User canceled authentication
    frm = doc.ThreadScreen(None, api=api, title='Twitter to CMS')
    frm.Show()
    app.MainLoop()
