"""
Common functionality for sqlalchemy schemas.
"""

import hashlib
import uuid

from datetime import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    DateTime,
    Unicode,
)


DeclarativeBase = declarative_base()


def eid_gen():
    """
    Generates an unique eid based on a random string.

    :returns: a unique random string.
    """
    sha = hashlib.sha1('{}'.format(uuid.uuid4()).encode())
    return sha.hexdigest()


class AuditableMixing(object):
    """
    Table mixing to add the common fields in our database, to make it auditable
    we add timestamps and an eid field as primary key just for convenience.
    """

    eid = Column(Unicode(40), primary_key=True, default=eid_gen)
    created = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )
    modified = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    @classmethod
    def find_by_eid(cls, database, eid):
        """
        Finds a model by it's eid of a chunk of it, returns None if there are
        no models matching the eid chunk.

        :param db: sqlalchemy session to find the item.
        :param eid: eid to match, can be a partial.
        :returns: the model if its found None otherwise.
        """
        return database.query(cls).filter(cls.eid.like('{}%'.format(eid))).first()

    @classmethod
    def latest(cls, database):
        """
        Finds the latest model in the given db.

        :param db: sqlalchemy session to find the item.
        :returns: the latest model if its found None otherwise.
        """
        return database.query(cls).order_by(cls.created.desc()).first()
    

    @classmethod
    def list(cls, database, count=None):
        query = database.query(cls).order_by(cls.created.desc())
        if count is not None:
            query = query.limit(count)
        return query.all()

    @classmethod
    def count(cls, database):
        query = database.query(cls)
        return query.count()
