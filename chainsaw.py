#!/usr/bin/python3

import sqlite3
import traceback


def setup_database():
    try:
        db = sqlite3.connect("chainsaw.sqlite")

        cur = db.cursor()

        cur.execute(
            "CREATE TABLE IF NOT EXISTS Juggler(\
                Name TEXT, \
                Country TEXT, \
                NumCatches INT \
                )"
        )

        # Test if table is empty and seed it as needed
        # http://stackoverflow.com/questions/22630307/sqlite-check-if-table-is-empty
        cur.execute(
            "SELECT count(*) FROM Juggler"
        )
        # that returns a 1-tuple, have to get the first (and only) item
        lines_in_table = int(cur.fetchone()[0])

        if lines_in_table == 0:
            print("DEBUG: Seeding data")
            cur.execute(
                "INSERT INTO Juggler VALUES ('Ian Stewart', 'Canada', 94)"
            )
            cur.execute(
                "INSERT INTO Juggler VALUES ('Aaron Gregg', 'Canada', 88)"
            )
            cur.execute(
                "INSERT INTO Juggler VALUES ('Chad Taylor', 'USA', 78)"
            )
        else:
            print("DEBUG: found data, proceeding")

        db.commit()

    except sqlite3.Error as err:
        print("Rolling back changes because of error: ", err)
        traceback.print_exc()
        db.rollback()

    finally:
        print("DEBUG: Closing database...")
        db.close()


def show_menu():
    print("""
    1. Show table
    2. Add record
    3. Update record
    4. Delete record
    0. Quit
    """)


def get_choice():
    while True:
        choice = int(input("Please enter on option: "))
        if 0 <= choice <= 4:
            return choice
        else:
            print("Please enter a valid option!")


def show_table():
    try:
        db = sqlite3.connect("chainsaw.sqlite")

        cur = db.cursor()

        cur.execute(
            "SELECT * FROM Juggler"
        )

        # TODO could format this string nicely
        for row in cur:
            print(row)

    except sqlite3.Error as err:
        print("Error reading table:", err)
        traceback.print_exc()
        # db.rollback()

    finally:
        # print("DEBUG: Closing DB")
        db.close()


def add_record():
    try:
        db = sqlite3.connect("chainsaw.sqlite")

        cur = db.cursor()

        name = input("Enter the name of the person: ")
        country = input("Enter the country of the person: ")
        catches = input("Enter the number of catches for the record:")
        catches_int = int(catches)  # TODO more robust validation

        with db:
            cur.execute(
                "INSERT INTO Juggler VALUES (?, ?, ?)",
                (name, country, catches_int)
            )

        # Using context manager
        # db.commit()

        print("DEBUG: Record added")

    except sqlite3.Error as err:
        print("Rolling back changes because of error:", err)
        traceback.print_exc()
        # db.rollback()

    finally:
        # print("DEBUG: Closing DB")
        db.close()


def update_record():
    try:
        db = sqlite3.connect("chainsaw.sqlite")

        cur = db.cursor()

        # First loop until we get a valid person
        # TODO: We should really dump back to main menu if query fails
        while True:
            name_query = input("Whose record would you like to update? ")
            # Pad with wildcards for LIKE
            substr_query = '%' + name_query + '%'

            cur.execute("SELECT * FROM Juggler "
                        "WHERE Name LIKE ?",
                        (substr_query, )
                        )

            result = cur.fetchone()
            if result is None or cur.rowcount == 0:
                print("Can't find anyone with that name...")
                continue  # prompt for name again
            else:
                found_name = str(result[0])
                found_country = str(result[1])
                found_catches = int(result[2])
                y_or_n = input("Do you mean \"" + found_name + "\"? [Y/N] ")
                if y_or_n.upper() == "N":
                    continue
                else:  # default case so we can quickly Enter through prompt
                    break

        # having selected a record, we can continue
        print(found_name + "\'s best record is currently " + str(found_catches))
        new_catches = input("Enter an updated record: ")
        new_catches_int = int(new_catches)  # TODO better input validation

        with db:
            cur.execute(
                "UPDATE Juggler "
                "SET NumCatches=? "
                "WHERE Name=?",
                (new_catches_int, found_name)
            )

        print("Record updated!")

    except sqlite3.Error as err:
        print("DB Error:")
        print(err)
    finally:
        # print("DEBUG: Closing DB")
        db.close()


def delete_record():
    try:
        db = sqlite3.connect("chainsaw.sqlite")

        cur = db.cursor()

        # First loop until we get a valid person
        # TODO: We should really dump back to main menu if query fails
        while True:
            name_query = input("Whose record would you like to delete? ")
            # Pad with wildcards for LIKE
            substr_query = '%' + name_query + '%'

            cur.execute("SELECT * FROM Juggler "
                        "WHERE Name LIKE ?",
                        (substr_query, )
                        )

            result = cur.fetchone()
            if result is None or cur.rowcount == 0:
                print("Can't find anyone with that name...")
                continue  # prompt for name again
            else:
                found_name = str(result[0])
                found_country = str(result[1])
                found_catches = int(result[2])
                y_or_n = input("Do you mean \"" + found_name + "\"? [Y/N] ")
                if y_or_n.upper() == "N":
                    continue
                else:  # default case so we can quickly Enter through prompt
                    break

        # having selected a record, we can continue
        print("Deleting " + found_name + "...")

        with db:
            cur.execute(
                "DELETE FROM Juggler "
                "WHERE Name=?",
                (found_name, )
            )
            print("Done!")

    except sqlite3.Error as err:
        print("DB Error:")
        print(err)
    finally:
        # print("DEBUG: Closing DB")
        db.close()


def main():
    setup_database()
    while True:
        show_menu()
        choice = get_choice()
        if choice == 1:
            show_table()
        elif choice == 2:
            add_record()
        elif choice == 3:
            update_record()
        elif choice == 4:
            delete_record()
        else:
            # Selected quit
            break

main()
