import subprocess as cmd
import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from tqdm import tqdm
import concurrent.futures
from colorama import Fore, Style
import time
import socket

# Set to store all found links
allLinks = set()

# Function to print warning messages in red
def print_warning(message):
    print(f"{Fore.RED}Warning: {message}{Style.RESET_ALL}")

# Function to strip the protocol from a URL and return the hostname
def strip_protocol(url):
    top_level_domains = ['.com', '.org', '.net', '.io', '.ac.ke', '.to', '.me', '.edu', '.gov', '.uk', '.ca', '.au']
    hostName = url.find('://') + 3
    for domain in top_level_domains:
        domain_found = url.find(domain)
        if domain_found > 0:
            return url[hostName:domain_found + len(domain)]
    return url[hostName:]

# Function to scrape a web page and find links and forms
def scrape_page(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()
        
        # Check if the content type is not HTML
        if response.headers.get('content-type') and 'application/x' in response.headers['content-type']:
            print_warning(f"Error with finding links in {url}. Please look into it manually using decryption tools or other methods.")
            return [], []

    except requests.RequestException as e:
        print_warning(f"Failed to retrieve {url}: {e}")
        return [], []

    # Parse the HTML content
    html_content = response.text
    soup = BeautifulSoup(html_content, "html.parser")

    # Find all links and JavaScript sources
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

    # Find all forms and their actions
    forms = soup.find_all('form')
    form_actions = [urljoin(url, form.get('action')) for form in forms if form.get('action')]
    
    # Process each link found
    for link in links:
        href = link.get('href')
        if href:
            full_href = urljoin(url, href)
            parsed_href = urlparse(full_href)
            if parsed_href.scheme in ["http", "https"] and full_href not in allLinks:
                allLinks.add(full_href)
                found_links.append(full_href)

    return found_links, form_actions

def check_and_run_dnsenum(url):
    # Adjust the path to dnsenum if necessary
    dnsenum_path = "/usr/bin/dnsenum"  # Change this path if necessary
    command = [dnsenum_path, url]

    try:
        # Attempt to run dnsenum
        print(f"Running dnsenum for: {url}")
        cmd.run(command, check=True)
    except FileNotFoundError:
        print("dnsenum is not installed or not found. Installing dnsenum...")

        # Attempt to install dnsenum
        install_command = ["sudo", "apt", "update"]
        try:
            cmd.run(install_command, check=True)
            install_command = ["sudo", "apt", "install", "dnsenum", "-y"]
            cmd.run(install_command, check=True)
            print("dnsenum installed successfully. Re-running dnsenum...")
            cmd.run(command, check=True)
        except cmd.CalledProcessError as e:
            print(f"Failed to install or run dnsenum: {e}")

def main():
    # Argument parser setup
    parser = argparse.ArgumentParser(description='Web scraping tool')
    parser.add_argument('-u', '--url', help='URL to scrape')
    parser.add_argument('-A', '--aggressive', type=int, default=4, help='Number of threads for aggressive scan (default: 4)')
    parser.add_argument('-s', '--save', type=str, help='File to save the results')
    parser.add_argument('-f', '--forms', action='store_true', help='Find forms on the page')
    parser.add_argument('--find-ips', type=str, help='File containing URLs to find their IP addresses')
    parser.add_argument('--dnsenum', action='store_true', help='Perform DNS enumeration using dnsenum')
    args = parser.parse_args()

    if args.url:
        webTarget = args.url

        # Perform DNS enumeration if requested
        if args.dnsenum:
            check_and_run_dnsenum(webTarget)

        # Ensure the URL ends with a slash
        if not webTarget.endswith('/'):
            webTarget += '/html'

        # Use ThreadPoolExecutor for concurrent scraping
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.aggressive) as executor:
            initial_links, initial_forms = scrape_page(webTarget)
            allLinks.update(initial_links)

            # Progress bar setup
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

        # Print and optionally save the results
        output_lines = []
        print(f"\n{Fore.YELLOW}OVERALL OUTPUT:{Style.RESET_ALL}")
        for i, link in enumerate(allLinks, start=1):
            output_line = f"{Fore.GREEN}[{i}] {link}{Style.RESET_ALL}"
            print(output_line)
            time.sleep(0.5)
            output_lines.append(f"[{i}] {link}")

        if args.save:
            with open(args.save, 'w') as f:
                for line in output_lines:
                    f.write(line + '\n')
            print(f"\nResults saved to {args.save}")

        if args.forms:
            print(f"\n{Fore.YELLOW}Forms found:{Style.RESET_ALL}")
            for i, form_action in enumerate(initial_forms, start=1):
                print(f"{Fore.BLUE} {form_action}{Style.RESET_ALL}")

    if args.find_ips:
        print(f"\n{Fore.YELLOW}IP Addresses of Links from file {args.find_ips}:{Style.RESET_ALL}")
        with open(args.find_ips, 'r') as file:
            for i, line in enumerate(file, start=1):
                url = line.strip()
                cleaned_link = strip_protocol(url)
                try:
                    ip_address_for_url = socket.gethostbyname(cleaned_link)
                    print(f"{Fore.GREEN} {url}: {ip_address_for_url}{Style.RESET_ALL}")
                except socket.gaierror as e:
                    print(f"{Fore.RED} Error finding IP for {url}: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
