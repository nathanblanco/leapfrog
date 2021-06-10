#------------------------------------------------------------
# defines
#------------------------------------------------------------
LAPTOPRES = (1024, 768)
FULLSCREENRES = (1024, 768)

NEXT = 1
BACK = 0


OUTCOME_TIME = 1000
RESPONSE_TIME_ALLOWED = 1500

experimentname = 'Leapfrog'	
laptop = False #******** False
ntrials = 300 

n_practice_blocks = 5
    
if laptop:
    screenres = LAPTOPRES
else:
    screenres = FULLSCREENRES

# colors
white = (255, 255, 255)
grey = (175,175,175)
boxgrey = (128,128,128)
black = (0, 0, 0)
blue = (10, 10, 200)
green = (10,200,10)
red = (200, 10, 10)
oxygreen = (22,71,8)
screengreen = (173,198,156)
ltgrey = (193,193,193)
divred = (102,63,62)
purple = (150, 40, 200)
yellow = (250, 250, 0)
orange = (255, 140, 0)
