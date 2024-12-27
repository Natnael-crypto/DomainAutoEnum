import shodan
import os
from tqdm import tqdm
from utils import get_ip

def perform_shodan_check(subdomains_file, api_key, output_dir="output"):
    """
    Perform Shodan vulnerability checks on subdomains listed in a file.

    Args:
        subdomains_file (str): Path to the file containing subdomains.
        api_key (str): Shodan API key.
        output_dir (str): Directory to save the Shodan check results.
    """
    try:
        # Initialize Shodan API
        api = shodan.Shodan(api_key)
        
        # File to save results
        output_file = "shodan_results.txt"
        
        results = []
        with open(subdomains_file, 'r') as file, open(output_file, 'w') as out:
            subdomains = file.read().splitlines()
            results.append(f"Shodan Results:\n\n")
            
            for subdomain in tqdm(subdomains, desc="Performing Shodan checks", unit="domain"):
                try:
                    # Resolve the domain to IPs
                    target_ips = get_ip(subdomain)
                    if not target_ips:
                        results.append(f"[{subdomain}] Could not resolve to an IP.\n\n")
                        continue

                    for target_ip in target_ips:
                        results.append(f"[{subdomain}] IP: {target_ip}\n")
                        
                        # Fetch host details
                        host = api.host(target_ip)
                        
                        results.append(f"    Organization: {host.get('org', 'n/a')}\n")
                        
                        results.append(f"    OS: {host.get('os', 'n/a')}\n")
                        
                        # Write open ports
                        results.append("    Open Ports:\n")
                        for item in host['data']:
                            results.append(f"        Port {item['port']} - {item.get('product', 'n/a')}\n")
                        
                        # Write vulnerabilities
                        vulns = host.get('vulns', [])
                        if vulns:
                            results.append("    Vulnerabilities:\n")
                            for vuln in vulns:
                                results.append(f"        {vuln}\n")
                        else:
                            results.append("    No known vulnerabilities.\n")
                        
                        results.append("\n")
                except shodan.APIError as e:
                    results.append(f"[{subdomain}] Shodan API error: {e}\n")
                except Exception as e:
                    results.append(f"[{subdomain}] General error: {e}\n")
        
            print_out = "".join(results)
            out.write(print_out)
            print(print_out)

        print(f"Shodan check completed. Results saved to {output_file}.")
    
    except Exception as e:
        print(f"Error during Shodan checks: {e}")
