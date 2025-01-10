# app.py
import os
from datetime import datetime
import random
from pathlib import Path
import openai
from dotenv import load_dotenv
import tweepy
from atproto import Client
import random
from PIL import Image, ImageDraw, ImageFont

# Load environment variables
load_dotenv()

# API Keys and Authentication
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_SECRET = os.getenv('TWITTER_ACCESS_SECRET')
BLUESKY_EMAIL = os.getenv('BLUESKY_EMAIL')
BLUESKY_PASSWORD = os.getenv('BLUESKY_PASSWORD')
THREADS_USERNAME = os.getenv('THREADS_USERNAME')
THREADS_PASSWORD = os.getenv('THREADS_PASSWORD')

def generate_ai_tip():
    """Generate an AI tip using OpenAI."""
    client = openai.Client(api_key=OPENAI_API_KEY)
    
    prompt = """Generate a short, useful tip about using AI tools. Focus on one of these areas:
    1. Coding with AI
    2. Designing with AI
    3. Writing better prompts
    Make it concise and practical."""
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

def create_image_with_text(text):
    """Create an image with the tip text."""
    # Get random background
    bg_folder = Path('backgrounds')
    backgrounds = list(bg_folder.glob('*.jpg'))
    background = random.choice(backgrounds)
    
    # Get random font
    font_folder = Path('fonts')
    fonts = list(font_folder.glob('*.ttf'))
    font_path = random.choice(fonts)
    
    # Open and resize background
    img = Image.open(background)
    img = img.resize((1080, 1080))
    
    # Add text
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(str(font_path), 60)
    
    # Wrap text
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        current_line.append(word)
        bbox = draw.textbbox((0, 0), ' '.join(current_line), font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if w > 900:  # Max width
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    
    # Draw text
    y = 400  # Starting Y position
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (1080 - w) / 2  # Center text
        draw.text((x, y), line, font=font, fill='white')
        y += h + 10
    
    # Save image
    output_path = 'output.jpg'
    img.save(output_path)
    return output_path

def post_to_twitter(text, image_path):
    """Post to Twitter."""
    client = tweepy.Client(
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_SECRET
    )
    
    auth = tweepy.OAuth1UserHandler(
        TWITTER_API_KEY,
        TWITTER_API_SECRET,
        TWITTER_ACCESS_TOKEN,
        TWITTER_ACCESS_SECRET
    )
    api = tweepy.API(auth)
    
    # Upload image
    media = api.media_upload(image_path)
    
    # Create tweet
    client.create_tweet(text=text, media_ids=[media.media_id])

def post_to_bluesky(text, image_path):
    """Post to Bluesky."""
    client = Client()
    client.login(BLUESKY_EMAIL, BLUESKY_PASSWORD)
    
    with open(image_path, 'rb') as f:
        img_data = f.read()
        
    # Upload image
    response = client.com.atproto.repo.upload_blob(img_data)
    
    # Create post
    client.com.atproto.repo.create_record({
        'repo': client.me.did,
        'collection': 'app.bsky.feed.post',
        'record': {
            'text': text,
            'createdAt': datetime.now().isoformat(),
            'embed': {
                '$type': 'app.bsky.embed.images',
                'images': [{
                    'alt': 'AI Tip Image',
                    'image': response.blob
                }]
            }
        }
    })

def main():
    """Main function to run the bot."""
    # Generate tip
    tip = generate_ai_tip()
    
    # Create image
    image_path = create_image_with_text(tip)
    
    # Post to platforms
    try:
        post_to_twitter(tip, image_path)
        print("Posted to Twitter!")
    except Exception as e:
        print(f"Error posting to Twitter: {e}")
        
    try:
        post_to_bluesky(tip, image_path)
        print("Posted to Bluesky!")
    except Exception as e:
        print(f"Error posting to Bluesky: {e}")
    
    # Clean up
    os.remove(image_path)

if __name__ == "__main__":
    main()