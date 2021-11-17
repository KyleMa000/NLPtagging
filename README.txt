The program takes in three argument. The first two are the training sets.
(WSJ_02-21.pos and WSJ_24.pos). The two training sets will be merge together as one.
The third is the testing set (WSJ_23.words).

To run my program do:
-> python Tagging.py <firstTrain> <secondTrain> <Test>

Output will be a Result.pos file 
The contain will also be printing on the screen

Using score.py gives a 93% precision
Testing on WSJ_24.words 

Handling the OOV:
Hardcode method were used for:
words ends_in_s --> .5NNS
Begin with capital --> .5NNP
consist digits -->1.0CD  
All other OOV items used constant of 1/100000 
