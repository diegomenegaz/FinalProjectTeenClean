# FinalProjectTeenClean
This is where I am going to be managing the scripts for this project.
I will document common Errors and how I resolved them the examples of this include
"/dev/blah-blah blah" - Maestro Error means that the motors are little bitches and overwhelmed/the last script run still have motor commands on the stack, restart the fucking pi
"Motors should be moving but arent" there is probably a controller being instanced, causing an error. remove that fucking controller call, should be fixed.
"Time out" P-Threads = solution
