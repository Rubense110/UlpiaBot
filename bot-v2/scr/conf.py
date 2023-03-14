import os

# The path file is critical. Changing anything in it could cause issues.

PATH = os.path.join(os.path.abspath("."),"UlpiaBot","bot-v2")
TAGS = os.path.join(PATH,"data","00_countries.txt")
GRAPHS = os.path.join(PATH,"graphs")
CSV  = os.path.join(PATH,"data","csv")

OLD_CSV = os.path.join(CSV,"new.csv")
NEW_CSV = os.path.join(CSV,"new.csv")


