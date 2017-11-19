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


class NotEmptyTextValidator(wx.Validator):
    """ This validator rejects an empty string, and accepts all others.
    """
    def __init__(self):
        wx.Validator.__init__(self)

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
    """ Dialog that has a button to open a browser to a given URL and accept a pincode.
    """

    def __init__(self, url, *args, **kwargs):
        """ Constructor.

            url: URL to which the browser is to open, to get granted access.
                 When access is granted, the webpage is to display a pincode
                 that the user can copy into the pincode field.
        """
        super(WxAccessTokenDialog, self).__init__(*args,
            style=wx.DEFAULT_DIALOG_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL,
            **kwargs)
        self.url = url

        pincodeField = wx.StaticBox(self, wx.ID_ANY, 'Pincode')
        pincodeFieldSizer = wx.StaticBoxSizer(pincodeField, wx.VERTICAL)
        self.pincodeTextCtrl_ = wx.TextCtrl(pincodeField, validator=NotEmptyTextValidator(), name='Pincode', style=wx.TE_CENTRE)
        self.storeCtrl_ = wx.CheckBox(pincodeField, label='Remember Credentials', style=wx.CHK_2STATE)
        pincodeFieldText = wx.StaticText(pincodeField,
            label='Once you grant access, twitter will display a pincode. '
                  'Please enter the pincode here.')
        pincodeFieldSizer.Add(pincodeFieldText, proportion=10, flag=wx.ALIGN_LEFT|wx.TOP)
        pincodeFieldSizer.Add(self.pincodeTextCtrl_, proportion=10, flag=wx.EXPAND|wx.CENTER)
        pincodeFieldSizer.Add(self.storeCtrl_, proportion=10, flag=wx.EXPAND|wx.CENTER)

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

        self.Bind(wx.EVT_BUTTON, self.onGrantAccess_, id=1)

    def onGrantAccess_(self, event):
        """ Button event that opens the URL.
        """
        webbrowser.open(self.url)

    def getPin_(self):
        """ Property accessor that retrieves the pincode, that the user has entered.
        """
        return self.pincodeTextCtrl_.GetValue()

    def getStore_(self):
        """ Property accessor that retrieves the store checkbox value.
        """
        return self.storeCtrl_.IsChecked()

    pin = property(getPin_)
    store = property(getStore_)


def wxGetAccessToken(consumer_key, consumer_secret, *args, **kwargs):
    """ Perform OAuth authentication against the twitter API.
        This function uses a modal dialog to get the user to enter a pincode.

        Returns a dictionary of access tokens on success.
        If the user cancels the operation, None is returned.
    """
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
            store = dialog.store
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
             'access_token_secret': '{0}'.format(resp.get('oauth_token_secret')),
             'store': store
           }
