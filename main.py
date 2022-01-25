
import gemini
import sys

def run(p1: str, p2: str, observers: list):

	product = f"{p1}{p2}"
	client = gemini.PublicClient()

	try:
		while True:
			ticker = client.get_ticker(product)
			line = f"{ticker['ask']}, {ticker['volume'][p1]}, {ticker['bid']}, {ticker['volume'][p2]}\n"
			for obs in observers:
				obs(line)

	except KeyboardInterrupt as _:
		print("Syphon loop interrupted by user")

	except Exception as e:
		print("An exception occured: ", e)


if __name__ == "__main__":

	if len(sys.argv) != 4:
		print("Not enough args")
		# add help
		exit()

	outputfn, prod1, prod2 = sys.argv[1:4]

	with open(outputfn, "w") as outputfile:

		run(prod1, prod2, observers=[
			lambda x: print(x, end=""),
			outputfile.write,
		])




