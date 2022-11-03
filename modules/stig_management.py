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
"""

# Import external libraries
import os

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
                stig_repo()

# Create and manage the Information System's local DoD Cyber Exchange STIG and SCAP repository
class stig_repo:

    def __init__(self):
        
        # Check that folders are created
        subDirs = [
            'data/stig_repo',
            'data/stig_repo/tools',
            'data/stig_repo/benchmarks',
            'data/stig_repo/stigs',
        ]
        for dir in subDirs:
            if not os.path.exists(dir):
                os.mkdir(dir)
