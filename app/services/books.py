import sqlite3

DB_PATH = "library.db"


def get_books(user_id, search_term, filter_by):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.row_factory = sqlite3.Row

    # Constructing the base query string
    base_query = "SELECT books.title, books.author, sections.title AS section_name, books.id AS book_id " \
                 "FROM books JOIN sections ON books.book_section = sections.id"

    # Constructing the conditional part of the query based on the filter type
    if filter_by == 'author':
        cur.execute(f"{base_query} WHERE books.author=?", (search_term,))
    elif filter_by == 'section':
        cur.execute(f"{base_query} WHERE sections.title=?", (search_term,))
    elif filter_by == 'title':
        cur.execute(f"{base_query} WHERE books.title LIKE ?", (search_term,))
    else:
        cur.execute(base_query)

    all_books = cur.fetchall()

    cur.execute("SELECT book_id FROM user_requested_books WHERE user_id=?", (user_id,))
    requested_books = [row['book_id'] for row in cur.fetchall()]

    # Execute the query
    # cur.execute(query, (search_term,))

    # Fetching results

    # Creating list of books
    books_list = []
    for book in all_books:
        book_dict = {
            'id': book['book_id'],
            'title': book['title'],
            'author': book['author'],
            'section_name': book['section_name'],
            'requested': book['book_id'] in requested_books
        }
        books_list.append(book_dict)

    con.close()
    return books_list


def get_my_books_current(user_id):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.row_factory = sqlite3.Row
    cur.execute(
        "SELECT books.title,books.author,sections.title as section_name FROM user_books INNER JOIN books on books.id = user_books.book_id INNER JOIN sections on books.book_section = sections.id where user_books.user_id=? and returned_on is NULL",
        (user_id,))
    data = cur.fetchall()
    return data
    con.commit()
    con.close()


def get_my_books_completed(user_id):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.row_factory = sqlite3.Row
    cur.execute(
        "SELECT books.title,books.author,sections.title as section_name FROM user_books INNER JOIN books on books.id = user_books.book_id INNER JOIN sections on books.book_section = sections.id where user_books.user_id=? and returned_on is NOT NULL",
        (user_id,))
    data = cur.fetchall()
    return data
    con.commit()
    con.close()


def get_books_by_section(section_id):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.row_factory = sqlite3.Row
    cur.execute("SELECT id,title,author FROM books where book_section=?", (section_id,))
    data = cur.fetchall()
    con.commit()
    con.close()
    return data


def book_exists(title, section_id):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT * FROM books WHERE title=?  and book_section=?", (title, section_id))
    data = cur.fetchone()
    con.close()
    return data is not None


def add_book(title, author, section_id):
    if title is None or author is None or title == '' or author == '':
        return False
    if section_id is None:
        return False
    if book_exists(title, section_id):
        return False

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("INSERT INTO books (title,author,book_section) VALUES (?,?,?)", (title, author, section_id))
    con.commit()
    con.close()
    return True


def get_section_by_title(title):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.row_factory = sqlite3.Row
    cur.execute("SELECT * FROM sections WHERE title=?", (title,))
    data = cur.fetchone()
    con.commit()
    con.close()
    return data


def add_section(title, description, date):
    if title is None or title == '':
        return False
    if description is None or description == '':
        return False
    if date is None or date == '':
        return False
    if get_section_by_title(title) is not None:
        return False
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    # auto add date
    cur.execute("INSERT INTO sections (title,description,date_created) VALUES (?,?,?)", (title, description, date))
    con.commit()
    con.close()
    return True


def get_sections():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.row_factory = sqlite3.Row
    cur.execute("SELECT * FROM sections")
    data = cur.fetchall()
    con.commit()
    con.close()
    return data


def get_all_user_issued_books(section_id):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.row_factory = sqlite3.Row
    cur.execute(
        "SELECT      user_books.id AS user_requested_book_id,returned_on,      books.id AS id,      CASE WHEN user_books.returned_on IS  NULL THEN users.name END AS user_issued_to,      sections.title AS section_name,      books.title,      books.author  FROM      books          LEFT JOIN      user_books ON books.id = user_books.book_id          LEFT JOIN      users ON users.id = user_books.user_id          JOIN      sections ON sections.id = books.book_section  WHERE      book_section = ?  ",
        (section_id,))
    data = cur.fetchall()
    con.commit()
    con.close()
    return data


def get_book_by_id(book_id):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.row_factory = sqlite3.Row
    cur.execute("SELECT * FROM books WHERE id=?", (book_id,))
    data = cur.fetchone()
    con.commit()
    con.close()
    return data


def add_user_request_entry(user_id, book_id, days_requested):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.row_factory = sqlite3.Row
    cur.execute(
        "INSERT INTO user_requested_books (user_id, book_id, requested_on,approved_on,days_requested) VALUES (?, ?, DATETIME('now'),NULL,?)",
        (user_id, book_id, days_requested))
    con.commit()
    con.close()
    return True


def no_of_requested_books_user(user_id):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.row_factory = sqlite3.Row
    cur.execute("SELECT * FROM user_requested_books WHERE user_id=?", (user_id,))
    no_requested_books = cur.fetchall()
    con.close()
    return len(no_requested_books)


def get_books_read_per_section(user_id):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.row_factory = sqlite3.Row
    cur.execute(
        "SELECT sections.title AS section_title, COUNT(user_books.book_id) AS books_read FROM user_books JOIN books ON user_books.book_id = books.id JOIN sections ON books.book_section = sections.id WHERE user_books.user_id = ? GROUP BY sections.title",
        (user_id,))
    data = cur.fetchall()
    con.close()
    return data


def get_section_distribution():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.row_factory = sqlite3.Row
    cur.execute("SELECT title, COUNT(*) AS count FROM sections GROUP BY title")
    data = cur.fetchall()
    con.close()
    return data


def return_book(user_id, book_id):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("UPDATE user_books SET returned_on = CURRENT_TIMESTAMP WHERE user_id = ? AND book_id = ?",
                (user_id, book_id))
    con.commit()
    con.close()


def get_section_by_id(section_id):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.row_factory = sqlite3.Row
    cur.execute("SELECT * FROM sections WHERE id=?", (section_id,))
    con.commit()
    data = cur.fetchone()
    con.close()
    return data


def update_section(section_id, title, description, date):
    if title is None or title == '':
        return False
    if description is None or description == '':
        return False
    if date is None or date == '':
        return False
    if section_id is None:
        return False
    if get_section_by_id(section_id) is None:
        return False

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("UPDATE sections SET title=?,description=?,date_created=? WHERE id=?",
                (title, description, date, section_id))
    con.commit()
    con.close()
    return True


def delete_all_user_book_by_book_id(book_id):
    if book_id is None:
        return False
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("DELETE FROM user_books WHERE book_id=?", (book_id,))
    con.commit()
    con.close()
    return True


def delete_all_user_requested_books_by_book_id(book_id):
    if book_id is None:
        return False
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("DELETE FROM user_requested_books WHERE book_id=?", (book_id,))
    con.commit()
    con.close()
    return True


def delete_book(book_id):
    if book_id is None:
        return False
    if get_book_by_id(book_id) is None:
        return False
    if not delete_all_user_book_by_book_id(book_id):
        return False
    if not delete_all_user_requested_books_by_book_id(book_id):
        return False
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("DELETE FROM books WHERE id=?", (book_id,))
    con.commit()
    con.close()
    return True


def delete_section(section_id):
    if section_id is None:
        return False
    if get_section_by_id(section_id) is None:
        return False
    books = get_books_by_section(section_id)
    for book in books:
        if not delete_book(book['id']):
            return False
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("DELETE FROM sections WHERE id=?", (section_id,))
    con.commit()
    con.close()
    return True


def update_book(book_id, title, author):
    if title is None or title == '':
        return False
    if author is None or author == '':
        return False
    if book_id is None:
        return False
    if get_book_by_id(book_id) is None:
        return False

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("UPDATE books SET title=?,author=? WHERE id=?", (title, author, book_id))
    con.commit()
    con.close()
    return True


def approve_request(request_id):
    if request_id is None:
        return False
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("UPDATE user_requested_books SET approved_on=DATETIME('now') WHERE id=?", (request_id,))
    con.commit()
    con.close()
    return True


def revoke_request(request_id):
    if request_id is None:
        return False
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("DELETE FROM user_requested_books WHERE id=?", (request_id,))
    con.commit()
    con.close()
    return True


def revoke_book(user_requested_id):
    if user_requested_id is None:
        return False
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("Update user_books SET returned_on=DATETIME('now') WHERE id=?", (user_requested_id,))
    con.commit()
    con.close()
    return True


def get_all_current_user_books():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.row_factory = sqlite3.Row
    cur.execute('''select
    user_books.id as id,
    b.title as book_title,
    u.name as user_issued_to,
    user_books.taken_on as date_issued,
    s.title as section_name,
    b.author as author_name,
    taken_on,
    days_requested_for,
    CAST(days_requested_for - (julianday('now') - julianday(taken_on)) AS INTEGER) AS days_remaining,
    CASE
        WHEN julianday('now') > julianday(taken_on, '+' || days_requested_for || ' days') THEN 'true'
        ELSE 'false'
        END AS is_due,
    date(taken_on, '+' || days_requested_for || ' days') AS due_on
from user_books
         join books on user_books.book_id = books.id

join books b on b.id = user_books.book_id
join users u on u.id = user_books.user_id
join sections s on s.id = b.book_section


where user_books.returned_on is NULL
    ''')
    data = cur.fetchall()
    con.close()
    return data


def get_all_requested_books():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.row_factory = sqlite3.Row
    cur.execute('''SELECT name as user_name,s.title as section_name, b.title as book_title, b.author as book_author, b.id as book_id, u.id as user_id
,user_requested_books.id as id
,user_requested_books.days_requested as days_requested
FROM user_requested_books
         join main.books b on b.id = user_requested_books.book_id
            join main.users u on u.id = user_requested_books.user_id
         join sections s on s.id = b.book_section
         where approved_on is NULL''')
    data = cur.fetchall()
    con.close()
    return data


def approve_request(request_id, is_approved):
    if request_id is None:
        return False
    con = sqlite3.connect(DB_PATH)
    if is_approved == "true":
        cur = con.cursor()
        cur.execute("UPDATE user_requested_books SET approved_on=DATETIME('now') WHERE id=?", (request_id,))
        con.commit()
        cur.execute("SELECT * FROM user_requested_books WHERE id=?", (request_id,))
        con.commit()
        data = cur.fetchone()
        cur.execute("INSERT INTO user_books (user_id, book_id, taken_on, days_requested_for) VALUES (?, ?, DATETIME('now'), ?)",
                    (data[1], data[2], data[5]))
        con.commit()
        con.close()
        return True
    elif is_approved == "false":
        cur = con.cursor()
        cur.execute("DELETE FROM user_requested_books WHERE id=?", (request_id,))
        con.commit()
        con.close()
        return True
