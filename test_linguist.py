"""
test_linguist.py

Test script for linguist.py. Creates users, decks, and flashcards, and
verifies every CRUD function using `assert` statements.

Run with:
    python test_linguist.py
"""

import os

# Start from a clean database file every time this script runs, so that
# repeated runs don't fail on unique-email constraints or leftover data.
DB_FILE = "linguist.db"
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

import linguist as ln


def test_user_crud():
    print("Testing User CRUD...")

    # CREATE
    user = ln.user_create("Олена", "olena@example.com", "secret123")
    assert user is not None
    assert user.id is not None
    assert user.name == "Олена"
    assert user.email == "olena@example.com"
    assert user.password == "secret123"

    # READ
    fetched = ln.user_get_by_id(user.id)
    assert fetched is not None
    assert fetched.id == user.id
    assert fetched.name == "Олена"

    # READ - non-existent user
    assert ln.user_get_by_id(999999) is None

    # UPDATE - name
    updated = ln.user_update_name(user.id, "Олена Коваль")
    assert updated is not None
    assert updated.name == "Олена Коваль"
    assert ln.user_get_by_id(user.id).name == "Олена Коваль"

    # UPDATE name - non-existent user
    assert ln.user_update_name(999999, "Хтось") is None

    # UPDATE - password with wrong old password should fail
    result = ln.user_change_password(user.id, "wrong_password", "new_pass")
    assert result is False
    assert ln.user_get_by_id(user.id).password == "secret123"

    # UPDATE - password with correct old password should succeed
    result = ln.user_change_password(user.id, "secret123", "new_pass456")
    assert result is True
    assert ln.user_get_by_id(user.id).password == "new_pass456"

    # UPDATE password - non-existent user
    assert ln.user_change_password(999999, "a", "b") is False

    # DELETE
    assert ln.user_delete_by_id(user.id) is True
    assert ln.user_get_by_id(user.id) is None

    # DELETE - already deleted / non-existent user
    assert ln.user_delete_by_id(user.id) is False

    print("User CRUD: OK")


def test_deck_crud():
    print("Testing Deck CRUD...")

    owner = ln.user_create("Іван", "ivan@example.com", "pass1")

    # CREATE
    deck = ln.deck_create("Basic Vocabulary", owner.id)
    assert deck is not None
    assert deck.id is not None
    assert deck.name == "Basic Vocabulary"
    assert deck.user_id == owner.id

    # READ
    fetched = ln.deck_get_by_id(deck.id)
    assert fetched is not None
    assert fetched.name == "Basic Vocabulary"

    # READ - non-existent deck
    assert ln.deck_get_by_id(999999) is None

    # UPDATE
    updated = ln.deck_update(deck.id, "Advanced Vocabulary")
    assert updated is not None
    assert updated.name == "Advanced Vocabulary"
    assert ln.deck_get_by_id(deck.id).name == "Advanced Vocabulary"

    # UPDATE - non-existent deck
    assert ln.deck_update(999999, "Ghost Deck") is None

    # DELETE
    assert ln.deck_delete_by_id(deck.id) is True
    assert ln.deck_get_by_id(deck.id) is None

    # DELETE - already deleted / non-existent deck
    assert ln.deck_delete_by_id(deck.id) is False

    print("Deck CRUD: OK")


def test_card_crud():
    print("Testing Card CRUD...")

    owner = ln.user_create("Марія", "maria@example.com", "pass2")

    # CREATE
    card = ln.card_create(
        owner.id, "apple", "яблуко", "Think of an apple pie."
    )
    assert card is not None
    assert card.id is not None
    assert card.word == "apple"
    assert card.translation == "яблуко"
    assert card.tip == "Think of an apple pie."
    assert card.user_id == owner.id

    # READ
    fetched = ln.card_get_by_id(card.id)
    assert fetched is not None
    assert fetched.word == "apple"

    # READ - non-existent card
    assert ln.card_get_by_id(999999) is None

    # UPDATE - only some fields
    updated = ln.card_update(card.id, translation="зелене яблуко")
    assert updated is not None
    assert updated.word == "apple"                    # unchanged
    assert updated.translation == "зелене яблуко"      # changed
    assert updated.tip == "Think of an apple pie."     # unchanged

    # UPDATE - non-existent card
    assert ln.card_update(999999, word="ghost") is None

    # DELETE
    assert ln.card_delete_by_id(card.id) is True
    assert ln.card_get_by_id(card.id) is None

    # DELETE - already deleted / non-existent card
    assert ln.card_delete_by_id(card.id) is False

    print("Card CRUD: OK")


def test_card_filter():
    print("Testing card_filter...")

    owner = ln.user_create("Петро", "petro@example.com", "pass3")

    card1 = ln.card_create(owner.id, "apple", "яблуко", "A common fruit.")
    card2 = ln.card_create(owner.id, "banana", "банан", "Yellow and curved.")
    card3 = ln.card_create(owner.id, "pineapple", "ананас", "Has a spiky skin.")
    card4 = ln.card_create(owner.id, "grape", "виноград", "Small and round, apple-adjacent in the fruit aisle.")

    # substring match in "word" field ("apple" appears in "apple" and "pineapple")
    results = ln.card_filter("apple")
    result_ids = {c.id for c in results}
    assert isinstance(results, tuple)
    assert card1.id in result_ids
    assert card3.id in result_ids
    assert card4.id in result_ids   # matches via the "tip" field
    assert card2.id not in result_ids

    # substring match in "translation" field
    results = ln.card_filter("банан")
    assert len(results) == 1
    assert results[0].id == card2.id

    # substring match in "tip" field
    results = ln.card_filter("spiky")
    assert len(results) == 1
    assert results[0].id == card3.id

    # case-insensitivity
    results = ln.card_filter("APPLE")
    result_ids = {c.id for c in results}
    assert card1.id in result_ids

    # no matches
    results = ln.card_filter("xyz_no_such_thing")
    assert results == ()

    print("card_filter: OK")


if __name__ == "__main__":
    test_user_crud()
    test_deck_crud()
    test_card_crud()
    test_card_filter()
    print("\nAll tests passed!")
