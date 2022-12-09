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

# Making the STIG Applicability Matrix separate for portability
class SAM:

    def __init__(self):
        self.name = 'data/sam.db'
        self.con = sqlite3.connect(self.name)
        self.cur = self.con.cursor()

        self.make_table()
    
    # Create standard table
    def make_table(self):

        # Table for STIG/SCAP xccdf content only
        q = """
        CREATE TABLE IF NOT EXISTS xccdf(
            [stigId] TEXT PRIMARY KEY,
            [fileName] TEXT,
            [href] TEXT,
            [date] TEXT,
            [download] TEXT,
            [fileType] TEXT,
            [fileContent] BLOB
        )
        """
        self.cur.execute(q)

        # Table for all packages
        q = """
        CREATE TABLE IF NOT EXISTS packages(
            [fileName] TEXT PRIMARY KEY,
            [href] TEXT,
            [date] TEXT,
            [size] TEXT,
            [download] TEXT,
            [fileType] TEXT,
            [fileContent] BLOB
        )
        """
        self.cur.execute(q)

        self.con.commit()