# RSL Rotrics Dexarm

Python functions and example code to control the Rotrics Dexarm.


## Demo Codes:

1. MovementScripts/fullControl.py
   - Control Robot Arm/Sliding Rail/Conveyor with keyboard
     - Commands listed in top of file 
   - Change COM Number (Line 42)
   - Change what robot is connected to (Lines 49/50)
2. LaserScripts/simpleWordEngrave.py
   - Engraves a word on to a object in the center
   - Change COM Number (Line 18)
   - Change Word (Line 15)
3. LaserScripts/dogEngrave.py
   - Closes laser door
   - Then, engraves an actual dog, the letters dog, and underlines the word
   - Lastly, opens laser door
   - Change COM Number (Line 18)
   - Change Arduino COM Number (Laser Module -> Line 204)
4. Coaster/coasterMain.py
   - First, a coaster is picked up and dropped off, then a word ("CAR" or "DOG") is engraved, then the coaster is dropped off at a conveyor
   - Then an image is taken and coaster is sorted by word
     - "CAR" -> Sliding Rail is used to drop coaster in container
     - "DOG" -> Conveyor Belt is used to drop coaster
   - The locations of each robot action is stored in Coaster/constants.py
     - fullControl.py can be used to determine all locations 