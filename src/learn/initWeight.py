# -*- coding:utf-8 -*-

def main():
	NUM_PATTARNS = [3**8]*3 + [3**4, 3**5, 3**6, 3**7, 3**8] + [3**10]*2 + [3**9]
	NUM_STAGES = 60/4
	for stage in range(NUM_STAGES):
		f = open("../../wei/w"+str(stage)+".txt", "w")
		for feature in range(11):
			for pattern in range(NUM_PATTARNS[feature]):
				f.write(str(0.0)+" ")
			f.write("\n")
		f.close()

if __name__ == "__main__":
  main()
