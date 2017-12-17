---
title: iOS Reading List
description: 未整理的知识列表
date: 2016-1-27
categories:
- Others
photos: 
keywords:
---

# 2016-01
+ ## [iOS 开发博客列表](https://github.com/tangqiaoboy/iOSBlogCN)

# 2016-02
+ ## frame 和 bounds 区别

	1. [设置父 View 的 bounds 的原点，本质是将父 View 的左上角顶点改为 bounds 的原点值](http://blog.csdn.net/mad1989/article/details/8711697)
	2. 快速输出 frame 和 bounds：NSStringFromCGRect(view.frame)
	3. [bounds 比其 frame 大或小的影响](http://www.cocoachina.com/ios/20140925/9755.html)
	4. [横屏之后，播放器 Controller 的 view 的 frame 的 size 为(320,480)，而 bounds 的 size 为(480,320)](http://stackoverflow.com/questions/17036225/why-self-view-frame-and-self-view-bounds-are-different-w`hen-the-devices-rotate)，这是因为横屏对播放器 Controller 的 view 应用了 transform，应用了 transform 之后 frame 不变，但是 bounds 会改变
	
		In addition the frame property’s values are undefined if the view has any transform other than the identity transform. Rotating a view into landscape mode applies a transform to the view so it is not safe to rely on frame values for an app in landscape mode.
	
		摘自 [UIView Frames and Bounds](http://blog.carbonfive.com/2010/05/27/uiview-frames-and-bounds/)

+ ## [如何成为一名入门级 iOS 开发者](http://www.jianshu.com/p/958c1c52db6c)

+ ## 调试过程使用"thread return"or "thread return YES"来 return 函数

+ ## [SVN 合并分支](https://tortoisesvn.net/docs/nightly/TortoiseSVN_zh_CN/tsvn-dug-merge.html)

# 2016-03
+ ## 调试技巧之条件断点(BOOL)[str isEqualToString:@"ABC"]