# Hexo 博客备份方法总结
## 方法1：使用两个仓库
自己琢磨出来的，这个方法比较麻烦，详情请见：https://github.com/Norcy/HexoBackup

## 方法2：使用双分支
Google 出来的，比较优雅

### 简介
该 Git 仓库有2个分支

+ HexoBackup 存放生成网站的所有原始文件，默认分支
+ master 存放 Hexo 生成的静态文件

如果在其他电脑上需要更新博客，可以参照以下步骤：

###  拉取仓库
创建新文件夹：`mkdir HexoBackup`

进入该文件夹：`cd HexoBackup`

拉取仓库：`git clone https://github.com/Norcy/HexoBackup.git`

### 设置 HexoBackup 为默认分支
设置 HexoBackup 为默认分支：`git checkout HexoBackup`

### 安装 Hexo Git 插件
项目文件夹（即 HexoBackup）下依次输入 npm install、npm install hexo-deployer-git --save（不需要 hexo init 这条指令）

### 一键部署
使用 go.sh 来一键生成 Hexo 静态文件和备份所有原始文件到 Github：`sh go.sh`


## 方法3：使用 Travis
魁爷介绍，最优雅，终端电脑无需安装 Hexo

按照方法2，拉取仓库，设置默认分支，更新博客内容后，只需要使用 `sh Travis.sh` 脚本更新即可

参考：http://www.jianshu.com/p/5e74046e7a0f

