"""
KAGUYA -- ASSET Management

Summary
-------

This feature is for the handling and manipulation of
the Information System (IS) hardware, software, and
ports, protocols, and services management (PPSM).
"""

# Standard menu template
class menu:

    def __init__(self, app):

        # Establish connection to sqlite db
        app.env = app.check_env('STIG Repository Path')
        repo = asset_repo(app.env["Information System Name"])

        # Sub menu
        while True:

            # Create menu options
            options = {
                1: 'Do Something',
                5: 'Back',
            }

            # Display menu options
            print(
                "\n" + "="*28 + "[ASSET MENU]" + "="*27,
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
            if options[int(choice)] == 'Do Something':
                None
            

# Create and manage the Information System's local DoD Cyber Exchange STIG and SCAP repository
class asset_repo:

    def __init__(self, systemName):
        from modules import db_management
        self.db = db_management.asset(systemName)