---
title: 别忘了NSTimer会保留其目标对象
date: 2016-06-20
categories:
- iOS
keywords: NSTimer;循环引用;self
---

# 别忘了NSTimer会保留其目标对象
```objc
self.timer = [NSTimer scheduledTimerWithTimeInterval:3
                                              target:self
                                            selector:@selector(f)
                                            userInfo:nil
                                             repeats:YES];

- (void)dealloc
{
    [self.timer invalidate];
}
```
由于 NSTimer 会引用住 self，而 self 又持有 NSTimer 对象，所以形成循环引用，dealloc 永远不会被执行，timer 也永远不会被释放，定时任务会一直执行下去
# 在 viewWillAppear 启动定时器，在 viewWillDisappear 停止定时器
这种方法将 NSTimer 的停止时机提前到 viewWillDisappear，所以不会出现循环引用的问题，只是维护起来比较麻烦

# 为什么不直接使用 weakself
我的第一直觉是像解决 Block 的循环引用一样，所以尝试 weakself 方案

```objc
__weak typeof(self) weakSelf = self;
self.timer = [NSTimer scheduledTimerWithTimeInterval:3
                                              target:weakSelf
                                            selector:@selector(f)
                                            userInfo:nil
                                             repeats:YES];
```
实验发现这种方案是无法解决循环引用的问题，这个问题其实很经典，新手很容易混淆，以为用 weakSelf 就可以解决所有循环引用问题

回顾下，Block 中只是对变量 weakSelf 拷贝了一份，是拷贝变量而不是拷贝对象。即 Block 中也新定义了一个 weakSelf 对象，内部实现代码类似这样`__weak blockWeakSelf = weakSelf;`，对象的 retainCount 没有变化。如果拷贝的是 self，那么 Block 内部实现代码类似这样`__strong blockStrongSelf = self;`，strong 类型的拷贝操作是会使对象的 retainCount 加1的

回到 NSTimer
>   The timer maintains a strong reference to this object until it (the timer) is invalidated

NSTimer 内部拿到 target 之后，就对其进行强引用，此时即使传入的是 weakSelf，但是 self 仍然会被引用住！因为是对对象本身进行引用，weakSelf 指向的跟 self 指向的都是同个对象，所以这里传 self 和 weakSelf 是没区别的。这也是为什么 block 里面用 strongSelf 强引用住 weakSelf，就可以让 self 不释放的原因

# 使用 Block 来解决循环引用
```objc
//.h
@interface NSTimer (NCYTimer)
+ (NSTimer *)ncy_scheduledTimerWithTimeInterval:(NSTimeInterval)interval block:(void(^)())block repeats:(BOOL)repeats;
@end

//.m
@implementation NSTimer (NCYTimer)
+ (NSTimer *)ncy_scheduledTimerWithTimeInterval:(NSTimeInterval)interval
                                          block:(void(^)())block
                                        repeats:(BOOL)repeats
{
    return [self scheduledTimerWithTimeInterval:interval
                                         target:self
                                       selector:@selector(ncy_blockHandle:)
                                       userInfo:[block copy]    //记得使用 copy
                                        repeats:repeats];
}

+ (void)ncy_blockHandle:(NSTimer *)timer
{
    void (^block)() = timer.userInfo;
    if (block)
    {
        block();
    }
}
@end
```

调用过程注意循环引用

```objc
__weak typeof(self) weakSelf = self;    //避免 block 强引用 self
self.timer = [NSTimer ncy_scheduledTimerWithTimeInterval:3
                                                   block:^{
                                                       typeof(weakSelf) strongSelf = weakSelf;
                                                       [strongSelf f];
                                                   }
                                                 repeats:YES];

```
+ 这套方案将计时器应执行的任务封装成 block，然后再放到 userInfo 传给计时器，block 作为参数传递时要 copy 到堆上，否则等到真正执行的时候很可能会被释放
+ 这套方法依然存在循环引用的问题，但因为现在 NSTimer 引用的 target 是类对象，__类对象本身是个单例__，无需回收，而不是调用者，所以循环引用了也没关系
+ 调用的时候记得 block 里面要用 weakSelf，然后使用的时候再将 weakSelf 转为 strongSelf，防止 block 执行过程中，self 被释放
+ 疑问点：为什么类方法可以使用 self？
    1. 类方法可以调用类方法
    2. 类方法不可以调用实例方法，但是类方法可以通过创建对象来访问实例方法
    3. 类方法不可以使用实例变量，类方法可以使用self，因为self不是实例变量
    	1. 实例方法里面的self，是对象的首地址
    	2. 类方法里面的self，是Class
+ 疑问点：全部定时器执行的代码放到一个单例去做，不会冲突吗？定时器每执行一个任务就是新建一个线程吗

    定时器每执行一个任务并没有新建一个线程，都是在当前线程，所以冲突是有可能的，假如某个任务很耗时，是会影响其他任务的执行的，更多线程问题可以参考[NSTimer和实现弱引用的timer的方式][1]

# 使用 NSProxy 来解决循环引用
引入一个对象 NSProxy，NSProxy 弱引用 self，然后 NSProxy 传入 NSTimer。即，self 强引用 NSTimer，NSTimer 强引用 NSProxy，NSProxy 弱引用 self，此时不会形成环。

这个 NSProxy 可参考 [YYWeakProxy](https://github.com/ibireme/YYKit/blob/master/YYKit/Utility/YYWeakProxy.m) 的实现

# 参考资料
+ 《Effective-Objective-C-读书笔记》之《第52条：别忘了NSTimer会保留其目标对象》
+ [NSTimer和实现弱引用的timer的方式][1]
[1]:http://www.jianshu.com/p/8121e4aadb4f