import requests

i = 0
dicc = {"mal":0,"bien":0}
while(i<100):
    print(i)
    try:
        requests.get("https://skanderbeg.pm/browse.php?id=0be268")
        dicc["bien"]+=1
        print("bien")
        
    except:
        dicc["mal"]+=1
        print("mal")
    finally:
        i+=1

print(dicc)