from datetime import datetime, timedelta

tzinfo = {u'Algeria': 0,
 u'Antarctica': -4,
 u'Argentina': 0,
 u'Armenia': 3,
 u'Austria': 1,
 u'Australia': 10,
 u'Belarus': 2,
 u'Belgium': 0,
 u'Bosnia and Herzegovina': 1,
 u'Brazil': -3,
 u'British Indian Ocean Territory': 5,
 u'Bulgaria': 0,
 u'Canada': -5,
 u'Chile': -5,
 u'China': 8,
 u'Colombia': 0,
 u'Congo, the Democratic Republic of the': 1,
 u"Cote D'Ivoire": 0,
 u'Croatia': 1,
 u'Czech Republic': 1,
 u'Estonia': 2,
 u'Finland': 2,
 u'France': 1,
 u'Germany': 1,
 u'Greece': 2,
 u'Hungary': 1,
 u'Iceland': 0,
 u'India': 5,
 u'Ireland': 0,
 u'Israel': 2,
 u'Italy': 1,
 u'Japan': 9,
 u"Korea, Democratic People's Republic of": 7,
 u'Latvia': 2,
 u'Lithuania': 2,
 u'Macedonia': 1,
 u'Malta': 1,
 u'Mexico': -6,
 u'Morocco': 0,
 u'Netherlands': 1,
 u'Netherlands Antilles': -4,
 u'New Zealand': 12,
 u'Nicaragua': -6,
 u'Northern Mariana Islands': 10,
 u'Norway': 1,
 u'Peru': -5,
 u'Poland': 1,
 u'Portugal': 0,
 u'Romania': 1,
 u'Russian Federation': 4,
 u'Serbia': 1,
 u'Singapore': 7,
 u'Slovakia': 1,
 u'Slovenia': 1,
 u'Spain': 1,
 u'Sweden': 1,
 u'Switzerland': 1,
 u'Thailand': 7,
 u'Trinidad and Tobago': -4,
 u'Tunisia': 1,
 u'Turkey': 2,
 u'United Kingdom': 0,
 u'United States': -7,
 u'United States Minor Outlying Islands': -11,
 u'Venezuela': -4.5,
 u'Zimbabwe': 0}

def shift(timestamp, country):
    new_timestamp = timestamp
    if country in tzinfo:
        delta = timedelta(hours=tzinfo[country])
        new_timestamp += delta

    return new_timestamp
