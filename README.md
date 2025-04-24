# FinalProjectTeenClean
This is where I am going to be managing the scripts for this project.
I will document common Errors and how I resolved them the examples of this include
"/dev/blah-blah blah" - Maestro Error means that the motors are little bitches and overwhelmed/the last script run still have motor commands on the stack, restart the fucking pi
"Motors should be moving but arent" there is probably a controller being instanced, causing an error. remove that fucking controller call, should be fixed.
"Time out" P-Threads = solution \n

Arm Motor Controls
Left Arm
5 - Shoulder Movement forward(Up is 6000+) or backward(Down)
6 - Horizontal Elbow Movement Out is 5500- and in is 5500+. 5500 is Resting 
7 - Elbow Vertical Movement, of course tho its fucking inverted for some reason. 8000 straightens the arm, while 1000 does a curl
8 - Wrist Curling up ward is 8000, down is 6000-
9 - literally twists the wrist left = 1000, right = 8000 whole thing turns exactly 180 from vertical to inverted vertical.
Right Arm
11 - Shoulder Fucking inverted so 3000 = Up, 6000+ = Down
12 - Elbow is not inverted but resting is now 7000
13 - Elbow on this one luckily vertically is inverted and thus can fucking curl in the right direction
14
