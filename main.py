import argparse
import asyncio
import os
from sublister_runner import run_sublister
from domain_processor import resolve_domains_from_file
from subdomain_takeover import process_subdomains
from firewall_checker import perform_firewall_check
from google_dorking import perform_google_dorking
from nmap_scanner import perform_nmap_scan
from shodan_checker import perform_shodan_check

def main():
    print(r'''
.------------------------------------------------------------------------------------------.
|$$$$$$$\                                    $$\                                           |
|$$  __$$\                                   \__|                                          |
|$$ |  $$ | $$$$$$\  $$$$$$\$$$$\   $$$$$$\  $$\ $$$$$$$\                                  |
|$$ |  $$ |$$  __$$\ $$  _$$  _$$\  \____$$\ $$ |$$  __$$\                                 |
|$$ |  $$ |$$ /  $$ |$$ / $$ / $$ | $$$$$$$ |$$ |$$ |  $$ |                                |
|$$ |  $$ |$$ |  $$ |$$ | $$ | $$ |$$  __$$ |$$ |$$ |  $$ |                                |
|$$$$$$$  |\$$$$$$  |$$ | $$ | $$ |\$$$$$$$ |$$ |$$ |  $$ |                                |
|\_______/  \______/ \__| \__| \__| \_______|\__|\__|  \__|                                |
|                                                                                          |
|                                                                                          |
|                                                                                          |
| $$$$$$\              $$\                     $$$$$$$$\                                   |
|$$  __$$\             $$ |                    $$  _____|                                  |
|$$ /  $$ |$$\   $$\ $$$$$$\    $$$$$$\        $$ |      $$$$$$$\  $$\   $$\ $$$$$$\$$$$\  |
|$$$$$$$$ |$$ |  $$ |\_$$  _|  $$  __$$\       $$$$$\    $$  __$$\ $$ |  $$ |$$  _$$  _$$\ |
|$$  __$$ |$$ |  $$ |  $$ |    $$ /  $$ |      $$  __|   $$ |  $$ |$$ |  $$ |$$ / $$ / $$ ||
|$$ |  $$ |$$ |  $$ |  $$ |$$\ $$ |  $$ |      $$ |      $$ |  $$ |$$ |  $$ |$$ | $$ | $$ ||
|$$ |  $$ |\$$$$$$  |  \$$$$  |\$$$$$$  |      $$$$$$$$\ $$ |  $$ |\$$$$$$  |$$ | $$ | $$ ||
|\__|  \__| \______/    \____/  \______/       \________|\__|  \__| \______/ \__| \__| \__||
'------------------------------------------------------------------------------------------'
    ''')
    parser = argparse.ArgumentParser(
        description="A comprehensive tool for domain enumeration and security checks.",
        epilog="Example usage:\n"
               "  python3 script.py -d example.com --takeover -x --fast --shodan YOUR_API_KEY --dork\n"
               "  python3 script.py -f subdomains.txt --takeover --fast -o results\n",
        formatter_class=argparse.RawTextHelpFormatter
    )
    

    parser.add_argument('-d', '--domain', type=str, help='The target domain for enumeration and processing.')
    parser.add_argument('-o', '--output', type=str, default="output", help='Directory to save outputs (default: output).')
    parser.add_argument('-f', '--file', type=str, help='Use a file containing subdomains instead of running Sublist3r.')
    

    parser.add_argument('-x', '--firewall', action='store_true', help='Perform firewall checks on the target domain.')
    parser.add_argument('--fast', action='store_true', help='Perform fast scans in Nmap for discovered subdomains.')
    parser.add_argument('--shodan', type=str, metavar='API_KEY', help='Use Shodan API key to perform vulnerability checks.')
    parser.add_argument('-g','--dork', action='store_true', help='Perform Google dorking to search for exposed sensitive information.')
    parser.add_argument('--takeover', action='store_true', help='Perform subdomain takeover checks based on known fingerprints.')

    args = parser.parse_args()
    

    output_dir = args.output
    domain = args.domain
    subdomains_file = args.file

    os.makedirs(output_dir, exist_ok=True)
    os.chdir(output_dir)

 
    if not (domain or subdomains_file):
        print("Error: You must specify a domain (-d) or provide a subdomain file (-f).")
        parser.print_help()
        return


    if domain and not subdomains_file:
        print(f"\nPerforming Subdomain Enumeration on {domain}...")
        subdomains_file = run_sublister(domain)
    else:
        print(f"\nUsing provided subdomain file: {subdomains_file}")
    

    print("\nProcessing the discovered subdomains...")
    resolve_domains_from_file(subdomains_file)
    
    if args.takeover:
        print("\nChecking for subdomain takeover...")
        process_subdomains(subdomains_file)
    
    if args.firewall:
        print("\nPerforming firewall checks...")
        perform_firewall_check(subdomains_file, output_dir)
    
    if args.fast:
        print("\nPerforming fast Nmap scan...")
        perform_nmap_scan(subdomains_file, fast=True, output_dir=output_dir)
    
    if args.shodan:
        print("\nPerforming Shodan checks...")
        perform_shodan_check(subdomains_file, api_key=args.shodan, output_dir=output_dir)
    
    if args.dork:
        print("\nPerforming Google dorking...")
        asyncio.run(perform_google_dorking(domain, output_dir))

    print("\nAll tasks completed!")

if __name__ == "__main__":
    main()