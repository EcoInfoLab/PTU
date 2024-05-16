# PTU
A model for estimation of heading dates using Yin et al. (1995) and Wang and Engel (1998)    
* Yin, X., Kropff, M. J., McLaren, G., & Visperas, R. M. (1995). A nonlinear model for crop development as a function of temperature. Agricultural and Forest Meteorology, 77(1-2), 1-16.
* Wang, E., & Engel, T. (1998). Simulation of phenological development of wheat crops. Agricultural systems, 58(1), 1-24.

Input file (input.txt)    
-------------
Tab separated file    
Includes sitename, year, planting dates, and measured heading dates (-99 if missing)
````
site	year	planting	heading    
X105	1999	145	216    
X105	2000	146	215    
X105	2001	141	213     
X105	2002	140	217    
````
Input file (parameter.txt)    
-------------
Tab separated file    
````
baseT	criticalT	alpha	beta	optimumP	criticalP	threshold	RmaxVeg	RmaxRep
10	36	1.5	0.5	13	16	100	1.05	1.
````
Input file (weather files)    
-------------
Use DSSAT format
