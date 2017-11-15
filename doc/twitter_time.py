import datetime
import twitter
import pytz


TWITTER_MONTHS_ = [
    u'Jan',
    u'Feb',
    u'Mar',
    u'Apr',
    u'May',
    u'Jun',
    u'Jul',
    u'Aug',
    u'Sep',
    u'Oct',
    u'Nov',
    u'Dec'
]


def twitterTimestampToDatetime(str_or_tweet):
    """ Constructs a datetime from a tweet, or its tweet.created_at field.

        Twitter tweets have a created_at field.
        It is a string, of the form u'Sat Nov 11 19:44:57 +0000 2017'.
        It's always in UTC.
        This function converts it to a datetime, so it can be changed to different timezones.

        str_or_tweet: a string/unicode, or a twitter.Status.
    """
    if isinstance(str_or_tweet, twitter.Status):
        s = str_or_tweet.created_at
    else if isinstance(str_or_tweet, str) or isinstance(str_or_tweet, unicode):
        s = str_or_tweet
    else:
        raise ValueError("twitterTimestampToDatetime requires a str/unicode or twitter.Status argument")

    # 's' is a date time string in US notation, with US names.
    # Switching to manual conversion, to prevent the need of global changes to locale.
    components = s.split(' ')
    if len(components) != 6:
        raise ValueError('Invalid timestamp')

    # components[0] = day of week, in 3 char abbreviation -- we discard this
    pass

    # components[1] = month, in 3 char abbreviation
    month = 1 + TWITTER_MONTHS_.index(components[1])

    # components[2] = day of month
    day = int(components[2])

    # components[3] = time, in HH:MM:SS notation
    time_components = components[3].split(':')
    if len(time_components) != 3:
        raise ValueError('Invalid timestamp')
    hour = int(time_components[0])
    minute = int(time_components[1])
    seconds = int(time_components[2])

    # components[4] = the timezone with value '+0000' -- we validate this
    if components[4] != '+0000':
        raise ValueError('Twitter timezones are supposed to be in UTC, indicated by +0000')

    # components[5] = year
    year = int(components[5])

    return pytz.utc.localize(datetime(year, month, day, hour, minute, second))
