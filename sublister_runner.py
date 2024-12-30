import subprocess
import shutil

def run_sublister(domain):
    """Run Sublist3r to enumerate subdomains and save to <domain>.txt."""
    # Check if Sublist3r is installed
    if not shutil.which("sublist3r"):
        print("Error: Sublist3r is not installed or not in PATH.")
        install = input("Would you like to install Sublist3r using apt? (yes/no): ").strip().lower()
        if install in ['yes', 'y']:
            try:
                print("\nInstalling Sublist3r using apt...")
                subprocess.run(
                    ["sudo", "apt", "update"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                subprocess.run(
                    ["sudo", "apt", "install", "-y", "sublist3r"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print("Sublist3r installed successfully!")
            except subprocess.CalledProcessError as e:
                print(f"Error installing Sublist3r: {e.stderr}")
                exit(1)
        else:
            print("Sublist3r is required to continue. Exiting...")
            exit(1)

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
