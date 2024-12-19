import subprocess

def run_sublister(domain):
    """Run Sublist3r to enumerate subdomains and save to <domain>.txt."""
    output_file = f"{domain}.txt"
    print(f"\nRunning Sublist3r for domain: {domain}")
    
    try:
        subprocess.run(
            ["sublist3r", "-d", domain, "-o", output_file],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"Subdomains saved to: {output_file}\n")
        return output_file
    except subprocess.CalledProcessError as e:
        print(f"Error running Sublist3r: {e.stderr}")
        exit(1)
