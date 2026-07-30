"""
linguist.py

A small application for managing language-learning flashcards.

Three models are defined using SQLAlchemy ORM:
    - User: an account that owns decks and cards.
    - Deck: a named collection belonging to a user.
    - Card: a single flashcard (English word, Ukrainian translation, a tip).

Each model has a set of CRUD (Create, Read, Update, Delete) functions
built on top of a single shared SQLAlchemy session.
"""

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, or_
from sqlalchemy.orm import declarative_base, sessionmaker

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

engine = create_engine("sqlite:///linguist.db")
Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class User(Base):
    """A registered user of the Linguist application."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name!r}, email={self.email!r})>"


class Deck(Base):
    """A named collection of flashcards belonging to a user."""

    __tablename__ = "decks"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return f"<Deck(id={self.id}, name={self.name!r}, user_id={self.user_id})>"


class Card(Base):
    """A single flashcard: an English word, its Ukrainian translation, and a tip."""

    __tablename__ = "cards"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    word = Column(String, nullable=False)
    translation = Column(String, nullable=False)
    tip = Column(String)

    def __repr__(self):
        return (
            f"<Card(id={self.id}, word={self.word!r}, "
            f"translation={self.translation!r})>"
        )


Base.metadata.create_all(engine)


# ---------------------------------------------------------------------------
# User CRUD functions
# ---------------------------------------------------------------------------

def user_create(name, email, password):
    """Create a new user and return the User object."""
    user = User(name=name, email=email, password=password)
    session.add(user)
    session.commit()
    return user


def user_get_by_id(user_id):
    """Retrieve a user by their ID and return the User object (or None)."""
    return session.get(User, user_id)


def user_update_name(user_id, name):
    """Update the name of a user and return the updated User object."""
    user = session.get(User, user_id)
    if user is None:
        return None
    user.name = name
    session.commit()
    return user


def user_change_password(user_id, old_password, new_password):
    """
    Change the password of a user.

    The change only happens if `old_password` matches the user's current
    password. Returns True on success, False otherwise (user not found or
    wrong old password).
    """
    user = session.get(User, user_id)
    if user is None:
        return False
    if user.password != old_password:
        return False
    user.password = new_password
    session.commit()
    return True


def user_delete_by_id(user_id):
    """Delete a user by their ID. Returns True on success, False otherwise."""
    user = session.get(User, user_id)
    if user is None:
        return False
    session.delete(user)
    session.commit()
    return True


# ---------------------------------------------------------------------------
# Deck CRUD functions
# ---------------------------------------------------------------------------

def deck_create(name, user_id):
    """Create a new deck belonging to a user and return the Deck object."""
    deck = Deck(name=name, user_id=user_id)
    session.add(deck)
    session.commit()
    return deck


def deck_get_by_id(deck_id):
    """Retrieve a deck by its ID and return the Deck object (or None)."""
    return session.get(Deck, deck_id)


def deck_update(deck_id, name):
    """Update the name of a deck and return the updated Deck object."""
    deck = session.get(Deck, deck_id)
    if deck is None:
        return None
    deck.name = name
    session.commit()
    return deck


def deck_delete_by_id(deck_id):
    """Delete a deck by its ID. Returns True on success, False otherwise."""
    deck = session.get(Deck, deck_id)
    if deck is None:
        return False
    session.delete(deck)
    session.commit()
    return True


# ---------------------------------------------------------------------------
# Card CRUD functions
# ---------------------------------------------------------------------------

def card_create(user_id, word, translation, tip):
    """Create a new flashcard and return the Card object."""
    card = Card(user_id=user_id, word=word, translation=translation, tip=tip)
    session.add(card)
    session.commit()
    return card


def card_get_by_id(card_id):
    """Retrieve a flashcard by its ID and return the Card object (or None)."""
    return session.get(Card, card_id)


def card_filter(sub_word):
    """
    Retrieve all flashcards where `sub_word` appears (case-insensitively)
    in the word, translation, or tip fields.

    Returns a tuple of Card objects.
    """
    pattern = f"%{sub_word}%"
    cards = (
        session.query(Card)
        .filter(
            or_(
                Card.word.ilike(pattern),
                Card.translation.ilike(pattern),
                Card.tip.ilike(pattern),
            )
        )
        .all()
    )
    return tuple(cards)


def card_update(card_id, word=None, translation=None, tip=None):
    """
    Update one or more fields of a flashcard.

    Only fields that are not None are changed. Returns the updated Card
    object (or None if the card does not exist).
    """
    card = session.get(Card, card_id)
    if card is None:
        return None
    if word is not None:
        card.word = word
    if translation is not None:
        card.translation = translation
    if tip is not None:
        card.tip = tip
    session.commit()
    return card


def card_delete_by_id(card_id):
    """Delete a flashcard by its ID. Returns True on success, False otherwise."""
    card = session.get(Card, card_id)
    if card is None:
        return False
    session.delete(card)
    session.commit()
    return True
