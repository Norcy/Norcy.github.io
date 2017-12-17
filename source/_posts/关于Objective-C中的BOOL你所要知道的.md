---
title: 关于Objective-C中的BOOL你所要知道的
date: 2016-06-01
categories:
- iOS
keywords: BOOL
---

# 问题
曾经同事遇到一个关于 BOOL 的坑，这里分享下

```objectivec
- (BOOL)isPreloadingViewShowing
{
    return self.mainCtl.preLoadingView.superview;
}
```
当 preLoadingView 明明有 superview 的时候，该函数居然有可能返回 NO

通过进一步的测试，发现在64位机器上没有这个问题，而在32位机器上有可能出现

Why?!先写个 Demo 测试下

---

# Demo
```objectivec
static BOOL dif(int a, int b)
{
    return a-b;
}

if (dif(11, 10))
{
    NSLog(@"11 != 10");
}

if (dif(10, 11))
{
    NSLog(@"10 != 11");
}

if (dif(512, 256))
{
    NSLog(@"512 != 256");
}
```

# Demo 运行结果
+ 64位机器上

```objectivec
11 != 10
10 != 11
512 != 256
```
+ 32位机器上

```objectivec
11 != 10
10 != 11
```

唯一的问题是为什么32位机器上最后一个的结果不对？！

# Objective-C 中的 BOOL 到底是什么
第一个要搞清楚的问题是，Obj-C 中的 BOOL 到底是什么？打开 objc.h，查看 BOOL 的定义

```objectivec
// objc.h

#if (TARGET_OS_IPHONE && __LP64__)  ||  TARGET_OS_WATCH
typedef bool BOOL;
#else
typedef signed char BOOL; 
#endif
```
意思是，在64位机器上，BOOL 是 bool，bool 的取值只有 true or false；在32位机器上，BOOL 是 signed char，长度8 bits

所以，没有多余的机器可以测试的时候，我们可以把`static BOOL dif(int a, int b)`改为`static bool dif(int a, int b)`或`static signed char dif(int a, int b)`来模拟64位机器或32位机器的情况


# Demo 结果分析
Demo 中，a-b的结果是 int 类型，
> int 作为返回值的时候会被强转为 BOOL，32位机器上 int 强转为 BOOL 的时候，其实是转为 signed char，只取了最低的8位，而64位机器上，BOOL 就是 bool，什么问题都没有，0即 false，非0即 true，可以像 C/C++ 语言那样放心使用

+ 64位机器上

```objectivec
11-10=1 -> 0x0000000000000001 -> true
10-11=-1 -> 0xffffffffffffffff -> true
512-256=256 -> 0x0000000000000100 -> true
```
+ 32位机器上

```objectivec
11-10=1 -> 0x00000001 -> 00000001 -> true
10-11=-1 -> 0xffffffff -> 11111111 -> true
512-256=256 -> 0x00000100 -> 00000000 -> false
```

关于32位机器与64位机器数据类型长度类型，可以参见[32位机器与64位机器数据类型长度][1]

---

# 解决方法
理清了 Demo，最上面的问题就迎刃而解了，superview 是一个指针（指针在 32/64 位机器上的位数是不同的），32位机器上，如果指针地址刚好最后8位都是0，那么即使指针不是空的，也会导致返回结果为空

正确的做法应该为

```objectivec
- (BOOL)isPreloadingViewShowing
{
    if (self.mainCtl.preLoadingView.superview) 
        return YES;
    else
        return NO;
}
```

# 结论
> 取 int 或指针等类型作为 BOOL 的返回值时要注意，强转的时候可能会只取最低8位作为结果，尽量避免这种情况

# 参考
+ [重新认识一下OC 中的 BOOL 值](http://www.jianshu.com/p/2b97f18918b3?utm_campaign=hugo&utm_medium=reader_share&utm_content=note)
+ [32位机器与64位机器数据类型长度][1]
[1]: https://developer.apple.com/library/ios/documentation/General/Conceptual/CocoaTouch64BitGuide/Major64-BitChanges/Major64-BitChanges.html