import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

# Function to create a database if it doesn't exist
def create_database_if_not_exists():
    try:
        user=os.getenv('user')
        password=os.getenv(password)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  #  MySQL username
            password='12345678'  #  MySQL password
        )
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS posts")
        print("Database 'posts' created or already exists.")
    except Error as e:
        print(f"Error while creating database: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Function to connect to the MySQL database
def connect_to_db():
    try:
        user=os.getenv('user')
        password=os.getenv(password)
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Replace with your MySQL username
            password='12345678',  # Replace with your MySQL password
            database='posts'
        )
        print("Successfully connected to the database")
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

# Function to create necessary tables in the database
def create_tables(connection):
    try:
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS title (
                postno INT AUTO_INCREMENT  UNIQUE,
                titleid VARCHAR(255) PRIMARY KEY,
                title TEXT,
                tag VARCHAR(255),
                description TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS comments (
                commentid INT AUTO_INCREMENT PRIMARY KEY,
                titleid VARCHAR(255),
                userid VARCHAR(255),
                comment TEXT,
                FOREIGN KEY (titleid) REFERENCES title(titleid)
            )
        ''')
        print("Tables 'title' and 'comments' created or already exist.")
    except Error as e:
        print(f"Error while creating tables: {e}")
    finally:
        cursor.close()

# Function to save title and description to the database
def save_data_to_db(connection,titleid, title, tag, description):
    try:
        cursor = connection.cursor()
        insert_title_query = '''
            INSERT INTO title (titleid,title, tag, description) 
            VALUES (%s, %s, %s, %s)
        '''
        cursor.execute(insert_title_query, (titleid,title, tag, description))
        connection.commit()
        print(f"Title '{title}' inserted with titleid: {titleid}")
        return titleid
    except Error as e:
        print(f"Error while inserting title: {e}")
        return None
    finally:
        cursor.close()

# Function to save comments to the database
def save_comments_to_db(connection, titleid,userid, comment):
    try:
        cursor = connection.cursor()
        insert_comment_query = '''
            INSERT INTO comments (titleid,userid, comment) 
            VALUES (%s, %s, %s)
        '''
        cursor.execute(insert_comment_query, (titleid,userid, comment))
        connection.commit()
        # print(f"Comment/replies inserted for titleid: {titleid}")
    except Error as e:
        print(f"Error while inserting comment: {e}")
    finally:
        cursor.close()

def post_exists_in_db(connection, titleid):
    try:
        cursor = connection.cursor()
        check_query = '''
            SELECT COUNT(*) FROM title WHERE titleid = %s
        '''
        cursor.execute(check_query, (titleid,))
        result = cursor.fetchone()[0]  # Fetch the count result
        return result > 0  # If count > 0, post exists
    except Exception as e:
        print(f"Error while checking if post exists: {e}")
        return False
    finally:
        cursor.close()