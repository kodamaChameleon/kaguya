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
import uuid

# Create STIG management menu
class menu:

    def __init__(self, app):

        # Establish connection to sqlite db
        app.env = app.check_env('STIG Repository Path')
        repo = stig_repo(app.env['STIG Repository Path'])

        # Sub menu
        while True:

            # Create menu options
            options = {
                1: 'Download STIG Content (Internet Required)',
                2: 'Export STIG/SCAP Content',
                3: 'Create STIG Checklist',
                4: 'Back',
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
                repo.db.con.close()
                break

            # Download STIG content
            if options[int(choice)] == 'Download STIG Content (Internet Required)':
                repo.check_available()
                repo.download()
            
            # Export STIG content
            if options[int(choice)] == 'Export STIG/SCAP Content':
                selection = repo.db.select_content()
                if selection:
                    print('\n' + selection)
                    repo.export_xccdf(selection)

            # Create STIG checklist from content in stig.db
            if options[int(choice)] == 'Create STIG Checklist':
                selection = repo.db.select_content(benchmark=False)
                if selection:
                    print('\n' + selection)
                    repo.create_ckl(selection)

# Create and manage the Information System's local DoD Cyber Exchange STIG and SCAP repository
class stig_repo:

    def __init__(self, rootDir):
        from modules import db_management
        self.db = db_management.stig()
        self.url = "https://public.cyber.mil/stigs/downloads/"
        self.fileStructure = {
            'content': {
                'path': os.path.join(rootDir, 'content'),
                'authExt': [],
            },
            'stig_checklists': {
                'path': os.path.join(rootDir, 'stig_checklists'),
                'authExt': [],
            },
            'wip': {
                'path': os.path.join(rootDir, 'stig_checklists\\work-in-progress'),
                'authExt': ['ckl'],
            },
            'final': {
                'path': os.path.join(rootDir, 'stig_checklists\\final'),
                'authExt': ['ckl'],
            },
            'benchmark': {
                'path': os.path.join(rootDir, 'content\\xccdf-benchmark'),
                'authExt': ['xml'],
            },
            'manual': {
                'path': os.path.join(rootDir, 'content\\xccdf-manual'),
                'authExt': ['xml'],
            },
            'results': {
                'path': os.path.join(rootDir, 'content\\scc-results'),
                'authExt': ['xml'],
            },
            'docs': {
                'path': os.path.join(rootDir, 'documents'),
                'authExt': ['csv', 'pdf', 'doc', 'docx', 'txt', 'xlsx'],
            },
            'archive': {
                'path': os.path.join(rootDir, 'archive'),
                'authExt': [],
            },
        }

        # Build repo file structure if it does not exist
        for dir in self.fileStructure:
            if not os.path.exists(self.fileStructure[dir]['path']):
                os.mkdir(self.fileStructure[dir]['path'])

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
        
        self.content = content

    # Build a SQLite inventory of cyber.mil contents for reference
    def download(self):
    
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
                update = self.db.check_updates(i, self.content[i]['date'])
                if update:

                    # Download and identify extension
                    r = requests.get(url, allow_redirects=False)
                    urlExt = url.split(".")[-1].lower()
                    row = {}
                    
                    if urlExt == 'zip':
                        zipData = ZipFile(BytesIO(r.content))
                        stig_content = False
                        for file in zipData.namelist():
                            if file.split(".")[-1].lower() == 'xml':
                                
                                # Content wich can not be unzipped and parsed is assumed to not be STIG/SCAP content
                                try:
                                    xccdf = zipData.open(file).read().decode('utf-8')
                                    root = ET.fromstring(xccdf)

                                    # Determine if SCAP or STIG content
                                    if 'manual' in file.lower():
                                        fileType = 'manual'
                                    elif 'benchmark' in file.lower():
                                        fileType = 'benchmark'

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
                                    stig_content = True
                                except:
                                    None
                        
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

        self.db.update_content(data)
        print("[" + "="*46 + "COMPLETE" + "="*46 + "]")

    # Export xccdf content
    def export_xccdf(self, stigId):

        content = self.db.fetch_content(columns = ['fileName', 'fileContent'], conditions = {'stigId': stigId})

        # Save file to exports
        if 'benchmark' in content[0][0].lower():
            fileName = os.path.join(self.fileStructure['benchmark']['path'], content[0][0])
        else:
            fileName = os.path.join(self.fileStructure['manual']['path'], content[0][0])
        with open(fileName, 'wb') as f:
            f.write(content[0][1].encode('utf-8'))
        print("\nSaved content to " + fileName)

    # Create STIG checklist
    def create_ckl(self, stigId):

        # Fetch content from database
        content = self.db.fetch_content(columns = ['fileName', 'fileContent'], conditions = {'stigId': stigId})

        # Parse xccdf into dictionary, then convert to checklist
        xccdf_dict = parse_xccdf(content[0][0], content[0][1])
        ckl = generate_ckl(xccdf_dict)

        # Parse ckl to get filename
        ckl_dict = parse_ckl(ckl)

        # Save file to exports
        fileName = os.path.join(self.fileStructure['wip']['path'], name_ckl(ckl_dict))
        with open(fileName, 'wb') as f:
            f.write(ckl.encode('UTF-8'))
        print("\nSaved content to " + fileName)

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
def parse_xccdf(filename, raw):
    
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

# Create checklist from parsed xccdf file
def generate_ckl(xccdf_dict, host_data=None, version = '2.17'):
    
    # Set default asset information
    if host_data == None:
        host_data = {
            'ROLE': 'None',
            'ASSET_TYPE': 'Computing',
            'MARKING': 'CUI',
            'HOST_NAME': None,
            'HOST_IP': None,
            'HOST_MAC': None,
            'HOST_FQDN': None,
            'TARGET_COMMENT': None,
            'TECH_AREA': None,
            'TARGET_KEY': '4072',
            'WEB_OR_DATABASE': 'false',
            'WEB_DB_SITE': None,
            'WEB_DB_INSTANCE': None,
        }
    
    # Create xml structure
    CHECKLIST = ET.Element('CHECKLIST')
    ASSET = ET.SubElement(CHECKLIST, 'ASSET')
    
    ## GENERATE asset ELEMENTS
    for element in host_data:
        ET.SubElement(ASSET, element).text = host_data[element]
    
    # Generate STIG, ISTIG, STIG_INFO ELEMENTS
    STIGS = ET.SubElement(CHECKLIST, 'STIGS')
    ISTIG = ET.SubElement(STIGS, 'iSTIG')
    STIG_INFO = ET.SubElement(ISTIG, 'STIG_INFO')
    
    # Populate STIG_INFO
    stig_data = {
        'version': xccdf_dict['version'],
        'classification': 'UNCLASSIFIED',
        'customname': '',
        'stigid': xccdf_dict['benchmark']['id'],
        'description': xccdf_dict['description'] if xccdf_dict['description'] != None else '',
        'filename': xccdf_dict['filename'],
        'releaseinfo': xccdf_dict['release-info'],
        'title': xccdf_dict['title'],
        'uuid': str(uuid.uuid4()),
        'notice': 'terms-of-use',
        'source': xccdf_dict['reference']['source'],
    }
    for element in stig_data:
        SI_DATA = ET.SubElement(STIG_INFO, 'SI_DATA')
        ET.SubElement(SI_DATA, 'SID_NAME').text = element
        if stig_data[element]:
            ET.SubElement(SI_DATA, 'SID_DATA').text = stig_data[element]
    
    # Determine if manual or benchmark
    if 'manual' in stig_data['filename'].lower():
        manual = True
    else:
        manual = False
    
    # Populate rules
    for g in xccdf_dict['group']:
        VULN = ET.SubElement(ISTIG, 'VULN')
        
        # Handle exceptions in formating
        try:
            TargetKey = xccdf_dict['group'][g]['rule']['reference']['identifier']
        except:
            TargetKey = None
        
        # Populate STIG data
        vuln_data = {
            'Vuln_Num': g,
            'Severity': xccdf_dict['group'][g]['rule']['severity'],
            'Group_Title': xccdf_dict['group'][g]['title'],
            'Rule_ID': xccdf_dict['group'][g]['rule']['id'],
            'Rule_Ver': xccdf_dict['group'][g]['rule']['version'],
            'Rule_Title': xccdf_dict['group'][g]['rule']['title'],
            'Vuln_Discuss': xccdf_dict['group'][g]['rule']['description']['VulnDiscussion'],
            'IA_Controls': xccdf_dict['group'][g]['rule']['description']['IAControls'],
            'Check_Content': xccdf_dict['group'][g]['rule']['check']['content'],
            'Fix_Text': xccdf_dict['group'][g]['rule']['fixtext'],
            'False_Positives': xccdf_dict['group'][g]['rule']['description']['FalsePositives'],
            'False_Negatives': xccdf_dict['group'][g]['rule']['description']['FalseNegatives'],
            'Documentable': xccdf_dict['group'][g]['rule']['description']['Documentable'],
            'Mitigations': xccdf_dict['group'][g]['rule']['description']['Mitigations'],
            'Potential_Impact': xccdf_dict['group'][g]['rule']['description']['PotentialImpacts'],
            'Third_Party_Tools': xccdf_dict['group'][g]['rule']['description']['ThirdPartyTools'],
            'Mitigation_Control': xccdf_dict['group'][g]['rule']['description']['MitigationControl'],
            'Responsibility': xccdf_dict['group'][g]['rule']['description']['Responsibility'],
            'Security_Override_Guidance': xccdf_dict['group'][g]['rule']['description']['SeverityOverrideGuidance'],
            'Check_Content_Ref': 'M' if manual else xccdf_dict['group'][g]['rule']['check']['ref'],
            'Weight': xccdf_dict['group'][g]['rule']['weight'],
            'Class': 'Unclass',
            'STIGRef': xccdf_dict['title'] + " :: Version " + xccdf_dict['version'] + ", " + xccdf_dict['release-info'],
            'TargetKey': TargetKey,
            'STIG_UUID': stig_data['uuid'],
        }
            
        for v in vuln_data:
            STIG_DATA = ET.SubElement(VULN, 'STIG_DATA')
            ET.SubElement(STIG_DATA, 'VULN_ATTRIBUTE').text = v
            ET.SubElement(STIG_DATA, 'ATTRIBUTE_DATA').text = vuln_data[v]
        
        if manual:
            # Legacy IDs
            for i in xccdf_dict['group'][g]['rule']['legacyId']:
                STIG_DATA = ET.SubElement(VULN, 'STIG_DATA')
                ET.SubElement(STIG_DATA, 'VULN_ATTRIBUTE').text = 'LEGACY_ID'
                ET.SubElement(STIG_DATA, 'ATTRIBUTE_DATA').text = i

            # Add CCI
            for i in xccdf_dict['group'][g]['rule']['CCI']:
                STIG_DATA = ET.SubElement(VULN, 'STIG_DATA')
                ET.SubElement(STIG_DATA, 'VULN_ATTRIBUTE').text = 'CCI_REF'
                ET.SubElement(STIG_DATA, 'ATTRIBUTE_DATA').text = i
            
        # Add status, details, comments, severity override, and justification
        ET.SubElement(VULN, 'STATUS').text = 'Not_Reviewed'
        ET.SubElement(VULN, 'FINDING_DETAILS').text = ''
        ET.SubElement(VULN, 'COMMENTS').text = ''
        ET.SubElement(VULN, 'SEVERITY_OVERRIDE').text = ''
        ET.SubElement(VULN, 'SEVERITY_JUSTIFICATION').text = ''
    
    # Convert to checklist
    ET.indent(CHECKLIST, space = '\t', level=0)
    comment = '\n<!--DISA STIG Viewer :: ' + version + '-->\n'
    ckl = ET.tostring(CHECKLIST, encoding="UTF-8", xml_declaration=True, short_empty_elements=False)
    ckl = ckl.decode("UTF-8").split("\n",1)[0] + comment + ckl.decode("UTF-8").split("\n",1)[1]

    return ckl

# Parse ckl contents into dictionary
def parse_ckl(ckl):
    
    CHECKLIST = ET.fromstring(ckl)
    
    ckl_dict = {
        'summary': {
            'Not_Reviewed': 0,
            'NotAFinding': 0,
            'Not_Applicable': 0,
            'Open': 0,
            'Missing_Details': 0,
            'Missing_Comments': 0,
        },
        'ASSET': {},
        'STIG_INFO': {},
        'VULN': {}
    }
    
    # Parse asset info
    for a in CHECKLIST.find('ASSET'):
        ckl_dict['ASSET'][a.tag] = a.text
        
    # Parse stig info
    for i in CHECKLIST.findall('STIGS/iSTIG/STIG_INFO/SI_DATA'):
        try:
            ckl_dict['STIG_INFO'][i.find('SID_NAME').text] = i.find('SID_DATA').text
        except AttributeError:
            ckl_dict['STIG_INFO'][i.find('SID_NAME').text] = None
            
    # Parse vuln info
    for v in CHECKLIST.findall('STIGS/iSTIG/VULN'):
        
        # Create new dictionary to parse vuln by their Vuln_Num
        vulnId = v.find('.//*[VULN_ATTRIBUTE="Vuln_Num"]/./ATTRIBUTE_DATA').text
        ckl_dict['VULN'][vulnId] = {}

        # Populate vulnId dictionary
        for child in v:
            if child.tag == 'STIG_DATA':
                
                # Skip Vuln_num since already used as key
                if child.find('VULN_ATTRIBUTE').text == 'Vuln_Num':
                    continue
                ckl_dict['VULN'][vulnId][child.find('VULN_ATTRIBUTE').text] = child.find('ATTRIBUTE_DATA').text
                
            else:
                ckl_dict['VULN'][vulnId][child.tag] = child.text
                
                # Populate summary
                if child.tag == 'STATUS':
                    ckl_dict['summary'][child.text] += 1
                elif child.tag == 'FINDING_DETAILS' and child.text == None:
                    ckl_dict['summary']['Missing_Details'] += 1
                elif child.tag == 'COMMENTS' and child.text == None:
                    ckl_dict['summary']['Missing_Comments'] += 1
                    
    return ckl_dict

# Generate a standard name based on parsed ckl
def name_ckl(ckl_dict):
    
    # Determine if a hostname was provided
    if ckl_dict['ASSET']['HOST_NAME']:
        hostname = str(ckl_dict['ASSET']['HOST_NAME'])
    else:
        hostname = 'Template'
        
    # Abbrevieate release info
    parse = ckl_dict['STIG_INFO']['releaseinfo'].split(' Benchmark Date: ')
    release = parse[0].split(' ')[-1]
    date = parse[-1].replace(' ', '-')
    version = 'v' + ckl_dict['STIG_INFO']['version'] + 'r' + release
    
    # Define components and build name
    nameComponents = [
        str(ckl_dict['ASSET']['MARKING']),
        hostname,
        str(ckl_dict['STIG_INFO']['stigid']),
        version,
        date,
    ]
    fileName = '_'.join(nameComponents)  + '.ckl'
    
    return fileName