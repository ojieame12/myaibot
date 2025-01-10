import os
import openai  # if you want to use OpenAI for text generation
from PIL import Image, ImageDraw, ImageFont  # for creating images
import random

# 1. Set up OpenAI Key (the "secret password" for using OpenAI)
openai.api_key = os.environ.get("OPENAI_API_KEY")

def generate_tip():
    # Use your AI service to create a short tip
    # Example using OpenAI's GPT
    prompt = "Give me a short tip about using AI for coding or design."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=50
    )
    tip_text = response.choices[0].text.strip()
    return tip_text

def create_image_with_text(tip):
    # 2. Pick a random background image
    backgrounds_folder = "backgrounds"
    background_files = os.listdir(backgrounds_folder)
    random_bg = random.choice(background_files)
    bg_path = os.path.join(backgrounds_folder, random_bg)

    # 3. Open the background image
    img = Image.open(bg_path)

    # 4. Choose a random font sometimes
    fonts = ["fonts/CoolFont1.ttf", "fonts/CoolFont2.ttf", "fonts/Default.ttf"]
    chosen_font = random.choice(fonts)

    # 5. Draw text on the image
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(chosen_font, 40)  # size 40
    # Position the text in the middle
    text_x = img.width // 10
    text_y = img.height // 10
    draw.text((text_x, text_y), tip, font=font, fill=(255,255,255))

    # 6. Save the final image
    output_path = "final_image.png"
    img.save(output_path)

    return output_path

import tweepy

def post_to_twitter(tip, image_path):
    api_key = os.environ.get("TWITTER_API_KEY")
    api_secret = os.environ.get("TWITTER_API_SECRET")
    access_token = os.environ.get("TWITTER_ACCESS_TOKEN")
    access_token_secret = os.environ.get("TWITTER_ACCESS_TOKEN_SECRET")

    # Set up the tweepy authentication
    auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
    api = tweepy.API(auth)

    # Post tweet with image
    status = tip  # The text you want to go with the tweet
    api.update_status_with_media(status=status, filename=image_path)

from threads_api.src.threads import ThreadsAPI

def post_to_threads(tip, image_path):
    threads_username = os.environ.get("THREADS_USERNAME")
    threads_password = os.environ.get("THREADS_PASSWORD")

    threads_client = ThreadsAPI()
    threads_client.login(threads_username, threads_password)

    # Threads might need an upload step or direct post if the library supports it
    # This is pseudo-code because it's not official
    threads_client.post_thread(text=tip, image_path=image_path)

def main():
    # Generate the AI tip
    tip = generate_tip()

    # Create the image
    image_path = create_image_with_text(tip)

    # Post to Twitter
    post_to_twitter(tip, image_path)

    # Post to Bluesky
    post_to_bluesky(tip, image_path)

    # Post to Threads
    post_to_threads(tip, image_path)

if __name__ == "__main__":
    main()
