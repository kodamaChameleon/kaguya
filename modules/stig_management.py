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
import re

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
                repo.download()

# Download files using url
def download(url: str, dest_folder: str):

    filename = url.split('/')[-1].replace(" ", "_")  # be careful with file names
    file_path = os.path.join(dest_folder, filename)

    r = requests.get(url, stream=True)
    if r.ok:
        #print("saving to", os.path.abspath(file_path))
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    else:  # HTTP status code 4XX/5XX
        print("Download failed: status code {}\n{}".format(r.status_code, r.text))

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
        self.content = self.sort_available(self.check_available())

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

    # Sort DoD Cyber Exchange content
    def sort_available(self, content):

        """
        Unfortunately, DoD Cyber Exchange does not have any obvious way of
        standardizing names to better identify types of content. So here goes
        our best effort to automate the sorting. Please advise if you feel like
        there is a discrepancy in the sorting by reporting it at
        https://github.com/kodamaChameleon/kaguya/issues with specific details.
        """

        knownToolsRegex = {
            r'STIG\sViewer\s[\d]+\.[\d]+',
            r'SCC\s[\d]+\.[\d]+\s',
            r'CCI\s[\w]+',
            r'Group Policy Objects',
            r'STIG Applicability Guide',
        }
        for file in content:
            if content[file]['href']:

                # Set pdf, txt, xlsx, docx file destinations to documents path
                ext = content[file]['href'].rsplit(".",1)[-1].lower()
                if  ext in ['pdf', 'txt', 'xlsx', 'docx'] or 'overview' in file.lower():
                    content[file]['destination'] = 'data/stig_repo/documents/'
                
                # Sort zip archives
                elif ext == 'zip':
                    
                    # Locate all benchmarks
                    if 'benchmark' in file.lower():
                        content[file]['destination'] = 'data/stig_repo/benchmarks/'
                    else:
                        
                        # Check if file name matches known pattern for tools
                        tool = False
                        for reg in knownToolsRegex:
                            if re.match(reg, file):
                                tool = True
                        
                        # Set destination
                        if tool == False:
                            content[file]['destination'] = 'data/stig_repo/stigs/'
                        elif tool == True:
                            content[file]['destination'] = 'data/stig_repo/tools/'
                            
                # Files not able to be sorted
                else:
                    content[file]['destination'] = None

            # Files not able to be sorted
            else:
                content[file]['destination'] = None
        
        return content

    # Download files
    def download(self):

        # Display content
        print("\nFILENAME" + " "*(150-len("FILENAME" )) + "SIZE" + " "*(15-len("SIZE")) + "DATE")
        totalSize = float(0)
        for i in self.content:
            if self.content[i]['destination'] and not os.path.exists(self.content[i]['destination'] + str(self.content[i]['href']).split("/")[-1]):
                print(str(i) + "."*(150-len(str(i))) + str(self.content[i]['size']) + "."*(15-len(str(self.content[i]['size']))) + str(self.content[i]['date']))

                # Add size to total
                size = None
                if self.content[i]['size'][-2:].upper() == 'KB':
                    size = float(self.content[i]['size'][:-3])/1000
                elif self.content[i]['size'][-2:].upper() == 'MB':
                    size = float(self.content[i]['size'][:-3])
                elif self.content[i]['size'][-1:].upper() == 'B':
                    size = float(self.content[i]['size'][:-2])/1000000
                totalSize = totalSize + size
        
        if totalSize > 0:
            # User prompt for download
            opt = ""
            while opt.lower() not in ['y', 'n']:
                opt = input("\nDownload all (y/n)? [" + str(round(totalSize,2)) + " MB] ")

            # Download content
            if opt.lower() == 'y':
                ptr = 0
                for i in self.content:
                    if self.content[i]['destination'] and not os.path.exists(self.content[i]['destination'] + str(self.content[i]['href']).split("/")[-1]):
                        download(self.content[i]['href'], self.content[i]['destination'])
                    
                    # Update completion status
                    ptr = ptr + 1
                    print("[" + "="*(round((ptr/len(self.content))*100)) + " "*(100 - round((ptr/len(self.content))*100)) + "]", end = "\r")
            
            print("[" + "="*46 + "COMPLETE" + "="*46 + "]")
        else:
            print("\nNo new content available.")
