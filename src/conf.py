import os

# The path file is critical. Changing anything in it could cause issues.

PATH = os.path.join(os.path.abspath("."))

TAGS = os.path.join(PATH,"resources","00_countries.txt")
GRAPHS = os.path.join(PATH,"graphs")
CSV  = os.path.join(os.path.abspath("."),"data","csv")
ENV = os.path.join(os.path.abspath("."),"resources",".env")

OLD_CSV = os.path.join(CSV,"old.csv")
NEW_CSV = os.path.join(CSV,"new.csv")

print(GRAPHS)
