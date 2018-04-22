---
title: NSUserdefaults与NSMutableArray的坑
date: 2016-06-12
categories:
- iOS
keywords: NSUserdefaults;NSMutableArray;死锁;mutex lock;immutable
---

# 需求
App 本地记录用户看过的视频记录
# 方案
很简单的需求，我们可以使用 NSUserDefaults 来维护一个数组，每次有新的视频记录产生的时候，如果该视频记录不存在，则添加进数组，并更新 NSUserDefaults，否则不做任何操作

# 代码与坑
## 版本一
很直观地，我写出了下面这段代码

```objectivec
NSMutableArray *videoArray = [[NSUserDefaults standardUserDefaults] objectForKey:VIDEOKEY]; 
if (![videoArray containsObject:item])  //nil at first time
{
    [videoArray addObject:item];
    [[NSUserDefaults standardUserDefaults] setObject:videoArray forKey:VIDEOKEY];
}
```

问题来了

+ 如果是首次运行这段代码，videoArray 将会是空的，之后对 videoArray 做的一切操作都是没用的

## 版本二

好，继续修改我们的代码，确保 videoArray 不空

```objectivec
NSMutableArray *videoArray = [[NSUserDefaults standardUserDefaults] objectForKey:VIDEOKEY];
if (!videoArray)
    videoArray = [NSMutableArray array];
if (![videoArray containsObject:item])
{
    [videoArray addObject:item];    //crash
    [[NSUserDefaults standardUserDefaults] setObject:videoArray forKey:VIDEOKEY];
}
```

问题来了

+ 第一次插入元素没问题，但是第二次插入的时候在`[videoArray addObject:item];`就 Crash 了

Crash信息：

```objectivec
Terminating app due to uncaught exception 'NSInternalInconsistencyException', reason: '-[__NSCFArray insertObject:atIndex:]: mutating method sent to immutable object'
```

为什么？因为我对 NSUserDefaults 的理解出错了，其实

```objectivec
NSUserDefaults 的 objectForKey 方法永远返回不可变对象
(NSUserDefaults will always return an immutable version of the object you pass in)
```

+ 第一次运行，videoArray 是一个 NSMutableArray（__NSArrayM），往 NSUserDefaults 里塞 NSMutableArray 也不会出错
+ 第二次运行，videoArray 已经存在，它是一个 NSArray（__NSCFArray），NSArray 执行 addObject，必挂无疑！

## 版本三
好啊，那 NSUserDefaults 会不会有可以返回可变对象的接口呢，比如

```objectivec
NSMutableArray *videoArray = [[NSUserDefaults standardUserDefaults] mutableArrayValueForKey:VIDEOKEY];
if (![videoArray containsObject:item])
{
    [videoArray addObject:item];
    [[NSUserDefaults standardUserDefaults] setObject:videoArray forKey:VIDEOKEY];
}
```

这样看起来好像很完美，但是要明白的是

+ `mutableArrayValueForKey` 是 KVC 里面的内容，而不是 NSUserDefaults 里的
+ 即使 key 没找到，`mutableArrayValueForKey` 也不会返回 nil，所以这一段代码不需要做非空判断
+ videoArray 打印出来是一个 `NSKeyValueSlowMutableArray`
+ 其实如果直接修改 KVC 获取的这个可变对象而不写入 NSUserDefaults，其实是会影响 NSUserDefaults 里的内容，所以删除最后一行代码运行结果也是对的
+ NSUserdefaults 返回不可变对象一定有它的原因（比如不想返回的对象被别人直接修改，而是必须通过自身的`setObject:forKey:`接口来修改），这里其实是借 KVC 的手实现了获得一个可变对象，这其实是违背了 NSUserdefaults 的初衷的，这种做法不可取

但是，这里还有个最大最大的问题，**死锁**，留到后面讲。

## 版本四
最终版本出炉，使用`arrayForKey:`获取数组，并新建一个可变数组来执行增删操作

```objectivec
NSMutableArray *mutableVideoArray;
NSArray *videoArray = [[NSUserDefaults standardUserDefaults] arrayForKey:VIDEOKEY];
if (videoArray)
    mutableVideoArray = [videoArray mutableCopy];
else
    mutableVideoArray = [NSMutableArray array];
    
if (![mutableVideoArray containsObject:item])
{
    [mutableVideoArray addObject:item];
    [[NSUserDefaults standardUserDefaults] setObject:mutableVideoArray forKey:VIDEOKEY];
}
```
+ 这里使用`arrayForKey`而不是`objectForKey`，这样更贴切。

# 关于死锁
经实验，下面是发生死锁需要的最少行的代码

```objectivec
NSMutableArray *videoArray = [[NSUserDefaults standardUserDefaults] mutableArrayValueForKey:VIDEOKEY];
[videoArray addObject:item];
[[NSUserDefaults standardUserDefaults] setObject:videoArray forKey:VIDEOKEY];
```
1. 如果删除`[videoArray addObject:item];`这一行，直接 Crash，因此要研究死锁问题，必须先保证数组非空，所以这里是最少代码
2. 发生死锁是在最后一行代码里，是 iOS8 及以后版本的系统 bug（不过这种使用方法根本不对，也可以不算是 bug）
3. 如果断点在最后一行，则不会死锁，而断点在第二行还是会死锁。因为断点错开了代码之间执行的时间，所以我们有理由推测，死锁是 KVC 里面的 addObject: 与 setObject: 同时进行的时候而产生的
4. [StackOverFlow](http://stackoverflow.com/questions/26004892/ios-8-freezes-at-updating-userdefaults-object)上有类似问题

# 结论
+ 使用 NSUserDefaults 的时候注意非空判断
+ NSUserDefaults 的 objectForKey 方法永远返回不可变对象，但 setObject:forKey: 的 object 参数可以是可变对象
+ mutableArrayValueForKey 是 KVC 里面的内容，而不是 NSUserDefaults 里的，不建议使用它来获取 NSUserDefaults 的内容
+ NSUserDefaults+KVC 的组合在 iOS8 及其之后是会有死锁的问题

