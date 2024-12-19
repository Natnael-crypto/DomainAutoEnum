# DomainAutoEnum

## Overview
DomainAutoEnum is a comprehensive domain enumeration and security auditing tool. It automates tasks such as subdomain enumeration, subdomain takeover checks, firewall testing, vulnerability detection, and Google dorking. This tool is designed to streamline penetration testing and reconnaissance efforts by providing multiple functionalities in one package.

---

## Features
- **Subdomain Enumeration**: Discover subdomains of a target domain using Sublist3r.
- **Subdomain Takeover Detection**: Check for vulnerabilities based on known fingerprints.
- **Firewall Testing**: Evaluate the presence and functionality of a web application firewall (WAF).
- **Fast Nmap Scans**: Quickly identify open ports and services.
- **Shodan Integration**: Use the Shodan API for vulnerability analysis.
- **Google Dorking**: Perform advanced Google searches to find sensitive information.
- **Custom Output Directory**: Save all results in a user-specified location.
---

## Prerequisites
1. Python 3.8 or higher
2. Dependencies listed in `requirements.txt`:
    ```
    pip install -r requirements.txt
    ```
3. Sublist3r installed and configured
4. Shodan API key (optional, for Shodan checks)

---

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/Natnael-crypto/DomainAutoEnum.git
    ```
2. Navigate to the project directory:
    ```bash
    cd DomainAutoEnum
    ```
3. Install required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

---

## Usage
Run the script with the desired options:

### Basic Commands
- Perform subdomain enumeration on a target domain:
  ```bash
  python3 main.py -d example.com
  ```

- Use a pre-generated subdomain list file:
  ```bash
  python3 main.py -f subdomains.txt
  ```

### Advanced Options
| Option                | Description                                      |
|-----------------------|--------------------------------------------------|
| `-o, --output`        | Specify output directory (default: `output`).    |
| `-x, --firewall`      | Perform firewall checks.                         |
| `--fast`              | Perform fast Nmap scans.                         |
| `--shodan API_KEY`    | Perform Shodan vulnerability checks.             |
| `--dork`              | Perform Google dorking.                          |
| `--takeover`          | Check for subdomain takeover vulnerabilities.    |

### Example Commands
- Perform subdomain enumeration, fast scanning, and takeover checks:
  ```bash
  python3 main.py -d example.com --fast --takeover
  ```

- Use a file and perform Shodan checks with an API key:
  ```bash
  python3 main.py -f subdomains.txt --shodan YOUR_API_KEY
  ```

---

## Output
Results are saved in the specified output directory (`-o` option or `output` by default). The following files/directories are generated:
- **Subdomains File**: List of discovered subdomains.
- **Nmap Results**: Fast scan results.
- **Takeover Checks**: Report of vulnerable subdomains.
- **Google Dorking Results**: Sensitive data findings.

---

## Notes
- Ensure Sublist3r is installed and configured correctly.
- Use the `--shodan` option only if you have a valid API key.
- Running with the `--dork` option may send multiple queries to Google; avoid misuse.

---

