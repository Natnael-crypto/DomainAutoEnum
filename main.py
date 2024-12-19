import argparse
from sublister_runner import run_sublister
from domain_processor import resolve_domains_from_file
from subdomain_takeover import process_subdomains

def main():
    """Main script to run Sublist3r, process subdomains, and detect technologies."""
    parser = argparse.ArgumentParser(description="Run Sublist3r, process subdomains, and detect technologies.")
    parser.add_argument('domain', type=str, help='The target domain for enumeration and processing')
    args = parser.parse_args()

    print(f"\nPerforming Subdomain Enumeration on {args.domain}")
    subdomains_file = run_sublister(args.domain)
    print(f"\nSubdomains saved in {subdomains_file}")
    ## Process the subdomains
    print("\nProcessing the discovered subdomains...")
    resolve_domains_from_file(subdomains_file)
    
    print("\nTrying subdomain takeover...")
    process_subdomains(subdomains_file)


if __name__ == "__main__":
    main()
