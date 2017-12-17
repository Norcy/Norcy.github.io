# 当重装电脑之后，或者想在其他电脑上修改博客，可以使用下列步骤：
## 1. 先根据[官方网站](https://hexo.io/zh-cn/docs/index.html)安装 Hexo
## 2. 配置 Git 的个人信息，生成新的 ssh 密钥

1. 检查 ssh keys 是否存在打开终端输入 `ls -al ~/.ssh` 
    
    如果目录下面没有 `id_rsa`、`id_rsa.pub` 则表示key不存在
    
2. 如果需要备份，则执行 `mkdir key_backup` 和 `mv id_isa* key_backup`
3. 生成新的 Key：`ssh-keygen -t rsa -b 4096 -C "your_email@example.com"`
    
    输出显示：

    ```
    Generating public/private rsa key pair. 
    Enter file in which to save the key (/Users/your_user_directory/.ssh/id_rsa):<press enter>
    ```

    直接回车，不要修改默认路径

    ```
    Enter passphrase (empty for no passphrase):<enter a passphrase>
    Enter same passphrase again:<enter passphrase again>
    ```
    
    如果设置密码，则每次远程操作之前会要求输入密码。建议直接回车不输入
4. 成功：

    ```
    Your identification has been saved in /Users/your_user_directory/.ssh/id_rsa. 
    Your public key has been saved in /Users/your_user_directory/.ssh/id_rsa.pub. 
    The key fingerprint is: ... ...
    ```

5. 先确认 ssh-agent 是可用的，输入 `eval $(ssh-agent -s)`
    
    ```
    Agent pid 20632
    ```

6. 将 ssh key 添加到 ssh-agent，输入 `ssh-add ~/.ssh/id_rsa`

    ```
    Identity added: /Users/Norcy/.ssh/id_rsa (/Users/Norcy/.ssh/id_rsa)
    ```
    
7. 提交公钥：
    
    7.1. 复制 ~/.ssh/id_rsa.pub 的文本内容

    7.2 打开 https://github.com/settings/ssh ，点击 Add SSH Key 按钮，粘贴进去保存即可
        
## 3. 拉取仓库
创建新文件夹：`mkdir HexoBackup`

进入该文件夹：`cd HexoBackup`

拉取仓库：`git clone https://github.com/Norcy/HexoBackup.git`

## 4. 安装 Hexo Git 插件
项目文件夹（即 HexoBackup）下依次输入 `npm install`、`npm install hexo-deployer-git --save`（不需要 `hexo init` 这条指令）

## 5. 部署完毕，测试执行 `hexo clean`, `hexo g`, `hexo s`, `hexo d`

## 6. 每次编辑完文章之后使用 [go.sh](https://github.com/Norcy/HexoBackup/blob/master/go.sh) 来备份源文件和更新博客

# 参考文档：

+ [Github之SSH连接配置](http://www.linmuxi.com/2016/02/24/github-config-ssh/)
+ [Hexo 官方网站](https://hexo.io/zh-cn/docs/index.html)
+ [如何创建公钥](https://gist.github.com/yisibl/8019693)

