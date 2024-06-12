import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
import concurrent.futures
from colorama import Fore, Style
import time

allLinks = set()

def print_warning(message):
    print(f"{Fore.RED}Warning: {message}{Style.RESET_ALL}")

def scrape_page(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        if response.headers.get('content-type') and 'application/x' in response.headers['content-type']:
            print_warning(f"Error with finding links in {url}. Please look into it manually using decryption tools or other methods.")
            return [], []

    except requests.RequestException as e:
        print_warning(f"Failed to retrieve {url}: {e}")
        return [], []

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

    forms = soup.find_all('form')
    form_actions = [urljoin(url, form.get('action')) for form in forms if form.get('action')]
    
    for link in links:
        href = link.get('href')
        if href:
            full_href = urljoin(url, href)
            parsed_href = urlparse(full_href)
            if parsed_href.scheme in ["http", "https"] and full_href not in allLinks:
                allLinks.add(full_href)
                found_links.append(full_href)

    return found_links, form_actions

def main():
    parser = argparse.ArgumentParser(description='Web scraping tool')
    parser.add_argument('-u', '--url', help='URL to scrape', required=True)
    parser.add_argument('-A', '--aggressive', type=int, default=4, help='Number of threads for aggressive scan (default: 4)')
    parser.add_argument('-s', '--save', type=str, help='File to save the results')
    parser.add_argument('-f', '--forms', action='store_true', help='Find forms on the page')
    args = parser.parse_args()

    webTarget = args.url

    if not webTarget.endswith('/'):
        webTarget += '/html'

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.aggressive) as executor:
        initial_links, initial_forms = scrape_page(webTarget)
        allLinks.update(initial_links)

        with tqdm(total=len(initial_links), desc="Scraping") as pbar:
            future_to_url = {executor.submit(scrape_page, link): link for link in initial_links}
            for future in concurrent.futures.as_completed(future_to_url):
                link = future_to_url[future]
                try:
                    found_links, form_actions = future.result()
                except Exception as exc:
                    print_warning(f"Scraping failed for {link}: {exc}")
                else:
                    pbar.update(len(found_links))
                    for new_link in found_links:
                        if new_link not in allLinks:
                            allLinks.add(new_link)
                            future_to_url[executor.submit(scrape_page, new_link)] = new_link

    output_lines = []
    print(f"\n{Fore.YELLOW}OVERALL OUTPUT:{Style.RESET_ALL}")
    for i, link in enumerate(allLinks, start=1):
        output_line = f"{Fore.GREEN}[{i}] {link}{Style.RESET_ALL}"
        print(output_line)
        time.sleep(0.1)
        output_lines.append(f"[{i}] {link}")

    if args.save:
        with open(args.save, 'w') as f:
            for line in output_lines:
                f.write(line + '\n')
        print(f"\nResults saved to {args.save}")

    if args.forms:
        print(f"\n{Fore.YELLOW}Forms found:{Style.RESET_ALL}")
        for i, form_action in enumerate(initial_forms, start=1):
            print(f"{Fore.BLUE}[{i}] {form_action}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
