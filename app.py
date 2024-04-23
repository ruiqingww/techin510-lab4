import streamlit as st
from dotenv import load_dotenv
import os

import pandas as pd

from db import Database

load_dotenv()

def split_frame(input_df, rows):
    df = [input_df.loc[i : i + rows - 1, :] for i in range(0, len(input_df), rows)]
    return df

# Create a context manager to handle database connection
with Database(os.getenv('DATABASE_URL')) as pg:
    pg.create_table()
    
    st.title('Book Searching App 📖')

    # Input for searching
    search_term = st.text_input("Search for books by title or description")
    sort_by = st.selectbox("Sort by", options=["rating", "price"], index=0)
    order = st.selectbox("Order", options=["Ascending", "Descending"], index=0)

    # Convert order to SQL-friendly format
    order_sql = "ASC" if order == "Ascending" else "DESC"

    # Button to trigger search and sort
    if st.button("Search and Sort"):
        if search_term:
            df = pd.read_sql_query(f"SELECT * FROM quotes WHERE title ILIKE '%%{search_term}%%' OR description ILIKE '%%{search_term}%%'", pg.con)
        else:
            if sort_by == "rating":
                df = pd.read_sql_query(f"SELECT * FROM quotes ORDER BY CASE rating WHEN 'Five' THEN 5 WHEN 'Four' THEN 4 WHEN 'Three' THEN 3 WHEN 'Two' THEN 2 WHEN 'One' THEN 1 END {order_sql}", pg.con)
            elif sort_by == "price":
                df = pd.read_sql_query(f"SELECT * FROM quotes ORDER BY price::numeric {order_sql}", pg.con)
    else:
        df = pd.read_sql('SELECT * FROM quotes', pg.con)

    if not df.empty:
        container = st.container()
        with container:
            if st.button("Reset"):
                df = pd.read_sql('SELECT * FROM quotes', pg.con)  # Reload the full table

        # Pagination setup below the table
        bottom_menu = st.columns(3)
        with bottom_menu[0]:
            batch_size = st.selectbox("Page Size", options=[25, 50, 100], index=0)
        with bottom_menu[1]:
            total_pages = max(1, -(-len(df) // batch_size))
            current_page = st.number_input("Page", min_value=1, max_value=total_pages, step=1, value=1)
        with bottom_menu[2]:
            st.markdown(f"Page **{current_page}** of **{total_pages}**")

        pages = split_frame(df, batch_size)

        if pages and 0 <= current_page - 1 < len(pages):
            container.dataframe(pages[current_page - 1], use_container_width=True)
        else:
            st.error("Selected page is out of range. Please choose a valid page number.")
    else:
        st.warning("No data available.")
