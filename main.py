print("""
==================================================================
 __  __     ______     ______     __  __     __  __     ______    
/\ \/ /    /\  __ \   /\  ___\   /\ \/\ \   /\ \_\ \   /\  __ \   
\ \  _"-.  \ \  __ \  \ \ \__ \  \ \ \_\ \  \ \____ \  \ \  __ \  
 \ \_\ \_\  \ \_\ \_\  \ \_____\  \ \_____\  \/\_____\  \ \_\ \_\ 
  \/_/\/_/   \/_/\/_/   \/_____/   \/_____/   \/_____/   \/_/\/_/

==================================================================
    Automating the Management in Risk Management Framework
==================================================================
Version: 1.0
Release Date: 02 November, 2022
""")
"""
Summary
-------

Kaguya is a command line based application for automating common 
Risk Management Framework (RMF) controls and implementations. Kaguya's
primary audience is the Information System Security Manager (ISSM),
Information System Security Officer (ISSO), and other compliance 
auditors subject to NIST 800-53 and RMF compliance within the DoD
and other U.S. Government agencies.

License
-------

The project is licensed under the MIT license.
"""

# Import external libraries
from modules import system

# Import environmental variables
print("Importing environmental variables...")
app = system.environment()
app.check_env("Information System Name")
print("Complete!")

# Main menu
while True:

  # Create menu options
  options = {
    1: 'STIG Management',
    2: 'Asset Management',
    3: 'Update System Variables',
    4: 'Exit',
  }
  choice = system.menu('MAIN', options)

  # Quit program
  if options[int(choice)] == 'Exit':
    print("\nGoodbye!")
    break

  # Manage STIG content
  if options[int(choice)] == 'STIG Management':
    from modules import stig_management
    stig_management.menu(app)

  # Manage assets
  if options[int(choice)] == 'STIG Management':
    from modules import asset_management
    asset_management.menu(app)

  # Account for changes to system
  if options[int(choice)] == 'Update System Variables':
    app.update_env()