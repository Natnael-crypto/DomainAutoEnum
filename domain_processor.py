import dns.resolver
from urllib.parse import urlparse
from tabulate import tabulate
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from collections import Counter
import textwrap
import csv

def clean_domain(domain):
    """Remove schema (http://, https://) and trailing colon if present."""
    parsed_url = urlparse(domain)
    cleaned_domain = parsed_url.netloc if parsed_url.netloc else parsed_url.path
    return cleaned_domain.rstrip(':')

def get_ip(domain):
    """Resolve IP addresses for a domain."""
    try:
        result = dns.resolver.resolve(domain, 'A')
        return [ip.to_text() for ip in result]
    except Exception:
        return ["IP Not Found"]

def check_http_status(domain):
    """Check HTTP and HTTPS status codes for a domain."""
    results = []
    protocols = ["http", "https"]

    for protocol in protocols:
        url = f"{protocol}://{domain}"
        try:
            response = requests.head(url, timeout=5)
            results.append(f"{protocol} {response.status_code}")
        except requests.RequestException:
            results.append(f"{protocol} Not Reachable")
    
    return results

def wrap_text(text, width=35):
    """Wrap text to fit within a specified width."""
    return '\n'.join(textwrap.wrap(text, width=width))

def process_domain(domain):
    """Process a single domain to get IPs and HTTP status codes."""
    cleaned_domain = clean_domain(domain)
    ips = get_ip(cleaned_domain)
    status_codes = check_http_status(cleaned_domain)
    return [wrap_text(cleaned_domain), '\n'.join(ips), ', '.join(status_codes)], ips

def write_csv(filename, data, headers):
    """Write data to a CSV file."""
    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(data)
        print(f"CSV file '{filename}' created successfully.")
    except Exception as e:
        print(f"Error writing to CSV file '{filename}': {e}")

def resolve_domains_from_file(filename):
    """Read domains from a file and process them concurrently."""
    try:
        with open(filename, 'r') as file:
            domains = [line.strip() for line in file.readlines() if line.strip()]

        domain_table = []
        all_ips = []
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_domain, domain): domain for domain in domains}
            
            # Wrap the as_completed iterator with tqdm for progress display
            for i, future in enumerate(tqdm(as_completed(futures), total=len(futures), desc="Processing Domains"), start=1):
                try:
                    domain_data, ips = future.result()
                    domain_table.append([i, *domain_data])
                    all_ips.extend(ips)  # Collect all IPs for the second table
                except Exception as e:
                    domain_table.append([i, wrap_text(futures[future]), "Error", str(e)])
        
        # Print the first table
        print(tabulate(domain_table, headers=["No.", "Domain", "IP Addresses", "Status Code"], tablefmt="pretty", colalign=("left", "left", "left", "left")))

        # Write the domain-to-IP table to CSV
        domain_csv_data = [[row[1], row[2].replace('\n', ';'), row[3]] for row in domain_table]
        write_csv("domain2ip.csv", domain_csv_data, ["Domain", "IP Addresses", "Status Code"])

        # Generate and print the second table for IP statistics
        print("\nSummary of IP Addresses:")
        ip_counter = Counter(all_ips)
        ip_table = [[i, ip, count] for i, (ip, count) in enumerate(ip_counter.items(), start=1)]
        print(tabulate(ip_table, headers=["No.", "IP Address", "Number of Repetitions"], tablefmt="pretty", colalign=("left", "left", "left")))

        # Write the IP statistics to CSV
        ip_csv_data = [[row[1], row[2]] for row in ip_table]
        write_csv("ipaddress.csv", ip_csv_data, ["IP Address", "Number of Repetitions"])

    except FileNotFoundError:
        print(f"File {filename} not found.")
    except Exception as e:
        print(f"Error reading file: {e}")
