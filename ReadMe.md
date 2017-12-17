## 简介
该 Git 仓库有2个分支

+ HexoBackup 存放生成网站的所有原始文件，默认分支
+ master 存放 Hexo 生成的静态文件

如果在其他电脑上需要更新博客，可以参照以下步骤：

##  拉取仓库
创建新文件夹：`mkdir HexoBackup`

进入该文件夹：`cd HexoBackup`

拉取仓库：`git clone https://github.com/Norcy/HexoBackup.git`

## 设置 HexoBackup 为默认分支
设置 HexoBackup 为默认分支：`git checkout HexoBackup`
git push --set-upstream origin HexoBackup

## 安装 Hexo Git 插件
项目文件夹（即 HexoBackup）下依次输入 npm install、npm install hexo-deployer-git --save（不需要 hexo init 这条指令）

## 一键部署
使用 go.sh 来一键生成 Hexo 静态文件和备份所有原始文件到 Github：`sh go.sh`


