
import gemini
import sys
import os
import datetime

class DateTag:

	def __init__(self, year: int, week_number: int, week_day: int):
		self.year = year
		self.week_number = week_number
		self.week_day = week_day

	def __eq__(self, other):
		return self.year == other.year and \
			self.week_number == other.week_number and \
			self.week_day == other.week_day


class FileStreamManager:

	def __init__(self, p1: str, p2: str, check_frq: int = 3600):

		self.folder_name = f"{p1}{p2}"
		if not os.path.isdir(self.folder_name):
			os.mkdir(self.folder_name)

		self.check_frq = check_frq
		self.count = 0

		self.current_time = None
		self.current_year_folder = None
		self.current_week_folder = None
		self.current_week_day_file = None
		self.fstream = None

		now = datetime.datetime.now()
		self.current_time = DateTag(
			year=now.year,
			week_number=now.isocalendar()[1],
			week_day=now.weekday()
		)
		self.update_filename()

	def check_filename(self):
		now = datetime.datetime.now()
		date_tag = DateTag(
			year=now.year,
			week_number=now.isocalendar()[1],
			week_day=now.weekday()
		)

		if date_tag != self.current_time:
			self.current_time = date_tag
			self.update_filename()

	def update_filename(self):
		self.current_year_folder = os.path.join(self.folder_name, str(self.current_time.year))
		if not os.path.isdir(self.current_year_folder):
			os.mkdir(self.current_year_folder)

		self.current_week_folder = os.path.join(self.current_year_folder, str(self.current_time.week_number))
		if not os.path.isdir(self.current_week_folder):
			os.mkdir(self.current_week_folder)

		self.current_week_day_file = os.path.join(self.current_week_folder, str(self.current_time.week_day))
		self.fstream = open(self.current_week_day_file, "w")
		print(f"Active file name updated: {self.current_week_day_file}")

	def write_line(self, line: str):
		self.fstream.write(line)
		self.update_count()

	def update_count(self):
		self.count += 1
		if self.count >= self.check_frq:
			self.check_filename()
			self.count = 0

	def get_name(self):
		return self.current_week_day_file

	def __call__(self, *args, **kwargs):
		return self.get_name()

	def __del__(self):
		self.fstream.close()


def syphon(p1: str, p2: str, observers: list):
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

	if len(sys.argv) == 3:
		prod1, prod2 = sys.argv[1:3]

		fnmgr = FileStreamManager(prod1, prod2, 5)

		syphon(prod1, prod2, observers=[
			lambda x: print(f"[{x}]", end=""),
			fnmgr.write_line,
		])
	else:
		print("Not enough arguments")
		print(f"usage : {sys.argv[0]} P1 P2, example: {sys.argv[0]} BTC USD")

