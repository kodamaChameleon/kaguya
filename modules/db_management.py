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
                :href,
                :date,
                :fileType,
                :fileContent
            )"""
            self.cur.execute(q, row)

        self.con.commit()
    
    # Content selector
    def select_content(self):

        search = input("Enter the full or partial name of a STIG: ")

        q = """
        SELECT stigId from xccdf_content
        WHERE stigId LIKE "%_XXX_%"
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
    
    # Export content based on stigId
    def export_content(self, stigId):

        # Fetch data
        q = """
        SELECT * FROM xccdf_content
        WHERE [stigId] = ?
        """
        row = self.cur.execute(q, [stigId]).fetchall()[0]

        # Save file
        fileName = "data/" + row[1]
        with open(fileName, 'wb') as f:
            f.write(row[5].encode('utf-8'))
        print("Saved content to " + fileName)