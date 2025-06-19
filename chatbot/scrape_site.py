import os
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://cgwb.gov.in/cgwbpnm/search"

def construct_url(type=2, cat_id='', state_id='', district_id='', year_of_issue='', name_of_author='', keywords='', search='search'):
    params = {
        'type': type,
        'cat_id': cat_id,
        'state_id': state_id,
        'district_id': district_id,
        'year_of_issue': year_of_issue,
        'name_of_author': name_of_author,
        'keywords': keywords,
        'search': search
    }
    query_string = "&".join([f"{key}={value}" for key, value in params.items()])
    return f"{BASE_URL}?{query_string}"

def scrape_pdf_links(cat_id):
    url = construct_url(cat_id=cat_id)
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the category {cat_id}: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    pdf_links = []

    for link in soup.find_all('a', href=True):
        href = link['href']
        if href.endswith('.pdf'):
            pdf_links.append(href if href.startswith('http') else f"https://cgwb.gov.in{href}")

    return pdf_links

def download_pdf(pdf_url, download_folder="input_dir"):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    try:
        response = requests.get(pdf_url)
        if response.status_code == 200:
            pdf_name = os.path.join(download_folder, pdf_url.split("/")[-1])
            with open(pdf_name, "wb") as f:
                f.write(response.content)
            print(f"Downloaded: {pdf_name}")
        else:
            print(f"Failed to download {pdf_url}: {response.status_code}")
    except Exception as e:
        print(f"Error downloading {pdf_url}: {e}")

def get_all_category_ids():
    url = construct_url(cat_id='')
    response = requests.get(url)
    print("Response : " ,BASE_URL)
    if response.status_code != 200:
        print(f"Failed to retrieve the page: {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    print(soup.prettify())

    select_tag = soup.find('select', {'id': 'cat_id'})
    if not select_tag:
        print("No select tag found with id 'cat_id'.")
        return []

    category_ids = []
    for option in select_tag.find_all('option'):
        cat_id = option.get('value')
        print(f"Found category ID: {cat_id}")
        if cat_id and cat_id != '':
            category_ids.append(cat_id)

    return category_ids

def main():
    print("Fetching category IDs from the website...")
    category_ids = get_all_category_ids()
    print(category_ids)

    if not category_ids:
        print("No categories found.")
        return

    print(f"Found {len(category_ids)} category IDs.")
    all_pdfs = []

    for cat_id in category_ids:
        print(f"Scraping PDFs for category ID: {cat_id}")
        pdf_links = scrape_pdf_links(cat_id)
        print(f"  Found {len(pdf_links)} PDFs.")
        all_pdfs.extend(pdf_links)

    print(f"Total PDFs found: {len(all_pdfs)}")

    for pdf_url in all_pdfs:
        download_pdf(pdf_url)

if _name_ == "_main_":
    main()