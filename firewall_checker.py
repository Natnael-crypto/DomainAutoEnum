from wafw00f import main as wfwf
from utils import read_subdomains_file, write_csv
from tqdm import tqdm
import logging
from tabulate import tabulate
import os

log = logging.getLogger('wafw00f')
log.setLevel(logging.CRITICAL)


def perform_firewall_check(subdomains_file, output_dir):
    """
    Perform a firewall check to detect the presence of a Web Application Firewall (WAF).

    Parameters
    ---
    :param subdomains_file: The path to the file containing a list of subdomains to check.
    :param output_dir: The directory where the results of the firewall checks will be saved. 

    Returns
    ---
    :return: None, Writes output to stdout and file
    """
    try:
        subdomains = read_subdomains_file(subdomains_file)

        if not subdomains:
            print("No subdomains found to scan.")
            return

        results = []
        table_headers=["No.", "Domain", "WAF Type", "Reason"]

        for subdomain in tqdm(subdomains, desc="Checking for WAFs", unit="domain"):
            target = 'https://' + subdomain
            attacker = wfwf.WAFW00F(target=target)
            if attacker.rq is None:
                target = 'http://' + subdomain
                attacker = wfwf.WAFW00F(target=target)

                # Check again after changing to HTTP
                if attacker.rq is None:
                    print(f'[-] Site {subdomain} appears to be down. Make sure it has a web server.')
                    continue

            waf_type = ""
            reason = ""
            waf, _ = attacker.identwaf()

            if len(waf) > 0:
                waf_type = " and/or ".join(waf)
                reason = "Detected by wafw00f"
            if len(waf) == 0:
                generic_url = attacker.genericdetect()
                if generic_url:
                    waf_type = "Generic"
                    reason = attacker.knowledge["generic"]["reason"]
                    reason = reason.replace(",", "").replace('"', "'").replace("while the server header", "while the server header in")
                else:
                    waf_type = "None"
                    reason = "No changes detected between normal response and response in an attack."
            results.append([subdomain, waf_type, reason])

        # Print the results as a table
        if results:
            results = [[i + 1, result[0], result[1], result[2]] for i, result in enumerate(results)]
            table = tabulate(results, headers=table_headers, tablefmt="pretty", colalign=("left","left", "left", "left"))
            print("\nWAF Detection Results:")
            print(table)


            # Save the results to a CSV file
            output_to_file(output_dir, results, table_headers)
    except Exception as e:
        print(f'[-] An error occured while trying to check for WAFs {e}')


def output_to_file(output_dir, results, table_headers):
    waf_output_dir = "WAF_results"
    try:
        os.makedirs(waf_output_dir, exist_ok=True)

        print(f"Saving WAF detection results in {output_dir}/{waf_output_dir}")
    except Exception as e:
        print(f"An error occured when making directory: {e}")
        return

    try:
        output_file = f"{waf_output_dir}/{results[1]}_waf_detection.csv"
        write_csv(output_file, results, table_headers)
        print()
    except Exception as e:
        print(f"An error occured when writing WAF output: {e}")