import os
import sys
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    Text,
    DateTime,
    Float,
    Boolean)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Game(Base):
    __tablename__ = 'game'

    id = Column(Integer, primary_key=True)
    bgg_id = Column(Integer, nullable=False)
    name = Column(String(250), nullable=False)
    description = Column(Text)
    year = Column(Integer)
    gametype = Column(String(250), nullable=False)
    image = Column(String(250))
    thumbnail = Column(String(250))
    play_min = Column(Integer, nullable=False)
    play_max = Column(Integer, nullable=False)
    time_min = Column(Integer, nullable=False)
    time_max = Column(Integer, nullable=False)
    time_avg = Column(Integer, nullable=False)
    rank = Column(Integer)
    ratings = Column(Integer)
    rating = Column(Float)
    weighted_rating = Column(Float)
    weight = Column(Float)

class Artist(Base):
    __tablename__ = 'artist'

    id = Column(Integer, primary_key=True)
    art_id = Column(Integer, nullable=False)
    name = Column(String(250), nullable=False)

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    cat_id = Column(Integer, nullable=False)
    name = Column(String(250), nullable=False)

class Designer(Base):
    __tablename__ = 'designer'

    id = Column(Integer, primary_key=True)
    des_id = Column(Integer, nullable=False)
    name = Column(String(250), nullable=False)

class Mechanism(Base):
    __tablename__ = 'mechanism'

    id = Column(Integer, primary_key=True)
    mec_id = Column(Integer, nullable=False)
    name = Column(String(250), nullable=False)

class Publisher(Base):
    __tablename__ = 'publisher'

    id = Column(Integer, primary_key=True)
    pub_id = Column(Integer, nullable=False)
    name = Column(String(250), nullable=False)

class GameArtist(Base):
    __tablename__ = 'game_artist'

    id = Column(Integer, primary_key=True)
    bgg_id = Column(Integer, ForeignKey('game.bgg_id'))
    art_id = Column(Integer, ForeignKey('artist.art_id'))
    game = relationship(Game)
    art = relationship(Artist)

class GameCategory(Base):
    __tablename__ = 'game_category'

    id = Column(Integer, primary_key=True)
    bgg_id = Column(Integer, ForeignKey('game.bgg_id'))
    cat_id = Column(Integer, ForeignKey('category.cat_id'))
    game = relationship(Game)
    cat = relationship(Category)

class GameDesigner(Base):
    __tablename__ = 'game_designer'

    id = Column(Integer, primary_key=True)
    bgg_id = Column(Integer, ForeignKey('game.bgg_id'))
    des_id = Column(Integer, ForeignKey('designer.des_id'))
    game = relationship(Game)
    des = relationship(Designer)

class GameMechanism(Base):
    __tablename__ = 'game_mechanism'

    id = Column(Integer, primary_key=True)
    bgg_id = Column(Integer, ForeignKey('game.bgg_id'))
    mec_id = Column(Integer, ForeignKey('mechanism.mec_id'))
    game = relationship(Game)
    mec = relationship(Mechanism)

class GamePublisher(Base):
    __tablename__ = 'game_publisher'

    id = Column(Integer, primary_key=True)
    bgg_id = Column(Integer, ForeignKey('game.bgg_id'))
    pub_id = Column(Integer, ForeignKey('publisher.pub_id'))
    game = relationship(Game)
    pub = relationship(Publisher)

class GamePlayerPoll(Base):
    __tablename__ = 'game_player_poll'

    id = Column(Integer, primary_key=True)
    bgg_id = Column(Integer, ForeignKey('game.bgg_id'))
    player_count = Column(Integer, nullable=False)
    best = Column(Integer, nullable=False)
    recc = Column(Integer, nullable=False)
    nrec = Column(Integer, nullable=False)
    total = Column(Integer, nullable=False)
    game = relationship(Game)

class GameCollection(Base):
    __tablename__ = 'game_collection'

    id = Column(Integer, primary_key=True)
    bgg_id = Column(Integer, ForeignKey('game.bgg_id'))
    bgg_user = Column(String(250), nullable=False)
    stat_ownd = Column(Boolean, nullable=False)
    stat_pown = Column(Boolean, nullable=False)
    stat_fort = Column(Boolean, nullable=False)
    stat_want = Column(Boolean, nullable=False)
    stat_wtp = Column(Boolean, nullable=False)
    stat_wtb = Column(Boolean, nullable=False)
    stat_wish = Column(Boolean, nullable=False)
    stat_pre = Column(Boolean, nullable=False)
    num_plays = Column(Integer, nullable=False)
    user_rating = Column(Float)
    created_at = Column(DateTime, nullable=False)
    game = relationship(Game)

engine = create_engine('sqlite:///cache.db')

Base.metadata.create_all(engine)
