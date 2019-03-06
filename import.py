import csv 
from db  import db 

with open('books.csv', 'r') as f:
    books = csv.reader(f)
    skip = next(books)
    for row in books:
        db.execute("""
            insert into books(isbn, title, author, pub_year) 
            values(:isbn, :title, :author, :pub_year)
            """, {'isbn': row[0], 'title': row[1], 'author': row[2], 'pub_year': row[3]})

        print("book {} inserted".format(row[1]))

    db.commit()
