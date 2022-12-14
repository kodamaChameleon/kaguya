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
from modules import db_management

# Create STIG management menu
class menu:

    def __init__(self, app):

        # Sub menu
        while True:

            # Create menu options
            options = {
                1: 'Download STIG Content (Internet Required)',
                2: 'Export STIG Content',
                3: 'Back',
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

            # Download STIG content
            if options[int(choice)] == 'Download STIG Content (Internet Required)':
                stigDb = db_management.stig()
                repo = stig_repo()
                repo.download(stigDb)
                stigDb.con.close()
            
            # Export STIG content
            if options[int(choice)] == 'Export STIG Content':
                stigDb = db_management.stig()
                selection = stigDb.select_content()
                print(selection)
                if selection:
                    stigDb.export_content(selection)
                stigDb.con.close()

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
    def download(self, stigDb):
    
        print("\nDownloading xccdf content from https://public.cyber.mil/stigs/downloads/...")
        ptr = 0
        data = []
        for i in self.content:

            # Update completion status
            ptr = ptr + 1
            print("[" + "="*(round((ptr/len(self.content))*100)) + " "*(100 - round((ptr/len(self.content))*100)) + "]", end = "\r")

            # Check if url provided for download
            url = self.content[i]['href']
            if url:

                # Check if content needs updating
                update = stigDb.check_updates(i, self.content[i]['date'])
                if update:

                    # Download and identify extension
                    r = requests.get(url, allow_redirects=False)
                    urlExt = url.split(".")[-1].lower()
                    row = {}
                    
                    if urlExt == 'zip':
                        zipData = ZipFile(BytesIO(r.content))
                        stig_content = False
                        for file in zipData.namelist():
                            if file.split(".")[-1].lower() == 'xml' and 'xccdf' in file.lower():
                                stig_content = True
                                xccdf = zipData.open(file).read().decode('utf-8')
                                root = ET.fromstring(xccdf)

                                # Determine if SCAP or STIG content
                                if 'manual' in file.lower():
                                    fileType = 'manual'
                                elif 'benchmark' in file.lower():
                                    fileType = 'benchmark'

                                # Insert row into database
                                row = {
                                    'stigId': root.attrib['id'],
                                    'fileName': file.split("/")[-1],
                                    'zipFolder': i,
                                    'href': url,
                                    'date': self.content[i]['date'],
                                    'fileType': fileType,
                                    'fileContent': xccdf,
                                }
                                data.append(row)
                        
                        # Create entry to remember non-STIG/SCAP content
                        if stig_content == False:
                            row = {
                                'stigId': None,
                                'fileName': None,
                                'zipFolder': i,
                                'href': url,
                                'date': self.content[i]['date'],
                                'fileType': None,
                                'fileContent': None,
                            }
                            data.append(row)

                    else:
                        row = {
                            'stigId': None,
                            'fileName': None,
                            'zipFolder': i,
                            'href': url,
                            'date': self.content[i]['date'],
                            'fileType': None,
                            'fileContent': None,
                        }
                        data.append(row)

        stigDb.update_content(data)
        print("[" + "="*46 + "COMPLETE" + "="*46 + "]")

## FUNCTION: FIND BETWEEN TWO POINTS IN A STRING
## NEEDED DUE TO XML TAGS BEING CONTAINED WITHIN DESCRIPTION TEXT
def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""
# Credit for the find_between function goes to pkeech at https://github.com/pkeech/stig_parser


# Parse all components of xccdf into a dictionary file
def parse_xccdf(raw, filename):
    
    # Prep for building dictionary
    root = ET.fromstring(raw)
    nameSpace = {
        'xmlns': '{http://checklists.nist.gov/xccdf/1.1}',
        'dc': '{http://purl.org/dc/elements/1.1/}',
        'xhtml': '{http://www.w3.org/XML/1998/namespace}'
    }
    
    # Handle non-standard elements
    try:
        description = root.find(nameSpace['xmlns'] + 'description').text
    except AttributeError:
        description = None
    try:
        generator = root.find(".//*[@id='generator']").text
    except AttributeError:
        generator = None
    try:
        conventionsVersion = root.find(".//*[@id='conventionsVersion']").text
    except AttributeError:
        conventionsVersion = None
    
    # Add static data
    xccdf_dict = {
        'filename': filename,
        'benchmark': {
            'id': root.attrib['id'],
            'lang': root.attrib[nameSpace['xhtml'] + 'lang'],
        },
        'status': {
            'date': root.find(nameSpace['xmlns'] + 'status').attrib['date'],
            'result': root.find(nameSpace['xmlns'] + 'status').text,
        },
        'title': root.find(nameSpace['xmlns'] + 'title').text,
        'description': description,
        'reference': {
            'publisher': root.find(nameSpace['xmlns'] + 'reference').find(nameSpace['dc'] + 'publisher').text,
            'source': root.find(nameSpace['xmlns'] + 'reference').find(nameSpace['dc'] + 'source').text,
        },
        'release-info': root.find(".//*[@id='release-info']").text,
        'generator': generator,
        'conventionsVersion': conventionsVersion,
        'version': root.find(nameSpace['xmlns'] + 'version').text,
        'group': {}
    }
    
    # Add profile data
    for p in root.findall(nameSpace['xmlns'] + 'Profile'):
        profile = p.attrib['id']
        xccdf_dict[profile] = {
            'title': p.find(nameSpace['xmlns'] + 'title').text,
            'description': p.find(nameSpace['xmlns'] + 'description').text,
            'selected': {}
        }
        for child in p.findall(nameSpace['xmlns'] + 'select'):
            xccdf_dict[profile]['selected'][child.attrib['idref']] = child.attrib['selected']
            
    # Add group data
    for g in root.findall(nameSpace['xmlns'] + 'Group'):
        vulnId = g.attrib['id']

        # Add static content
        xccdf_dict['group'][vulnId] = {
            'title': g.find(nameSpace['xmlns'] + 'title').text,
            'description': g.find(nameSpace['xmlns'] + 'description').text,
            'rule': {},
        }

        # Add rule child elements
        for r in g.findall(nameSpace['xmlns'] + 'Rule'):
            
            # Handle exceptions
            try:
                check_content = r.find(nameSpace['xmlns'] + 'check/' + nameSpace['xmlns'] + 'check-content').text
            except AttributeError:
                check_content = None
            
            description = r.find(nameSpace['xmlns'] + 'description').text
            xccdf_dict['group'][vulnId]['rule'] = {
                'version': r.find(nameSpace['xmlns'] + 'version').text,
                'title': r.find(nameSpace['xmlns'] + 'title').text,
                'description': {
                    'VulnDiscussion': find_between(description, "<VulnDiscussion>", "</VulnDiscussion>"),
                    'FalsePositives': find_between(description, "<FalsePositives>", "</FalsePositives>"),
                    'FalseNegatives': find_between(description, "<FalseNegatives>", "</FalseNegatives>"),
                    'Documentable': find_between(description, "<Documentable>", "</Documentable>"),
                    'Mitigations': find_between(description, "<Mitigations>", "</Mitigations>"),
                    'SeverityOverrideGuidance': find_between(description, "<SeverityOverrideGuidance>", "</SeverityOverrideGuidance>"),
                    'PotentialImpacts': find_between(description, "<PotentialImpacts>", "</PotentialImpacts>"),
                    'ThirdPartyTools': find_between(description, "<ThirdPartyTools>", "</ThirdPartyTools>"),
                    'MitigationControl': find_between(description, "<MitigationControl>", "</MitigationControl>"),
                    'Responsibility': find_between(description, "<Responsibility>", "</Responsibility>"),
                    'IAControls': find_between(description, "<IAControls>", "</IAControls>"),
                },
                'reference': {},
                'legacyId': [],
                'CCI': [],
                'fixref': r.find(nameSpace['xmlns'] + 'fixtext').attrib['fixref'],
                'fixtext': r.find(nameSpace['xmlns'] + 'fixtext').text,
                'check': {
                    'ref': r.find(nameSpace['xmlns'] + 'check/' + nameSpace['xmlns'] + 'check-content-ref').attrib['href'],
                    'content': check_content,
                }
            }
            
            # Add rule id info
            for a in g.find(nameSpace['xmlns'] + 'Rule').attrib:
                xccdf_dict['group'][vulnId]['rule'][a] = g.find(nameSpace['xmlns'] + 'Rule').attrib[a]
            
            # Add reference child elements
            try:
                for child in r.find(nameSpace['xmlns'] + 'reference'):
                    xccdf_dict['group'][vulnId]['rule']['reference'][child.tag.split("}")[-1]] = child.text
            except TypeError:
                 xccdf_dict['group'][vulnId]['rule']['reference'] = None

            # Add legacy Ids and CCI
            for i in r.findall(nameSpace['xmlns'] + 'ident'):
                if i.text[:4].lower() == 'cci-':
                    xccdf_dict['group'][vulnId]['rule']['CCI'].append(i.text)
                else:
                    xccdf_dict['group'][vulnId]['rule']['legacyId'].append(i.text)
    
    return xccdf_dict