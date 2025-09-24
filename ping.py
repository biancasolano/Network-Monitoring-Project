import os 

# pings to the corresponding ip address but sends output to null interface
temp = os.system("ping -c 4 4.2.2.2 > null")

# if it succeeds temp should return 0, therefore server is reachable
if temp == 0:
	print("server reachable")
else:
	print("server not reachable")


