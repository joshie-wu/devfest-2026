from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from typing import List, Dict
import csv
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


def scrape_nyc_business_regulations() -> List[Dict[str, str]]:
    """
    Scrape NYC business regulations from https://nyc-business.nyc.gov/nycbusiness/index
    
    Extracts:
    - Title from <summary> block #text attribute
    - Description from <p> tag with class "previewCarddescription"
    
    Returns:
        List of dictionaries containing scraped data
    """
    url = "https://nyc-business.nyc.gov/nycbusiness/index"
    
    try:
        # Setup Chrome driver with headless mode
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        
        # Navigate to the page
        driver.get(url)
        
        # Wait for the data container to be populated (max 10 seconds)
        wait = WebDriverWait(driver, 10)
        container_element = wait.until(
            EC.presence_of_element_located((By.ID, 'data'))
        )
        
        # Wait a bit more for content to fully load
        wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'summary')))
        
        # Parse the rendered page with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        
        # Find the target container div
        container = soup.find('div', class_='index-page-data-container')
        
        if not container:
            print("Container div not found")
            return []
        
        regulations = []
        
        # Find all summary blocks within the container
        summary_blocks = container.find_all('summary')
        
        for summary in summary_blocks:
            # Get the text from summary
            title = summary.get_text(strip=True) if summary.string else None
            
            if not title:
                continue
            
            # Find the parent container to locate the description
            parent = summary.find_parent()
            if not parent:
                continue
            
            # Look for description in the same parent or nearby
            description_tag = parent.find('p', class_='previewCarddescription')
            description = description_tag.get_text(strip=True) if description_tag else None
            
            regulations.append({
                'title': title,
                'description': description or 'N/A'
            })
        
        return regulations
    
    except Exception as e:
        print(f"Error: {e}")
        return []


def save_to_csv(regulations: List[Dict[str, str]], filename: str = "nyc_regulations.csv"):
    """
    Save scraped regulations to a CSV file
    
    Args:
        regulations: List of regulation dictionaries
        filename: Output CSV filename
    """
    if not regulations:
        print("No regulations to save")
        return
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'description']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            writer.writerows(regulations)
        
        print(f"Successfully saved {len(regulations)} regulations to {filename}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")



if __name__ == "__main__":
    print("Starting NYC Business Regulations scraper...")
    regulations = scrape_nyc_business_regulations()
    
    if regulations:
        print(f"Found {len(regulations)} regulations")
        for reg in regulations[:5]:  # Print first 5
            print(f"Title: {reg['title']}")
            print(f"Description: {reg['description'][:100]}...")
            print("---")
        
        # Save to CSV
        save_to_csv(regulations, "nyc_regulations.csv")
    else:
        print("No regulations found")
