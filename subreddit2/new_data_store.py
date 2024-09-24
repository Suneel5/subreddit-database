from datetime import datetime
import os
import praw
import pandas as pd
import time
import random
from dotenv import load_dotenv
from manage_database import *
from get_data import get_data_save

# Load environment variables
load_dotenv()

# Reddit API authentication
client_id = os.getenv('client_id')
client_secret = os.getenv('client_secret')
user_agent = os.getenv('user_agent')

reddit = praw.Reddit(
    client_id=client_id,
    client_secret=client_secret,
    user_agent=user_agent
)

# Print the Reddit user
print(f"Authenticated as: {reddit.user.me()}\n")


csv_file = 'posts_url/new_posts.csv'
df = pd.DataFrame(columns=['url', 'postid', 'min_date'])

df1=pd.read_csv('posts_url/links_from_redditapi.csv')
df2=pd.read_csv('posts_url/links.csv')
# Define the subreddit and categories
subreddit = reddit.subreddit('RealEstate')
categories = ['new', 'rising','hot']

def get_posts_from_category(category):
    """Fetch posts from a specific category."""
    if category == 'hot':
        return subreddit.hot(limit=1000)
    elif category == 'new':
        return subreddit.new(limit=1000)
    elif category == 'rising':
        return subreddit.rising(limit=1000)

def post_exists(post_id, df):
    """Check if a post already exists in the DataFrame based on postid."""
    return post_id in df['postid'].values

# Loop through each category and fetch posts
for category in categories:
    print(f"\nFetching posts from category: {category}")
    
    posts = get_posts_from_category(category)
    
    for post in posts:
        # Convert Unix timestamp to human-readable format
        date_posted = datetime.fromtimestamp(post.created_utc)
        post_id = post.id
        # Get only the date part
        date_only = date_posted.date()
        
        # Check if the post already exists in the CSV file
        if not post_exists(post_id, df) and not post_exists(post_id,df1) and not post_exists(post_id,df2):
            print(f"New Post - URL: {post.url}")
            
            # Create a dictionary for the new post
            new_post = {
                'url': post.url,
                'postid': post_id,
                'min_date': date_only
            }
            
            # Add new post to the DataFrame
            new_row = pd.DataFrame([new_post])
            df = pd.concat([df, new_row], ignore_index=True)
        
            # Save the updated DataFrame to the CSV file
            df.to_csv(csv_file, index=False)
            print(f"Post saved to {csv_file}.")
        else:
            print(f"Post {post_id} already exists in CSV.")

    # Add a random delay between category fetches to avoid rate limits
    delay = random.uniform(3, 7)
    print(f"\nWaiting {delay:.2f} seconds before fetching the next category...\n")
    time.sleep(delay)

print("\n Got All New categories processed.")

print("\nAdding New posts to database.")

# Step 1: Database Initialization
create_database_if_not_exists()  # Create database if not exists
connection = connect_to_db()  # Connect to the database
create_tables(connection)  # Create tables if not exist

#  get data for new all postid and save it in db
for postid in df['postid'].values:
    get_data_save(postid,connection)
    time.sleep(2)

# Close the DB connection
if connection.is_connected():
    connection.close()
    print("MySQL connection is closed")

print("All new post added to database")



