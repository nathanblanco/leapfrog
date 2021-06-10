
Leapfrog

This contains code for running and modeling the Leapfrog task, a choice task designed to
investigate exploratory decision-making, which was introduced in: 

Knox, W.B., Otto, A.R., Stone, P., & Love, B.C. (2012). 
The Nature of Belief-Directed Exploratory Choice in Human
Decision-Making. Frontiers in Psychology, 2, 398.


Included are two folders: one containing code for running the behavioral task and one
containing code for fitting computational models to the behavioral data.

-The task code folder contains code written in Python that runs the behavioral experiment. 
 The experiment is built with the PyPsyExp system (http://gureckislab.org/pypsyexp/sphinx/)
 by Todd Gureckis, which is included in the /lib folder. To run the experiment, you'll need 
 Python 2.x (python.org), NumPy (numpy.org), and PyGame (pygame.org/download.shtml). 
 See the included GUIDE.txt file for further info on the enclosed files and folders.


-The model code folder contains Python code for fitting a set of computational models to
 data from the Leapfrog task. For information about the computational models see:

   Knox, W.B., Otto, A.R., Stone, P., & Love, B.C. (2012). 
   The Nature of Belief-Directed Exploratory Choice in Human
   Decision-Making. Frontiers in Psychology, 2, 398.

   and

   Blanco, N.J., Love, B.C., Cooper, J.A., McGeary, J.E., Knopik, V.S., Maddox, W.T. (2015) 
   A Frontal Dopamine System for Reflective Exploratory Behavior. Neurobiology of Learning
   and Memory. 123, 84-91.

 Running the code to fit the models requires Python 2.x, NumPy, and SciPy (scipy.org). Code for
 fitting the Ideal Actor relies on the POMDP-Solve library (pomdp.org/code) by Anthony
 Cassandra, which is included in the /pomdp-solve-5.3 folder.


All code (not otherwise attributed above) by Ross Otto, Brad Knox, and Nate Blanco. 
Contact Nate Blanco (nathanblanco@gmail.com) with questions.


This work is published under a Creative Commons Attribution-NonCommercial license
(CC BY-NC-SA). This means you may use and modify this work for non-commercial purposes 
as long as you cite us.