from bs4 import BeautifulSoup as makesoup
from zipfile import ZipFile
import os
import shutil
import glob

class SOZipParser:
	
	def __init__(self, zipname):
		self.zipname = zipname
		self.dirname = zipname[0:-4]
		self.path = os.getcwd() + "/" + self.dirname

	def unzip(self):
		zp = ZipFile(self.zipname)
		zp.extractall()
		zp.close()

	def reorganize(self):
		os.chdir(self.path)
		for f in os.listdir("."):
			if "manifest" in f or "dtd" in f:
				os.remove(f)			
			if f == "pdf":
				os.chdir(f)
				shutil.move(glob.glob("*.pdf")[0], "../")
				os.chdir("../")
				shutil.rmtree(f)
		
	def make_dc(self):
		os.chdir(self.path)
		base = open(glob.glob("*.xml")[0])
		soup = makesoup(base, 'xml')
		newsoup = makesoup('<dublin_core schema="dc"></dublin_core>', 'xml')

		# map all the tags from the old soup
		tag_list = []		
		tag_list.append(makesoup("<dcvalue element='publisher'>" + soup.PublisherName.string + "</dcvalue>", 'xml').contents[0])
		tag_list.append(makesoup("<dcvalue element='publication' qualifier='journal'>" + soup.JournalTitle.string + "</dcvalue>", 'xml').contents[0])
		tag_list.append(makesoup("<dcvalue element='identifier' qualifier='issn'>" + soup.Issn.string + "</dcvalue>", 'xml').contents[0])
		if soup.Replaces.string:
			tag_list.append(makesoup("<dcvalue element='replaces'>" + soup.Replaces.string + "</dcvalue>", 'xml').contents[0])
		tag_list.append(makesoup("<dcvalue element='title'>" + soup.ArticleTitle.string + "</dcvalue>", 'xml').contents[0])
		if soup.VernacularTitle.string:
			tag_list.append(makesoup("<dcvalue element='title' qualifier='vernacular'>" + soup.VernacularTitle.string + "</dcvalue>", 'xml').contents[0])
		middle_name = " " + soup.MiddleName.string if soup.MiddleName.string else ''
		tag_list.append(makesoup("<dcvalue element='contributor' qualifier='author'>" + soup.LastName.string + ", " + soup.FirstName.string + middle_name + "</dcvalue>", 'xml').contents[0])
		tag_list.append(makesoup("<dcvalue element='affiliation' qualifier='institution'>" + soup.Affiliation.string + "</dcvalue>", 'xml').contents[0])
		tag_list.append(makesoup("<dcvalue element='type'>" + soup.PublicationType.string + "</dcvalue>", 'xml').contents[0])
		tag_list.append(makesoup("<dcvalue element='identifier' qualifier='doi'>" + soup.find(IdType="doi").string + "</dcvalue>", 'xml').contents[0])
		year = soup.find(PubStatus="received").find("Year").string
		month = soup.find(PubStatus="received").find("Month").string
		day = soup.find(PubStatus="received").find("Day").string
		tag_list.append(makesoup("<dcvalue element='date' qualifier='submitted'>" + year + "-" + month + "-" + day + "</dcvalue>", 'xml').contents[0])
		year = soup.find(PubStatus="revised").find("Year").string
		month = soup.find(PubStatus="revised").find("Month").string
		day = soup.find(PubStatus="revised").find("Day").string
		tag_list.append(makesoup("<dcvalue element='date' qualifier='revised'>" + year + "-" + month + "-" + day + "</dcvalue>", 'xml').contents[0])
		year = soup.find(PubStatus="accepted").find("Year").string
		month = soup.find(PubStatus="accepted").find("Month").string
		day = soup.find(PubStatus="accepted").find("Day").string		
		tag_list.append(makesoup("<dcvalue element='date' qualifier='available'>" + year + "-" + month + "-" + day + "</dcvalue>", 'xml').contents[0])
		if soup.FullTextURL.string:
			tag_list.append(makesoup("<dcvalue element='identifier' qualifier='uri'>" + soup.FullTextURL.string + "</dcvalue>", 'xml').contents[0])
		tag_list.append(makesoup("<dcvalue element='description' qualifier='abstract'>" + soup.Abstract.string + "</dcvalue>", 'xml').contents[0])
		
		dc = newsoup.find('dublin_core')
		for tag in tag_list:
			dc.append(tag)
		self.soup = newsoup
		
		dublin_core = open("dublin_core.xml", 'w')
		dublin_core.write(str(newsoup))
		dublin_core.close()
		
	def make_contents(self):
		os.chdir(self.path)
		contents = open('contents', 'w')
		for f in os.listdir("."):
			if f != 'dublin_core.xml' and f != 'contents':
				contents.write(f + '\n')
		contents.close()

for zip in os.listdir('.'):			
	parser = SOZipParser(f)
	parser.unzip()
	parser.reorganize()
	parser.make_dc()
	parser.make_contents()
	