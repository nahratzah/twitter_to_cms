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
from thread import ThreadDoc
import wx


class ThreadScreen(wx.Frame):
    """ A window that handles downloading a tweet.
    """

    def __init__(self, *args, **kwargs):
        self.api_ = kwargs['api']
        del kwargs['api']
        wx.Frame.__init__(self, *args, **kwargs)

        # Labeled box, with layout:
        #
        # 'Text describing purpose of the box'
        # [Input-field-for-tweet]  [Download-button]
        tweetBox = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, 'Tweet'), wx.VERTICAL)
        tweetBox.Add(
            wx.StaticText(tweetBox.GetStaticBox(),
                label='In this field, place the ID of the last tweet of the twitter thread you want to download.'),
            proportion=0,
            flag=wx.ALIGN_LEFT|wx.TOP)
        tweetBoxInputs = wx.BoxSizer(wx.HORIZONTAL)
        self.tweetIdCtrl_ = wx.TextCtrl(tweetBox.GetStaticBox(), name='Tweet ID', style=wx.TE_LEFT)
        tweetBoxInputs.Add(
            self.tweetIdCtrl_,
            proportion=1,
            flag=wx.ALIGN_LEFT|wx.EXPAND)
        tweetBoxInputs.Add(
            wx.Button(tweetBox.GetStaticBox(), id=1, label='Download'),
            flag=wx.ALIGN_RIGHT)
        tweetBox.Add(tweetBoxInputs, flag=wx.EXPAND)

        # Text field for output HTML
        self.outputHtml_ = wx.TextCtrl(self, name='Output HTML', style=wx.TE_AUTO_SCROLL|wx.TE_DONTWRAP|wx.TE_MULTILINE)

        # Text field for log
        # Labeled box, with layout:
        #
        # 'multi-line text field with log messages'
        logBox = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, 'Log'), wx.HORIZONTAL)
        self.log_ = wx.TextCtrl(logBox.GetStaticBox(), name='Log', style=wx.TE_AUTO_SCROLL|wx.TE_DONTWRAP|wx.TE_MULTILINE|wx.TE_READONLY)
        logBox.Add(self.log_, proportion=1, flag=wx.EXPAND)

        mainBox = wx.BoxSizer(wx.VERTICAL)
        mainBox.Add(tweetBox, flag=wx.EXPAND)
        mainBox.AddStretchSpacer()
        mainBox.Add(self.outputHtml_, proportion=20, flag=wx.EXPAND)
        mainBox.AddStretchSpacer()
        mainBox.Add(logBox, proportion=1, flag=wx.EXPAND)
        self.SetSizer(mainBox)

        self.Bind(wx.EVT_BUTTON, self.onDownload_, id=1)


    def onDownload_(self, event):
        self.doc_ = ThreadDoc(self.api_, self.tweetIdCtrl_.GetValue(), print_fn=lambda x: self.appendLog_(x))
        self.outputHtml_.SetValue(self.doc_.unicode())

    def appendLog_(self, *args):
        for a in args:
            self.log_.AppendText(u'{0}\n'.format(a))
