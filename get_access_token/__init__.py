#!/usr/bin/env python
#
# Copyright 2007-2013 The Python-Twitter Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import print_function

from requests_oauthlib import OAuth1Session
import webbrowser
import wx

REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
SIGNIN_URL = 'https://api.twitter.com/oauth/authenticate'


class BadAccess(BaseException):
    def __init__(self, msg):
        BaseException.__init__(self)
        self.msg = msg

    def __str__(self):
        return self.msg


class NotEmptyTextValidator(wx.PyValidator):
    """ This validator rejects an empty string, and accepts all others.
    """
    def __init__(self):
        wx.PyValidator.__init__(self)

    def Clone(self):
        return NotEmptyTextValidator()

    def Validate(self, win):
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()
        if len(text) == 0:
            wx.MessageBox("You must enter a pincode.", "Error")
            textCtrl.SetFocus()
            return False
        else:
            return True

    def TransferToWindow(self):
        return True;

    def TransferFromWindow(self):
        return True;


class WxAccessTokenDialog(wx.Dialog):
    def __init__(self, url, *args, **kwargs):
        super(WxAccessTokenDialog, self).__init__(*args,
            style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL,
            **kwargs)
        self.url = url

        pincodeField = wx.StaticBox(self, wx.ID_ANY, 'Pincode')
        pincodeFieldSizer = wx.StaticBoxSizer(pincodeField, wx.VERTICAL)
        self.pincodeTextCtrl_ = wx.TextCtrl(pincodeField, validator=NotEmptyTextValidator(), name='Pincode')
        pincodeFieldText = wx.StaticText(pincodeField,
            label='Once you grant access, twitter will display a pincode. '
                  'Please enter the pincode here.')
        pincodeFieldSizer.Add(pincodeFieldText, proportion=10, flag=wx.ALIGN_LEFT|wx.TOP)
        pincodeFieldSizer.Add(self.pincodeTextCtrl_, proportion=10, flag=wx.EXPAND|wx.CENTER)

        text = wx.StaticText(self,
            label='In order to read tweets, I need to be given access. '
                  'The "Grant Access" button will start a browser, where Twitter will ask if you want to grant access. '
                  'If you grant access, a pincode will be displayed, that you need to copy to the "Pincode" box below.')

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(text, proportion=10, flag=wx.ALIGN_LEFT|wx.TOP)
        vbox.Add(wx.Button(self, id=1, label="Grant Access"), flag=wx.ALIGN_CENTER)
        vbox.AddStretchSpacer(1)
        vbox.Add(pincodeFieldSizer, proportion=10, flag=wx.ALL|wx.EXPAND)
        vbox.AddStretchSpacer(1)
        vbox.Add(self.CreateButtonSizer(wx.OK | wx.CANCEL), flag=wx.ALIGN_CENTER)
        self.SetSizer(vbox)
        print(pincodeFieldSizer)

        self.Bind(wx.EVT_BUTTON, self.onGrantAccess_, id=1)

    def onGrantAccess_(self, event):
        webbrowser.open(self.url)

    def getPin_(self):
        return self.pincodeTextCtrl_.GetValue()

    pin = property(getPin_)


def wxGetAccessToken(consumer_key, consumer_secret, *args, **kwargs):
    oauth_client = OAuth1Session(consumer_key, client_secret=consumer_secret, callback_uri='oob')
    try:
        # Request temp token from twitter.
        resp = oauth_client.fetch_request_token(REQUEST_TOKEN_URL)
    except ValueError as e:
        raise BadAccess('Invalid response from Twitter requesting temp token: {0}'.format(e))

    # Dialog to ask for pin.
    url = oauth_client.authorization_url(AUTHORIZATION_URL)
    with WxAccessTokenDialog(url, *args, **kwargs) as dialog:
        if dialog.ShowModal() == wx.ID_OK:
            pincode = dialog.pin
        else:
            return None

    # Generating and signing request for an access token...
    oauth_client = OAuth1Session(consumer_key, client_secret=consumer_secret,
                                 resource_owner_key=resp.get('oauth_token'),
                                 resource_owner_secret=resp.get('oauth_token_secret'),
                                 verifier=pincode)
    try:
        resp = oauth_client.fetch_access_token(ACCESS_TOKEN_URL)
    except ValueError as e:
        raise BadAccess('Invalid response from Twitter requesting temp token: {0}'.format(e))

    return { 'consumer_key': consumer_key,
             'consumer_secret': consumer_secret,
             'access_token_key': '{0}'.format(resp.get('oauth_token')),
             'access_token_secret': '{0}'.format(resp.get('oauth_token_secret'))
           }


def get_access_token(consumer_key, consumer_secret):
    oauth_client = OAuth1Session(consumer_key, client_secret=consumer_secret, callback_uri='oob')

    print('\nRequesting temp token from Twitter...\n')

    try:
        resp = oauth_client.fetch_request_token(REQUEST_TOKEN_URL)
    except ValueError as e:
        raise 'Invalid response from Twitter requesting temp token: {0}'.format(e)

    url = oauth_client.authorization_url(AUTHORIZATION_URL)

    print('I will try to start a browser to visit the following Twitter page '
          'if a browser will not start, copy the URL to your browser '
          'and retrieve the pincode to be used '
          'in the next step to obtaining an Authentication Token: \n'
          '\n\t{0}'.format(url))

    webbrowser.open(url)
    pincode = raw_input('\nEnter your pincode? ')

    print('\nGenerating and signing request for an access token...\n')

    oauth_client = OAuth1Session(consumer_key, client_secret=consumer_secret,
                                 resource_owner_key=resp.get('oauth_token'),
                                 resource_owner_secret=resp.get('oauth_token_secret'),
                                 verifier=pincode)
    try:
        resp = oauth_client.fetch_access_token(ACCESS_TOKEN_URL)
    except ValueError as e:
        raise BadAccess('Invalid response from Twitter requesting temp token: {0}'.format(e))

    return { 'consumer_key': consumer_key,
             'consumer_secret': consumer_secret,
             'access_token_key': '{0}'.format(resp.get('oauth_token')),
             'access_token_secret': '{0}'.format(resp.get('oauth_token_secret'))
           }


def main():
    consumer_key = raw_input('Enter your consumer key: ')
    consumer_secret = raw_input('Enter your consumer secret: ')
    print(get_access_token(consumer_key, consumer_secret))


if __name__ == "__main__":
    main()
