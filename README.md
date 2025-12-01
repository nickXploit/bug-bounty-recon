# 🔰 Bug Bounty Recon Automation

[![Python](https://img.shields.io/badge/Python-3.x-blue. svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Automated reconnaissance pipeline for bug bounty hunting.

## 🛠️ Tools Pipeline

```
subfinder → assetfinder → amass → httpx → nuclei
```

## 📦 Prerequisites

Make sure you have Go installed, then install the required tools:

```bash
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/tomnomnom/assetfinder@latest
go install -v github.com/owasp-amass/amass/v4/...@master
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# Update Nuclei templates
nuclei -ut
```

## 🚀 Usage

```bash
python3 recon.py
```

Enter your target domain when prompted.

## 📁 Output Files

| File | Description |
|------|-------------|
| `target_subfinder.txt` | Subfinder subdomain results |
| `target_assetfinder.txt` | Assetfinder subdomain results |
| `target_amass.txt` | Amass subdomain results |
| `target_subs_final.txt` | All subdomains merged & deduplicated |
| `target_httpx_live.txt` | Live hosts with status codes & tech |
| `target_nuclei_targets.txt` | Clean URLs for Nuclei scanning |
| `target_nuclei_results.txt` | Vulnerability findings |
| `target_report.txt` | Summary report |

## 📸 Demo

```
============================================================
               BUG BOUNTY RECON AUTOMATION
   subfinder -> assetfinder -> amass -> httpx -> nuclei
============================================================

[*] Checking required tools...
    [OK] subfinder
    [OK] assetfinder
    [OK] amass
    [OK] httpx
    [OK] nuclei
[OK] All tools installed!

[? ] Enter target domain (e.g., example.com): target.com
[? ] Start recon?  (y/n): y

============================================================
           STARTING RECON PIPELINE
============================================================

[STEP 1/6] SUBFINDER
[STEP 2/6] ASSETFINDER
[STEP 3/6] AMASS
[STEP 4/6] HTTPX
[STEP 5/6] PREPARE TARGETS
[STEP 6/6] NUCLEI

============================================================
           RECON COMPLETE! 
============================================================
```

## ⚠️ Disclaimer

**Only use this tool on targets you have explicit authorization to test!**

Unauthorized scanning is illegal and unethical. Always:
- Get written permission before testing
- Follow the program's rules of engagement
- Report vulnerabilities responsibly

## 👨‍💻 Author

**Anil Tadvi** - Cybersecurity Professional & Red Teamer

- 🌐 Website: [aniltadvi.me](https://www.aniltadvi.me)
- 🐙 GitHub: [@nickXploit](https://github.com/nickXploit)

## 📄 License

MIT License

## ⭐ Support

If you find this tool useful, please give it a star! 

---

Made with ❤️ for the bug bounty community
