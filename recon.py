#!/usr/bin/env python3
"""
Bug Bounty Recon Automation Script
Tools: subfinder -> assetfinder -> amass -> httpx -> nuclei
"""

import subprocess
import os
import sys
from datetime import datetime
from shutil import which

def banner():
    print("""
    ============================================================
                   BUG BOUNTY RECON AUTOMATION
       subfinder -> assetfinder -> amass -> httpx -> nuclei
    ============================================================
    """)

def check_tools():
    tools = ['subfinder', 'assetfinder', 'amass', 'httpx', 'nuclei']
    missing = []
    
    print("[*] Checking required tools...")
    for tool in tools:
        if which(tool) is None:
            missing.append(tool)
            print(f"    [X] {tool} - NOT FOUND")
        else:
            print(f"    [OK] {tool}")
    
    if missing:
        print(f"\n[!] Missing tools: {', '.join(missing)}")
        print("[!] Please install missing tools before running.")
        return False
    
    print("[OK] All tools installed!\n")
    return True

def create_output_dir(domain):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"recon_{domain}_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    print(f"[*] Output directory: {output_dir}\n")
    return output_dir

def run_command(command, description):
    print(f"[*] {description}...")
    print(f"    Command: {command}\n")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode != 0 and result.stderr:
            print(f"    [!] Warning: {result.stderr.strip()}")
        return True
    except Exception as e:
        print(f"    [X] Error: {str(e)}")
        return False

def count_lines(filepath):
    try:
        with open(filepath, 'r') as f:
            return sum(1 for _ in f)
    except FileNotFoundError:
        return 0

def subfinder_scan(domain, output_dir):
    output_file = os.path.join(output_dir, f"{domain}_subfinder.txt")
    command = f"subfinder -d {domain} -all -o {output_file}"
    
    success = run_command(command, "Running Subfinder")
    
    if success:
        count = count_lines(output_file)
        print(f"    [OK] Subfinder found {count} subdomains\n")
    
    return output_file

def assetfinder_scan(domain, output_dir, subfinder_file):
    assetfinder_file = os.path.join(output_dir, f"{domain}_assetfinder.txt")
    merged_file = os.path.join(output_dir, f"{domain}_subs_raw.txt")
    
    command = f"assetfinder --subs-only {domain} > {assetfinder_file}"
    success = run_command(command, "Running Assetfinder")
    
    if success:
        count = count_lines(assetfinder_file)
        print(f"    [OK] Assetfinder found {count} subdomains\n")
    
    command = f"cat {subfinder_file} {assetfinder_file} 2>/dev/null | sort -u > {merged_file}"
    run_command(command, "Merging results")
    
    count = count_lines(merged_file)
    print(f"    [OK] Combined unique subdomains: {count}\n")
    
    return merged_file

def amass_scan(domain, output_dir, raw_subs_file):
    amass_file = os.path.join(output_dir, f"{domain}_amass.txt")
    final_subs_file = os.path.join(output_dir, f"{domain}_subs_final.txt")
    
    command = f"amass enum -passive -d {domain} -o {amass_file}"
    success = run_command(command, "Running Amass (passive mode)")
    
    if success:
        count = count_lines(amass_file)
        print(f"    [OK] Amass found {count} subdomains\n")
    
    command = f"cat {raw_subs_file} {amass_file} 2>/dev/null | sort -u > {final_subs_file}"
    run_command(command, "Creating final subdomain list")
    
    count = count_lines(final_subs_file)
    print(f"    [OK] Total unique subdomains: {count}\n")
    
    return final_subs_file

def httpx_probe(domain, output_dir, subs_file):
    httpx_file = os.path.join(output_dir, f"{domain}_httpx_live.txt")
    
    command = (
        f"httpx -l {subs_file} -silent -status-code -title -tech-detect "
        f"-mc 200,301,302,403,401,500 -o {httpx_file}"
    )
    
    success = run_command(command, "Probing live hosts with httpx")
    
    if success:
        count = count_lines(httpx_file)
        print(f"    [OK] Found {count} live hosts\n")
    
    return httpx_file

def prepare_nuclei_targets(domain, output_dir, httpx_file):
    targets_file = os.path.join(output_dir, f"{domain}_nuclei_targets.txt")
    
    command = f"cut -d ' ' -f1 {httpx_file} > {targets_file}"
    run_command(command, "Extracting URLs for Nuclei")
    
    count = count_lines(targets_file)
    print(f"    [OK] Prepared {count} targets for Nuclei\n")
    
    return targets_file

def nuclei_scan(domain, output_dir, targets_file):
    nuclei_file = os.path.join(output_dir, f"{domain}_nuclei_results.txt")
    
    command = (
        f"nuclei -l {targets_file} -severity low,medium,high,critical "
        f"-o {nuclei_file} -silent"
    )
    
    success = run_command(command, "Running Nuclei vulnerability scanner")
    
    if success:
        count = count_lines(nuclei_file)
        print(f"    [OK] Nuclei found {count} potential vulnerabilities\n")
    
    return nuclei_file

def generate_report(domain, output_dir):
    report_file = os.path.join(output_dir, f"{domain}_report.txt")
    
    print("[*] Generating summary report...\n")
    
    with open(report_file, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write(f"  BUG BOUNTY RECON REPORT - {domain}\n")
        f.write(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        
        files = [
            (f"{domain}_subfinder.txt", "Subfinder Subdomains"),
            (f"{domain}_assetfinder.txt", "Assetfinder Subdomains"),
            (f"{domain}_amass.txt", "Amass Subdomains"),
            (f"{domain}_subs_final.txt", "Total Unique Subdomains"),
            (f"{domain}_httpx_live.txt", "Live Hosts"),
            (f"{domain}_nuclei_targets.txt", "Nuclei Targets"),
            (f"{domain}_nuclei_results.txt", "Vulnerabilities Found"),
        ]
        
        f.write("RESULTS SUMMARY\n")
        f.write("-" * 40 + "\n")
        
        for filename, description in files:
            filepath = os.path.join(output_dir, filename)
            count = count_lines(filepath)
            f.write(f"{description}: {count}\n")
            print(f"    {description}: {count}")
        
        f.write("\n" + "=" * 60 + "\n")
    
    print(f"\n[OK] Report saved to: {report_file}")
    return report_file

def main():
    banner()
    
    if not check_tools():
        sys.exit(1)
    
    print("-" * 60)
    domain = input("[?] Enter target domain (e.g., example.com): ").strip()
    
    if not domain:
        print("[!] Error: Domain cannot be empty!")
        sys.exit(1)
    
    domain = domain.replace("https://", "").replace("http://", "").replace("/", "")
    
    print(f"\n[*] Target: {domain}")
    print("-" * 60 + "\n")
    
    confirm = input("[?] Start recon? (y/n): ").strip().lower()
    if confirm != 'y':
        print("[!] Aborted.")
        sys.exit(0)
    
    print("\n" + "=" * 60)
    print("           STARTING RECON PIPELINE")
    print("=" * 60 + "\n")
    
    output_dir = create_output_dir(domain)
    
    print("[STEP 1/6] SUBFINDER")
    print("-" * 40)
    subfinder_file = subfinder_scan(domain, output_dir)
    
    print("[STEP 2/6] ASSETFINDER")
    print("-" * 40)
    raw_subs_file = assetfinder_scan(domain, output_dir, subfinder_file)
    
    print("[STEP 3/6] AMASS")
    print("-" * 40)
    final_subs_file = amass_scan(domain, output_dir, raw_subs_file)
    
    print("[STEP 4/6] HTTPX")
    print("-" * 40)
    httpx_file = httpx_probe(domain, output_dir, final_subs_file)
    
    print("[STEP 5/6] PREPARE TARGETS")
    print("-" * 40)
    targets_file = prepare_nuclei_targets(domain, output_dir, httpx_file)
    
    print("[STEP 6/6] NUCLEI")
    print("-" * 40)
    nuclei_file = nuclei_scan(domain, output_dir, targets_file)
    
    print("=" * 60)
    print("           GENERATING REPORT")
    print("=" * 60)
    generate_report(domain, output_dir)
    
    print("\n" + "=" * 60)
    print("           RECON COMPLETE!")
    print("=" * 60)
    print(f"\n[*] Results saved in: {output_dir}/")
    print("\n[!] Only scan targets you have permission to test!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted. Exiting...")
        sys.exit(0)
