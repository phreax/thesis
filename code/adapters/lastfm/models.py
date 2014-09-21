from sqlalchemy import Column, Integer, String, ForeignKey, types
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
import timezones

Base = declarative_base()
Session = sessionmaker()
db_name = 'sqlite:///db/lastfm.sqlite'

class QueryExtension:
    engine = create_engine(db_name, encoding='utf-8')
    session = Session(bind=engine)

    @classmethod
    def bind(cls,engine):
        cls.engine = engine
        cls.session = Session(bind=engine)

    @classmethod
    def query(cls):
        return cls.session.query(cls)

    @classmethod
    def drop(cls):
        return cls.__table__.drop(cls.engine)

    @classmethod
    def create(cls):
        return cls.__table__.create(cls.engine)

class Artist(Base,QueryExtension):
    """LastFM artist model"""

    __tablename__ = "artists"

    id    = Column(Integer,primary_key=True)
    uid   = Column(String)
    name  = Column(String)

    def __init__(self,uid,name):
        self.uid   = uid
        self.name  = name

    def __repr__(self):
        return "<Artist(id='%s',name='%s')>" % (self.id,self.name.encode('utf-8'))

class User(Base,QueryExtension):
    """LastFM user model"""

    __tablename__ = "users"
    id       = Column(Integer,primary_key=True)
    gender   = Column(String)
    country  = Column(String)
    name     = Column(String)
    age      = Column(Integer)

    registered_at = Column(types.DateTime())

    def __init__(self,name,gender,age,country,registered_at=None):
        self.name          = name
        self.gender        = gender
        self.age           = age
        self.country       = country
        self.registered_at = registered_at

    def __repr__(self):
        return "<User(id='%s',name='%s',country='%s')>" % (self.id,self.name.encode('utf-8'),self.country)

class Track(Base,QueryExtension):
    """LastFM track model"""

    __tablename__ = "tracks"

    id         = Column(Integer,primary_key=True)
    name       = Column(String)
    uid        = Column(String)
    artist_id  = Column(Integer, ForeignKey('artists.id'),index=True)
    artist     = relationship("Artist", backref=backref('tracks',order_by=id))

    def __init__(self,name,uid):
        self.uid  = uid
        self.name = name

    def __repr__(self):
        return "<Track(id='%s',name='%s')>" % (self.id,self.name.encode('utf-8'))

class Tag(Base, QueryExtension):
    """LastFM tag model"""

    __tablename__ = "tags"

    id         = Column(Integer, primary_key=True)
    name       = Column(String, unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<Tag(id='%s',name='%s')>" % (self.id,self.name.encode('utf-8'))

class ArtistTag(Base, QueryExtension):
    """LastFM artist-tag join model"""

    __tablename__ = "artist_tags"

    id          = Column(Integer, primary_key=True)
    artist_id   = Column(Integer, ForeignKey('artists.id'), nullable=False, index=True)
    tag_id      = Column(Integer, ForeignKey('tags.id'), nullable=False, index=True)
    relevance   = Column(Integer, nullable=False, index=True)

    artist = relationship("Artist",backref=backref('tags', order_by=relevance.desc(), lazy='dynamic'))
    tag    = relationship("Tag",lazy='joined')
    def __init__(self, relevance):
        self.relevance = relevance

    @property
    def name(self):
        return self.tag.name

    def __repr__(self):
        return "<ArtistTag(id='%s',name='%s',relevance='%d')>" % (self.id,self.name,self.relevance)


class ListenEvent(Base,QueryExtension):
    """LastFM listen event model"""

    __tablename__ = "listen_events"

    id         = Column(Integer,primary_key=True)
    track_id   = Column(Integer, ForeignKey('tracks.id'),nullable=False,index=True)
    user_id    = Column(Integer, ForeignKey('users.id'),nullable=False,index=True)
    timestamp  = Column(types.DateTime(),nullable=False,index=True)

    track = relationship("Track",backref=backref('listen_events',order_by=timestamp,lazy='dynamic'))
    user  = relationship("User",backref=backref('listen_events',order_by=timestamp,lazy='dynamic'))

    def __init__(self,timestamp,track_id,user_id):
        self.timestamp  = timestamp
        self.track_id   = track_id
        self.user_id    = user_id

    def __repr__(self):
        return "<ListenEvent(id='%s',track_id='%s',user_id='%s',timestamp='%s')>" % (self.id,self.track_id,self.user_id,self.timestamp)

    @property
    def item_id(self):
        return self.track_id

    @property
    def item(self):
        return self.track

    @property
    def local_timestamp(self):
        return timezones.shift(self.timestamp, self.user.country)

    @classmethod
    def first(cls):
        return cls.query().order_by(cls.timestamp).limit(1).first()

    @classmethod
    def last(cls):
        return cls.query().order_by(cls.timestamp.desc()).limit(1).first()

    @hybrid_method
    def percentile(self,n,of=10):

        if of<1:
            raise "of must be greater than 1"
        if n < 1 or n > of:
            raise "n must be in range 0 < n <= of"

        tfirst = self.first().timestamp
        tlast  = self.last().timestamp

        period = tlast - tfirst
        t1 = tfirst + (n-1)*(period/of)
        t2 = tfirst + n*(period/of)

        return (self.timestamp > t1) & (self.timestamp < t2)
