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

# Import environmental variables
print("Importing environmental variables...")
from modules import system
app = system.environment()
app.check_env("Information System Name")
print("Complete!")

# Main menu
while True:

  # Create menu options
  options = {
    1: 'STIG Management',
    2: 'Exit',
  }

  # Display menu options
  print(
    "\n" + "="*28 + "[MAIN MENU]" + "="*28,
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
  if options[int(choice)] == 'Exit':
    print("\nGoodbye!")
    break

  # Manage STIG content
  if options[int(choice)] == 'STIG Management':
    from modules import stig_management
    stig_management