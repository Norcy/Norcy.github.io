import sys;
import os;
import time;
import shutil;

class BlogItem(object):
	def __init__(self, year, mouth, date, type, name, url):
		super(BlogItem, self).__init__()
		if len(year):
			self.year = year;
		else:
			self.year = time.strftime("%Y", time.localtime());

		if len(mouth):
			self.mouth = mouth;
		else:
			self.mouth = time.strftime("%m", time.localtime());

		if len(date):
			self.date = date;
		else:
			self.date = time.strftime("%d", time.localtime());

		if len(type):
			self.type = type;
		else:
			self.type = "m";

		self.name = name;
		self.url = url;
	
	def markdownInfo(self):
		ret = "+ 《"+self.name+"》";
		if self.type == "b":
			ret += "（书）";
		elif self.type == "s":
			ret += "（连续剧）";
		return ret+"\n";

	def txtInfo(self):
		ret = self.year+" "+self.mouth+" "+self.date+" "+self.type+" "+self.name+"\n";
		return ret;

def addBlogItem(name, type=""):
	readFileName = "ReadList.txt";
	tmpFileName = "ReadList_tmp.txt";

	blogItem = BlogItem("", "", "", type, name, "");
	allItems = list();
	readFile = open(readFileName, 'r', encoding="utf-8");
	for line in readFile:
		line = line.strip();
		if len(line) == 0:
			continue;
		allItems.append(line+"\n");

	allItems.append(blogItem.txtInfo());
	allItems = list(set(allItems));
	allItems.sort(reverse=True);

	writeFile = open(tmpFileName, 'w', encoding="utf-8");
	for item in allItems:
		writeFile.write(item);

	writeFile.close();
	readFile.close();

	shutil.copy(tmpFileName, readFileName);
	os.unlink(tmpFileName);

	saveMarkdown();

def saveMarkdown():
	sourceFile = open("ReadList.txt", 'r', encoding="utf-8");
	destFilename = os.path.join(os.getcwd(), 'source', '_posts', "那些年，我看过的.md");
	# print(destFilename);
	destFile=open(destFilename,'w+');

	githubTitle = "---\ntitle: 那些年，我看过的\ndate: 2013-3-1\n\
description: 我的书籍/电影/电视剧/动漫列表\ncategories:\n- 代码之外 \n\
photos: images/girl.jpg\n---\n\n";
	destFile.write(githubTitle);

	blogItems = [];

	# Year sort 
	years = set();
	for line in sourceFile:
		line = line.strip();
		if len(line) == 0:
			continue;
		words = line.split(" ", 4);
		year = words[0].strip();
		mouth = words[1].strip();
		date = words[2].strip();
		type = words[3].strip();
		name = words[4].strip();

		years.add(year);

		blogItems.append(BlogItem(year, mouth, date, type, name, ""));
		

	yearsArray = list(years);
	yearsArray.sort(reverse = True);
	# print(yearsArray);

	# Mouth sort 
	
	for year in yearsArray:
		mouths = set();
		yearBlogItems = list();
		destFile.write("# "+year+"年\n");
		for blogItem in blogItems:
			if (blogItem.year == year):
				mouths.add(blogItem.mouth);
				yearBlogItems.append(blogItem);

		mouthArray = list(mouths);
		mouthArray.sort();
		for mouth in mouthArray:
			destFile.write("## "+mouth+"月\n");
			for blogItem in yearBlogItems:
				if (blogItem.mouth == mouth):
					destFile.write(blogItem.markdownInfo());
			destFile.write("\n");
		destFile.write("\n");


	sourceFile.close();
	destFile.close();

def main():
	if len(sys.argv) >= 3:
		addBlogItem(sys.argv[1], sys.argv[2]);
	elif len(sys.argv) >= 2:
		addBlogItem(sys.argv[1]);
	else:
		saveMarkdown();
	
  
if __name__=="__main__":
    main()
