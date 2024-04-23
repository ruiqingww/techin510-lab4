import time
import psycopg2

class Database:
    def __init__(self, database_url) -> None:
        self.con = psycopg2.connect(database_url)
        self.cur = self.con.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.close()

    def create_table(self):
        q = """
        CREATE TABLE IF NOT EXISTS quotes (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            rating TEXT NOT NULL,
            price TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.cur.execute(q)
        self.con.commit()

    def truncate_table(self):
        q = """
        TRUNCATE TABLE quotes
        """
        self.cur.execute(q)
        self.con.commit()
    
    def insert_quote(self, quote):
        q = """
        INSERT INTO quotes (title, rating, price, description) VALUES (%s, %s, %s, %s)
        """
        self.cur.execute(q, (quote['title'], quote['rating'], quote['price'],quote['description']))
        self.con.commit()
        
    
    def search_quotes(self, search_term):
        q = """
        SELECT * FROM quotes 
        WHERE title ILIKE %s OR description ILIKE %s
        """
        search_wildcard = f'%{search_term}%'
        self.cur.execute(q, (search_wildcard, search_wildcard))
        return self.cur.fetchall()


    def get_sorted_quotes(self, sort_by, order):
        if sort_by == "rating":
            # Map words to numbers for sorting if 'rating' is based on words like 'Three', 'Two', etc.
            q = f"""
            SELECT * FROM quotes 
            ORDER BY CASE rating
                WHEN 'Five' THEN 5
                WHEN 'Four' THEN 4
                WHEN 'Three' THEN 3
                WHEN 'Two' THEN 2
                WHEN 'One' THEN 1
            END {order}
            """
        elif sort_by == "price":
            q = f"""
            SELECT * FROM quotes
            ORDER BY price::numeric {order}
            """
        self.cur.execute(q)
        return self.cur.fetchall()
