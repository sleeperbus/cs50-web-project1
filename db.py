import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


def user_info(username):
    """
    return user info
    """
    return db.execute("select * from account where username = :username", {'username': username}).fetchone()


def is_registered_user(username, password):
    """
    check user account
    """
    user = db.execute("select * from account where username=:username and password=:password",
                      {'username': username, 'password': password}).fetchone()
    return True if user else False


def is_user(username):
    """
    check if user already exists
    """
    user = db.execute("select * from account where username = :username",
                      {'username': username}).fetchone()
    return True if user else False


def create_user(username, password):
    """
    create new user
    """
    db.execute("insert into account (username, password) values(:username, :password)",
               {'username': username, 'password': password})
    db.commit()


def find_books(keyword):
    """
    find books using keyword
    """
    keyword = '%' + keyword + '%'
    sql = "select * from books a where   a.title like :keyword"
    res = db.execute(sql, {'keyword': keyword}).fetchall()
    return res


def book_info(isbn):
    """
    return single book info
    """
    return db.execute("select * from books where isbn =:isbn", {'isbn': isbn}).fetchone()


def book_reviews(book_id):
    """
    return reviews of the book
    """
    sql = """
    select  a.book_id
            , a.review
            , a.user_id
            , b.username
    from    book_reviews a 
            , account b
    where   a.book_id = :book_id
    and     b.user_id = a.user_id
    """
    return db.execute(sql, {'book_id': book_id}).fetchall()


def add_review(isbn, username, review):
    """
    add user review to book
    """
    book_id = book_info(isbn).book_id
    user_id = user_info(username).user_id
    db.execute("insert into book_reviews(book_id, user_id, review) values(:book_id, :user_id, :review)",
               {'book_id': book_id, 'user_id': user_id, 'review': review})
    db.commit()


def delete_review(isbn, username):
    """
    delete user review
    """
    book_id = book_info(isbn).book_id
    user_id = user_info(username).user_id
    db.execute("delete book_reviews where book_id = :book_id and user_id = :user_id", {'book_id': book_id, 'user_id': user_id})
    db.commit()

