from selenium import webdriver
from selenium.webdriver.chrome.service import Service

path = r"C:\Program Files (x86)\chromedriver.exe"  # Ensure it's a raw string
service = Service(path)

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import re
import time
import random
import pandas as pd

# Function to randomly generate a User-Agent
def random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko"
    ]
    return random.choice(user_agents)

# Function to scrape individual character profiles
def scrape_character(browser, profile_id):
    url = f'https://www.personality-database.com/en-US/profile/{profile_id}'
    browser.get(url)
    time.sleep(random.uniform(2, 5))  # Random delay between requests to avoid detection

    character_data = {
        'profile_id': profile_id,
        'name': None,
        'personality_type': None,
        'show_movie': None,
        'four_letter_votes': None
    }

    try:
        page_source = browser.page_source  # Get the full page source (useful for regex and JS-heavy pages)

        # Use regex to extract character name, personality, and show/movie (fallback method)
        name_match = re.search(r'<h1 class="profile-name">(.*?)</h1>', page_source)
        personality_match = re.search(r'<div class="profile-personality">Personality Type: (.*?)</div>', page_source)
        show_match = re.search(r'<h1>(.*?)</h1>', page_source)
        votes_match = re.search(r'<label class="personality-vote-title">Four Letter</label>.*?<label class="personality-vote-count" data-hot="">(.*?) Votes</label>', page_source, re.DOTALL)

        if name_match:
            character_data['name'] = name_match.group(1).strip()
        if personality_match:
            character_data['personality_type'] = personality_match.group(1).strip()
        if show_match:
            character_data['show_movie'] = show_match.group(1).strip()
        if votes_match:
            character_data['four_letter_votes'] = votes_match.group(1).strip()

    except Exception as e:
        print(f"Error scraping profile {profile_id}: {e}")

    return character_data

# Main function to loop through profile IDs and save results
def main(start_id, end_id):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run Chrome in headless mode (no UI)
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")  # Fix for systems with low shared memory
    chrome_options.add_argument("--disable-dev-tools")  # Disable dev tools to prevent disconnection
    chrome_options.add_argument("--disable-gpu")  # Disable GPU rendering in headless mode
    chrome_options.add_argument(f'user-agent={random_user_agent()}')  # Randomize user-agent

    # Initialize WebDriver
    path = r"C:\Program Files (x86)\chromedriver.exe"  # Adjust this to your local ChromeDriver path
    service = Service(path)
    browser = webdriver.Chrome(service=service, options=chrome_options)

    results = []

    for profile_id in range(start_id, end_id + 1):
        print(f"Scraping profile ID: {profile_id}")
        character_data = scrape_character(browser, profile_id)
        
        # Print scraped data for verification
        print(character_data)  # Print the scraped data to verify it's working
        
        results.append(character_data)

        # Save every 10 profiles to avoid data loss in case of failure
        if profile_id % 10 == 0:
            pd.DataFrame(results).to_csv('character_profiles(4).csv', index=False)

    # Save the final result with all columns (including four_letter_votes)
    pd.DataFrame(results, columns=['profile_id', 'name', 'personality_type', 'show_movie', 'four_letter_votes']).to_csv('character_profiles(4).csv', index=False)
    browser.quit()
    print("Scraping completed and saved to character_profiles(4).csv")

if __name__ == '__main__':
    start_id = 6601  # Starting profile ID
    end_id = 6800   # Ending profile ID (you can increase this based on how many profiles you want to scrape)
    main(start_id, end_id)
