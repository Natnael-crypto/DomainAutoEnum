import nmap
import os
import csv
from tqdm import tqdm
from tabulate import tabulate
from utils import read_subdomains_file, write_csv

def get_description(port_info):
    service_name = port_info.get('name', 'Unknown Service')
    service_product = port_info.get('product', '')
    service_version = port_info.get('version', '')
    service_extrainfo = port_info.get('extrainfo', '')

    description = f"{service_name} {service_product} {service_version} {service_extrainfo}".strip()
    return description or "No description available"
                

def perform_nmap_scan(subdomains_file, fast, output_dir):
    """
    Perform Nmap scan on the subdomains listed in the provided file.

    Args:
        subdomains_file (str): Path to the file containing subdomains.
        fast (bool): If True, perform a fast scan.
        output_dir (str): Directory to save the scan results.

    Returns:
        None
    """
    # Initialize Nmap scanner
    scanner = nmap.PortScanner()

    # Set Nmap options
    scan_args = '-F' if fast else ''
    

    # Read the subdomains from the file
    subdomains = read_subdomains_file(subdomains_file)
    if not subdomains:
        print("No subdomains found to scan.")
        return
    
    nmap_output_dir = "nmap_results"
    try:
        os.makedirs(nmap_output_dir, exist_ok=True)
        os.chdir(nmap_output_dir)
        print(f"Saving nmap scan results in {output_dir}/{nmap_output_dir}")
    except Exception as e:
        print(f"[ERROR] when changing directory: {e}")
        return
    
    
    table_headers=["Port", "State", "Service Description"]
    for subdomain in tqdm(subdomains, desc="Scanning SubDomains", unit="domain"):
        print(f"\nScanning {subdomain}...")
        try:
            # Perform the scan
            scanner.scan(hosts=subdomain, arguments=scan_args)
            hosts = scanner.all_hosts()

            if not hosts:
                print(f"IP Not Found for subdomain {subdomain}")
                continue
            
            results = []
            for host in hosts:
                if "tcp" in scanner[host].all_protocols():
                    ports = scanner[host]["tcp"].keys()

                    if not ports:
                        print(f"No Ports Found for Host {host}")
                        continue
                    
                    # Extract port information
                    for port in ports:
                        port_info = scanner[host]['tcp'][port]
                        description = get_description(port_info)
                        state = port_info.get('state', '')
                        results.append([port, state, description])
                else:
                    print(f"No Ports Found for Host {host}")

            # Print the results as a table
            if results:
                table = tabulate(results, headers=table_headers, tablefmt="pretty", colalign=("left", "left", "left"))
                print(f"\nScan Results for {subdomain}:")
                print(table)

                # Save the results to a CSV file
                output_file = f"{subdomain}_scan.csv"
                write_csv(output_file, results, table_headers)
                print("\n\n")
            else:
                print(f"No open ports found for {subdomain}.")

        except Exception as e:
            print(f"Error scanning {subdomain}: {e}")
    
    try:
        os.chdir("..")
        # Get the current working directory
        current_dir = os.getcwd()

        # Check if the last part of the directory path is "output"
        if os.path.basename(current_dir) != "output":
            raise Exception("Not in 'output' directory")
    except Exception as e:
        print(f"[ERROR] when changing directory: {e}")
