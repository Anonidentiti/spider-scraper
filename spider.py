import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
import concurrent.futures
from colorama import Fore, Style

allLinks = set()

def print_warning(message):
    print(f"{Fore.RED}Warning: {message}{Style.RESET_ALL}")

def scrape_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Check if content type is application/x
        if response.headers.get('content-type') and 'application/x' in response.headers['content-type']:
            print_warning(f"Error with finding links in {url}. Please look into it manually using decryption tools or other methods.")
            return []
        
    except requests.RequestException as e:
        print_warning(f"Failed to retrieve {url}: {e}")
        return []
    
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")
    
    links = soup.find_all('a')
    js = soup.find_all('script')
    
    found_links = []
    for jss in js:
        src = jss.get('src')
        if src:
            full_src = urljoin(url, src)
            if full_src not in allLinks:
                allLinks.add(full_src)
                found_links.append(full_src)

    for link in links:
        href = link.get('href')
        if href:
            full_href = urljoin(url, href)
            parsed_href = urlparse(full_href)
            if parsed_href.scheme in ["http", "https"] and full_href not in allLinks:
                allLinks.add(full_href)
                found_links.append(full_href)
    
    return found_links

def main():
    parser = argparse.ArgumentParser(description='Web scraping tool')
    parser.add_argument('-u', '--url', help='URL to scrape', required=True)
    parser.add_argument('-A', '--aggressive', type=int, default=4, help='Number of threads for aggressive scan (default: 4)')
    args = parser.parse_args()
    
    webTarget = args.url
    
    if not webTarget.endswith('/'):
        webTarget += '/html'

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.aggressive) as executor:
        # Scrape the initial page
        initial_links = scrape_page(webTarget)
        allLinks.update(initial_links)

        # Initialize tqdm with the total number of links to scrape
        with tqdm(total=len(initial_links), desc="Scraping") as pbar:
            # Submit scraping tasks for each link found on the initial page
            future_to_url = {executor.submit(scrape_page, link): link for link in initial_links}
            # Iterate over completed tasks
            for future in concurrent.futures.as_completed(future_to_url):
                link = future_to_url[future]
                try:
                    found_links = future.result()
                except Exception as exc:
                    print_warning(f"Scraping failed for {link}: {exc}")
                else:
                    # Update progress bar
                    pbar.update(len(found_links))

                    # Submit scraping tasks for the newly found links
                    for new_link in found_links:
                        if new_link not in allLinks:
                            allLinks.add(new_link)
                            future_to_url[executor.submit(scrape_page, new_link)] = new_link

    # Print overall output with numbers
    print("\nOverall Output:")
    for i, link in enumerate(allLinks, start=1):
        print(f"{Fore.GREEN}[{i}] {link}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()