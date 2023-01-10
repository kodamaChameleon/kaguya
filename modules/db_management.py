"""
KAGUYA -- Database Management

Summary
-------

This feature is for the handling and manipulation of
the SQLite features of Kaguya including but not limited
to the STIG Applicability Matrix (SAM) and Information
System database.
"""

# Import external libraries
import sqlite3

# Making the STIG/SCAP xccdf content separate for portability
class stig:

    def __init__(self):
        self.name = 'data/stig.db'
        self.con = sqlite3.connect(self.name)
        self.cur = self.con.cursor()

        self.make_table()
    
    # Create standard table
    def make_table(self):

        # Table for STIG/SCAP xccdf content only
        q = """
        CREATE TABLE IF NOT EXISTS xccdf_content(
            [stigId] TEXT PRIMARY KEY,
            [fileName] TEXT,
            [zipFolder] TEXT,
            [href] TEXT,
            [date] TEXT,
            [fileType] TEXT,
            [fileContent] BLOB
        )
        """
        self.cur.execute(q)

        self.con.commit()
    
    # Insert content into xccdf_content table
    def update_content(self, data):

        for row in data:
            q = """
            INSERT OR REPLACE INTO xccdf_content VALUES(
                :stigId,
                :fileName,
                :zipFolder,
                :href,
                :date,
                :fileType,
                :fileContent
            )"""
            self.cur.execute(q, row)

        self.con.commit()
    
    # Content selector
    def select_content(self, benchmark = True):

        search = input("Enter the full or partial name of a STIG: ")

        if benchmark:
            q = """
            SELECT stigId from xccdf_content
            WHERE [stigId] LIKE "%_XXX_%"
            AND [fileContent] IS NOT NULL
            """.replace('_XXX_',search)
        else:
            q = """
            SELECT stigId from xccdf_content
            WHERE [stigId] LIKE "%_XXX_%"
            AND [fileContent] IS NOT NULL
            AND [fileName] NOT LIKE "%benchmark%"
            """.replace('_XXX_',search)
        options = [opt for sublist in self.cur.execute(q).fetchall() for opt in sublist] + [None]

        # Display Options
        for x in range(len(options)):
            print(str(x+1) + ") " + str(options[x]))

        # Make selection
        choice = 0
        while choice not in range(1,len(options)+1):
            try:
                choice = int(input("Select an Option to continue: "))
            except:
                print("\nSelect an integer number only.")
        stigId = options[choice-1]

        return stigId

    # Check if new updates available
    def check_updates(self, zipFolder, date):
        
        # Query database for matching zipFolder
        data = {
            'zipFolder': zipFolder,
            'date': date,
        }
        q = """
        SELECT zipFolder, date FROM xccdf_content
        WHERE [zipFolder] = :zipFolder
        AND [date] = :date
        """
        results = self.cur.execute(q, data).fetchall()

        # If results are returned, then local db matches online content
        if results:
            update = False
        else:
            update = True
        
        return update
    
    # Query local database for content
    def fetch_content(self, columns = ['*'], conditions = None):

        # Build query
        if columns[0] == '*' and conditions == None:
            q = "SELECT * FROM xccdf_content"
        else:
            q = "SELECT "
            
            # Add columns
            for i in range(len(columns)):
                if i == len(columns) - 1:
                    q = q + columns[i]
                else:
                    q = q + columns[i] + ', '
            q = q + ' FROM xccdf_content'
            
            # Add conditions
            if conditions:
                first_condition = True
                for col in conditions:
                    if first_condition:
                        q = q + "\nWHERE [" + str(col) + "] = '" + str(conditions[col]) + "'"
                        first_condition = False
                    else:
                        q = q + "\nAND [" + str(col) + "] = '" + str(conditions[col]) + "'"
        rows = self.cur.execute(q).fetchall()

        return rows

# Store data on system assets
class asset:

    def __init__(self, systemName):
        self.name = 'data/' + str(systemName) + '.db'
        self.con = sqlite3.connect(self.name)
        self.cur = self.con.cursor()

        self.make_table()
    
    # Create standard table
    def make_table(self):

        # Asset table with cpe as foreign key to platform
        q = """
        CREATE TABLE IF NOT EXISTS stig_ckls(
            [file_path] TEXT PRIMARY KEY,
            [hostname] TEXT,
            [fqdn] TEXT,
            [ip] TEXT,
            [stig_id] TEXT,
            [status] TEXT,
        )
        """
        self.cur.execute(q)

        # Following CPE 2.3 specifications.
        q = """
        CREATE TABLE IF NOT EXISTS platform(
            [cpe] TEXT PRIMARY KEY,
            [part] TEXT,
            [vendor] TEXT,
            [product] TEXT,
            [version] TEXT,
            [update] TEXT,
            [edition] TEXT,
            [language] TEXT,
            [sw_edition] TEXT,
            [target_sw] TEXT,
            [target_hw] TEXT,
            [other] TEXT
        )
        """
        self.cur.execute(q)

        # Table of ports, protocols, and servicies (see https://www.iana.org)
        q = """
        CREATE TABLE IF NOT EXISTS ppsm(
            [service] TEXT,
            [port] TEXT,
            [protocol] TEXT,
            [description] TEXT,
            [assignee] TEXT,
            [contact] TEXT,
            [registration_date] TEXT,
            [modification_date] TEXT,
            [reference] TEXT,
            [notes] TEXT,
            PRIMARY KEY([port], [protocol])
        )
        """
        self.cur.execute(q)

    # Import contents of checklist files
    def import_ckl(self, ckl_dict):

        q = """
        INSERT OR REPLACE INTO assets
        VALUES(
            :filePath,
            :hostname,
            :fqdn,
            :ip,
            :stig_id,
            :status
        )"""
        self.cur.execute(q, row)

        self.con.commit()