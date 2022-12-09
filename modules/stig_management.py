"""
KAGUYA -- STIG Management

Summary
-------

This feature is for the handling and manipulation of
Security Technical Implementation Guide checklists
and related components including but not limited to 
STIG viewer, Security Compliance Checker (SCC) and 
SCAP content.

External References
-------------------

https://public.cyber.mil/

As of 03 November 2022, 92% of all STIG/SCAP
content from DoD exchange is available to the public.
The remaining 8% requires a Common Access Card (CAC)
to obtain. This application does not currently make
any attempt to download the 8% non-public files.
"""

# Import external libraries
import os
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from zipfile import ZipFile
import xml.etree.ElementTree as ET

# Create STIG management menu
class menu:

    def __init__(self, app):

        # Sub menu
        while True:

            # Create menu options
            options = {
                1: 'Download STIG Content',
                2: 'Back',
            }

            # Display menu options
            print(
                "\n" + "="*28 + "[STIG MENU]" + "="*28,
                "\nChoose from the following options:",
                *[str(k) + ") " + options[k] for k in options],
                sep = "\n",
            )

            # Choose from menu options
            while True:
                try:
                    choice = int(input("\nSelect an Option to continue: "))
                    if choice in options:
                        break
                    else:
                        print("\n" + str(choice) + " is not a valid option.")
                except:
                    print("\nSelect an integer number only.")

            ## Execute menu options
            # Quit program
            if options[int(choice)] == 'Back':
                break

            # Manage STIG content
            if options[int(choice)] == 'Download STIG Content':
                repo = stig_repo()
                repo.inventory()

# Create and manage the Information System's local DoD Cyber Exchange STIG and SCAP repository
class stig_repo:

    def __init__(self):
        self.url = "https://public.cyber.mil/stigs/downloads/"
        
        # Check that folders are created
        subDirs = [
            'data/stig_repo',
            'data/stig_repo/tools',
            'data/stig_repo/benchmarks',
            'data/stig_repo/stigs',
            'data/stig_repo/documents'
        ]
        for dir in subDirs:
            if not os.path.exists(dir):
                os.mkdir(dir)

        # Store content from cyber.mil as a class element
        self.content = self.check_available()

    # Check DoD Cyber Exchange for available downloads
    def check_available(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.text, 'html.parser')
        content = {}
        for file in soup.find_all('tr',attrs={'class':'file'}):  
            try:
                content[file.a.text.strip()] = {
                    'size': file.find('td',attrs={'class':'size_column'}).text.strip(),
                    'href': file.a['href'],
                    'date': file.find('div',attrs={'class':'av-post-date'}).text.strip(),
                }
            except:
                content[file.span.text.strip()] = {
                    'size': None,
                    'href': None,
                    'date': file.find('div',attrs={'class':'av-post-date'}).text.strip(),
                }
        
        return content

    # Build a SQLite inventory of cyber.mil contents for reference
    def inventory(self):
    
        print("\nMaking an inventory of contents at https://public.cyber.mil/stigs/downloads/...")
        ptr = 0
        for i in self.content:

            # Update completion status
            ptr = ptr + 1
            print("[" + "="*(round((ptr/len(self.content))*100)) + " "*(100 - round((ptr/len(self.content))*100)) + "]", end = "\r")

            # Check if url provided for download
            url = self.content[i]['href']
            if url:

                # Download and identify extension
                r = requests.get(url, allow_redirects=True)
                resp = r.content
                urlExt = url.split(".")[-1].lower()
                
                # Parse data into content type
                data = {
                    'content': {},
                    'extensions': {},
                    'type': 'documentation',
                }
                
                if urlExt == 'zip':
                    zipData = ZipFile(BytesIO(r.content))
                    for file in zipData.namelist():
                        ext = file.split(".")[-1].lower()
                        if ext in data['extensions']:
                            data['extensions'][ext] = data['extensions'][ext] + 1
                            data['content'][file] = {'stigId': None} 
                        else:
                            data['extensions'][ext] = 1
                            data['content'][file] = {'stigId': None} 
                else:
                    data['extensions'][urlExt] = 1
                    data['content'][url.split("/")[-1]] = {'stigId': None} 
                    
                # Create comma separate list of names using lowercase for case insensitivty
                names = ','.join(data['content']).lower()

                # Categorize content types
                if any(x in data['extensions'] for x in ['exe', 'rpm', 'deb', 'scc', 'msi', 'gz', 'jar']):
                    data['type'] = 'tool'
                elif 'xml' in data['extensions']:
                    if 'benchmark' in names:
                        data['type'] = 'scap_content'
                    elif 'manual' in names:
                        data['type'] = 'stig_content'
                elif 'mobileconfig' in data['extensions']:
                    data['type'] = 'stig_content'
                elif 'zip' in data['extensions']:
                    if any(x in names for x in ['chef', 'powershell', 'ansible']):
                        data['type'] = 'script'
                    elif ('manual' in  names and 'stig' in names) or data['extensions']['zip'] > 15:
                        data['type'] = 'stig_content'
                elif any(x in data['extensions'] for x in ['sql', 'sh','bat']):
                    data['type'] = 'script'
                    
                # Add stig information if applicable
                for c in data['content']:
                    if c[-10:].lower() == '-xccdf.xml':
                        xccdf = zipData.open(c).read().decode('utf-8')
                        root = ET.fromstring(xccdf)
                        data['content'][c]['stigId'] = root.attrib['id']
                
                self.content[i]['date'] = data
        
        print("[" + "="*46 + "COMPLETE" + "="*46 + "]")