from scheduler import OASiS

for i in range(1,5):
  print(OASiS(i, "best_fit"))
  print(OASiS(i, "first_fit"))