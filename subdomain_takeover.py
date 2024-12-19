import json
import dns.resolver
import requests
import csv
import argparse
import re
from tqdm import tqdm

# Function to load fingerprints from JSON file
def load_fingerprints(file_path):
    """Load fingerprint definitions for subdomain takeover detection."""
    with open(file_path, "r") as file:
        return json.load(file)

# Function to resolve CNAME of a subdomain
def get_cname(domain):
    """Resolve CNAME records for a domain."""
    try:
        answers = dns.resolver.resolve(domain, "CNAME")
        return [str(record.target).rstrip('.') for record in answers]
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
        return []
    except Exception as e:
        print(f"Error resolving CNAME for {domain}: {e}")
        return []

# Function to check HTTP response
def get_http_fingerprint(domain):
    """Fetch HTTP response for a domain to check for takeover fingerprints."""
    try:
        url = f"http://{domain}"
        response = requests.get(url, timeout=5)
        return response.text, response.status_code
    except requests.RequestException:
        return "", None

# Function to check subdomain takeover
def check_subdomain_takeover(domain, fingerprints):
    """Check if a domain is vulnerable to subdomain takeover."""
    cname_records = get_cname(domain)
    http_body, http_status = get_http_fingerprint(domain)

    # Results to analyze
    results = {"domain": domain, "vulnerable": False, "service": "", "reason": ""}

    for fingerprint in fingerprints:
        # Check CNAME matches
        if cname_records and any(cname in cname_records for cname in fingerprint["cname"]):
            # Check for NXDOMAIN
            if fingerprint.get("nxdomain") and not cname_records:
                results["vulnerable"] = fingerprint["vulnerable"]
                results["service"] = fingerprint["service"]
                results["reason"] = "NXDOMAIN detected"
                return results

            # Check HTTP response fingerprint
            if fingerprint.get("fingerprint"):
                if re.search(fingerprint["fingerprint"], http_body, re.IGNORECASE):
                    results["vulnerable"] = fingerprint["vulnerable"]
                    results["service"] = fingerprint["service"]
                    results["reason"] = "HTTP fingerprint matched"
                    return results

    return results

# Function to process subdomains
def process_subdomains(subdomains_file):
    """Check all subdomains for takeover vulnerabilities."""
    fingerprints = load_fingerprints("fingerprints.json")
    
    with open(subdomains_file, "r") as file:
        subdomains = [line.strip() for line in file if line.strip()]
    
    results = []

    # Process each subdomain
    for subdomain in tqdm(subdomains, desc="Checking subdomains"):
        result = check_subdomain_takeover(subdomain, fingerprints)
        results.append(result)

    # Save results to CSV
    with open("takeover_results.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["domain", "vulnerable", "service", "reason"])
        writer.writeheader()
        writer.writerows(results)

    # Print summary
    print("\nSubdomain Takeover Check Results:")
    for result in results:
        if result['vulnerable']:
            print(f"{result['domain']} Vulnerable: {result['vulnerable']} \n Service: {result['service']} \n Reason: {result['reason']} \n")


