import utilities

advM = utilities.AdvancedMath()
e1 = advM.e1
e2 = advM.e2
e3 = advM.e3

T = advM.matrixMultiply(advM.inv(advM.Rot(e2, 50)), advM.Trans(e1, 5), advM.Trans(e2, 1),
                        advM.Trans(e3, 7), advM.Rot(e2, 50))


rot, pos = advM.extractData(T)
print (rot)
print (pos)


