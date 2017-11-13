import wx


class ThreadScreen(wx.Frame):
    """ A window that handles downloading a tweet.
    """

    def __init__(self, *args, **kwargs):
        api = kwargs['api']
        del kwargs['api']
        print 'ThreadScreen.__init__: api={0}, args={1}, kwargs={2}'.format(api, args, kwargs)
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
        tweetBoxInputs.Add(
            wx.TextCtrl(tweetBox.GetStaticBox(), name='Tweet ID', style=wx.TE_LEFT),
            proportion=1,
            flag=wx.ALIGN_LEFT|wx.EXPAND)
        tweetBoxInputs.Add(
            wx.Button(tweetBox.GetStaticBox(), label='Download'),
            flag=wx.ALIGN_RIGHT)
        tweetBox.Add(tweetBoxInputs, flag=wx.EXPAND)

        # Text field for output HTML
        outputHtml = wx.TextCtrl(self, name='Output HTML', style=wx.TE_AUTO_SCROLL|wx.TE_DONTWRAP|wx.TE_MULTILINE)

        # Text field for log
        # Labeled box, with layout:
        #
        # 'multi-line text field with log messages'
        logBox = wx.StaticBoxSizer(wx.StaticBox(self, wx.ID_ANY, 'Log'), wx.HORIZONTAL)
        log = wx.TextCtrl(logBox.GetStaticBox(), name='Log', style=wx.TE_AUTO_SCROLL|wx.TE_DONTWRAP|wx.TE_MULTILINE|wx.TE_READONLY)
        logBox.Add(log, proportion=1, flag=wx.EXPAND)

        mainBox = wx.BoxSizer(wx.VERTICAL)
        mainBox.Add(tweetBox, flag=wx.EXPAND)
        mainBox.AddStretchSpacer()
        mainBox.Add(outputHtml, proportion=20, flag=wx.EXPAND)
        mainBox.AddStretchSpacer()
        mainBox.Add(logBox, proportion=1, flag=wx.EXPAND)
        self.SetSizer(mainBox)
