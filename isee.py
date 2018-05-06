#coding=utf-8
import sys;
import os;
import time;
import shutil;
import stat;

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

def updateBlogItem(cmdType, name, type="", year="", mouth="", date=""):
    readFileName = os.path.join(sys.path[0], "ReadList.txt");
    tmpFileName = os.path.join(sys.path[0], "ReadList_tmp.txt");

    blogItem = BlogItem(year, mouth, date, type, name, "");
    allItems = list();
    readFile = open(readFileName, 'r', encoding="utf-8");
    for line in readFile:
        line = line.strip();
        if len(line) == 0:
            continue;
        words = line.split(" ", 4);
        curType = words[3].strip();
        curName = words[4].strip();
        if cmdType == "del":
            if curType == type && curName == name:
                continue;

        allItems.append(line+"\n");

    if cmdType != "del":
        allItems.append(blogItem.txtInfo());

    allItems = list(set(allItems));
    allItems.sort(reverse=True);

    writeFile = open(tmpFileName, 'w', encoding="utf-8");
    #os.chmod(tmpFileName, stat.S_IRWXU|stat.S_IRWXG|stat.S_IRWXO);
    for item in allItems:
        writeFile.write(item);

    writeFile.close();
    readFile.close();

    shutil.copyfile(tmpFileName, readFileName);
    #os.unlink(tmpFileName);
    saveMarkdown();

def saveMarkdown():
    sourceFileName = os.path.join(sys.path[0], "ReadList.txt");    
    sourceFile = open(sourceFileName, 'r', encoding="utf-8");
    destFilename = os.path.join(sys.path[0], 'source', '_posts', "那些年，我看过的.md");
    # print(destFilename);
    destFile = open(destFilename, 'w', encoding="utf-8");

    githubTitle = "---\ntitle: 那些年，我看过的\ndate: 2013-3-1\n\
description: 我的书籍/电影/电视剧/动漫列表\ncategories:\n- 代码之外 \n\
---\n\n";
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
    os.chdir(sys.path[0]);
    os.system("/usr/bin/git pull origin HexoBackup");
    os.system("/usr/bin/git add .");
    os.system("/usr/bin/git commit -m 'Update From PublicAccount'");
    os.system("/usr/bin/git push origin HexoBackup");    


def main():
    #os.system("whoami");
    if len(sys.argv) <= 2:
        saveMarkdown();
    else:
        cmdType="";
        year="";
        mouth="";
        date="";
        type="";
        name="";

        if len(sys.argv) >= 7:
            date = sys.argv[6];
        if len(sys.argv) >= 6:
            mouth = sys.argv[5];
        if len(sys.argv) >= 5:
            year = sys.argv[4];
        if len(sys.argv) >= 4:
            type = sys.argv[3];
        if len(sys.argv) >= 3:
            name = sys.argv[2];
        if len(sys.argv) >= 2:
            cmdType = sys.argv[1];

        
        updateBlogItem(cmdType, name, type, year, mouth, date);
    
  
if __name__=="__main__":
    main()
