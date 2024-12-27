import dns.resolver
from urllib.parse import urlparse
from tabulate import tabulate
import csv

def get_ip(domain):
    """Resolve IP addresses for a domain."""
    try:
        result = dns.resolver.resolve(domain, 'A')
        return [ip.to_text() for ip in result]
    except Exception:
        return []

def read_subdomains_file(subdomains_file):
    """Read the subdomains from the file. """
    try:
        with open(subdomains_file, 'r') as file:
            subdomains = [line.strip() for line in file.readlines() if line.strip()]

        return subdomains
    except FileNotFoundError:
        print(f"[ERROR] File not found: {subdomains_file}")
        return

def write_csv(filename, data, headers):
    """Write data to a CSV file."""
    try:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            writer.writerows(data)
        print(f"CSV file '{filename}' created successfully.")
    except Exception as e:
        print(f"[ERROR] writing to CSV file '{filename}': {e}")