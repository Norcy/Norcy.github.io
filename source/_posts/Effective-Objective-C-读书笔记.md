---
title: Effective-Objective-C-读书笔记
description: 《Effective Objective-C 2.0  编写高质量iOS与OS X代码的52个有效方法》
date: 2016-03-19
categories:
- 读书笔记
photos: 
---

# 第1章 熟悉Objective—C 
## 第1条：了解Objective—C语言的起源
```objectivec
NSString *s1 = @"Hello";
NSString *s2 = s1;
```
+ s1 和s2 的内存分配在栈上
+ @"Hello"的内存分配在堆上
+ s1 和 s2 指向同一块内存


## 第2条：在类的头文件中尽量少引入其他头文件

## 第3条：多用字面量语法，少用与之等价的方法
### 使用字面量语法，它是一种语法糖：
```objectivec
NSString *str = @"Hello";
NSNumber *intNum = @1;
NSNumber *doubleNum = @2.5;
NSNumber *charNum = @'a';
NSNumber *boolNum = @YES;
NSArray *array = @[@"hello", @1, @2.5, @'a'];
NSString *str2 = array[0];
NSDictionary *dic = @{@"1":@1, @"2":@2};
```
### 这个语法糖更容易暴露隐藏的问题
```objectivec
NSArray *array1 = [NSArray arrayWithObjects: obj1, obj2, obj3, nil];
NSArray *array2 = @[obj1, obj2, obj3];
```
如果 obj1 和 obj3 非空，而 obj2 是 nil

那么 array1 只有一个对象，不会出错；而 array2 在插入的时候会抛出异常

### 使用字面量语法创建的对象是不可变的，若想要创建一个可变的对象，需要复制一份：
```objectivec
NSMuatableArray *mArray = [@[@1, @2] mutableCopy];
```
## 第4条：多用类型常量，少用#define预处理指令 
详见[NSNotification Name 最佳写法](http://www.cnblogs.com/chenyg32/p/5080301.html)

## 第5条：用枚举表示状态、选项、状态码
### 使用 `NS_ENUM` 和 `NS_OPTIONS` 来表示`状态机`，
```objectivec
//NS_ENUM，定义状态等普通枚举
typedef NS_ENUM(NSUInteger, TTGState) {
    TTGStateOK = 0,
    TTGStateError,
    TTGStateUnknow
};

//NS_OPTIONS，定义选项
typedef NS_OPTIONS(NSUInteger, TTGDirection) {
    TTGDirectionNone = 0,
    TTGDirectionTop = 1 << 0,
    TTGDirectionLeft = 1 << 1,
    TTGDirectionRight = 1 << 2,
    TTGDirectionBottom = 1 << 3
};
```
### 如果一个`枚举变量`可以同时表示一个或多个选项的集合，那么应当使用 `NS_OPTIONS`，而且各个选项的值应定义为2的 N 次幂，如上代码，这样就可以用`或操作`将其组合起来进行表示

### 相比较 C 语言中的枚举，使用 `NS_ENUM` 和 `NS_OPTIONS` 的好处是，可以确保实现枚举值的数据类型是开发者所指定的，而不会默认采用编译器所选的类型
```objectivec
typedef enum _TTGState {
    TTGStateOK  = 0,
    TTGStateError,
    TTGStateUnknow
} TTGState;
```
### 处理枚举类型的 switch 分支中，不要实现 default 分支。这样的话，加入新的枚举值之后，编译器就会给出提示：switch 语句并未处理所有枚举

### 参考链接：[Enum-枚举的正确使用-Effective-Objective-C-读书笔记-Item-5](http://tutuge.me/2015/03/21/effective-objective-c-5-enum/)

# 第2章 对象、消息、运行期 
## 第6条：理解“属性”这一概念 
### 理解好`属性`和`实例变量`的区别

属性 = 实例变量 + setter + getter

如果声明属性

    @property (nonatomic, copy) NSString *str;

则编译器会默认实现

```objectivec
//.h
- (NSString *)str;
- (void)setStr:(NSString *)str;

//.m
- (NSString *)str
{
	return _str;
}

- (void)setStr:(NSString *)str
{
	_str = [str copy];
}
```
其中 `_str` 就是`实例变量`
 
### 使用`点语法`访问属性 = 调用 setter/getter 方法

### Property 的4种 attribute
	
+ 原子性(atomic, nonatomic)
+ 读写权限(readonly, readwrite)
+ 内存管理(strong, weak, unsafe_unretained, retain, assign, copy)
+ 存取方法(getter, setter)

### 非 ARC 下，没有 weak

### ARC下，修饰指针的内存修饰符
+ `__weak`:不retain，如果对象被回收，该指针会被置nil
+ `__strong`:默认，如果对象被回收，需要手动将指针置为nil？
+ `__unsafe__unretained`:不retain，如果对象被回收，该指针不会被置nil（为了在ARC刚发布时兼容iOS 4以及版本，现可废弃）
+ `__autoreleasing`:实现把对象"按引用传递"给方法，变量在方法返回时自动释放

编译器在为一个 property 合成实例变量的时候，也会使用相应的修饰符来修饰这个实例变量

### 常见数据类型的内存修饰符（待补充）
| 数据类型 | 内存修饰符 |
| :--:|:--:|
| 基本数据类型(int, NSInteger) | assign |
| block | copy |
| NSString | copy |
| NSMutableString | strong |
| NSArray | copy |
| NSMutableArray | strong |

### NSArray 用 strong 还是 copy 修饰
```objc
//.h
@property (nonatomic, strong) NSArray *strongArray;
@property (nonatomic, copy)   NSArray *copyedArray;
//.m
self.strongArray = [NSArray array];
self.copyedArray = [NSArray array];
    
NSMutableArray *mutableArray = [@[@"1"] mutableCopy];
self.strongArray = mutableArray;
self.copyedArray = mutableArray;
    
[mutableArray addObject:@"2"];
    
NSLog(@"%@\n%@\n%@", mutableArray, self.strongArray, self.copyedArray); //输出 (1,2) (1,2) (1)
```
可以看到使用 strong 修饰 NSArray 非常不安全，数组元素被外部修改了。原因是执行其 setter 操作的时候，假如将一个可变数组赋值给 NSArray，那么 NSArray 的指针会直接指向一个可变对象，然后就可以通过这个可变对象来修改 NSArray。而使用 copy 就不会有这个问题。所以 NSArray 建议使用 copy 修饰，而 NSMutableArray 没有这个问题，可以用 strong 修饰。


## 第7条：在对象内部尽量直接访问实例变量
### 类内使用 self.xxx 和 _xxx 的区别

+ 访问 _xxx 不经过 setter/getter 方法，速度更快
+ 访问 _xxx 不经过 setter 方法，绕过了 property 定义的内存管理逻辑。比如 ARC 下直接访问一个声明为 copy 的属性的实例变量，那赋值过程中，并没有 copy 操作
+ 访问 _xxx 不经过 setter/getter 方法，无法触发 KVO
+ 访问 _xxx 不经过 setter/getter 方法，无法断点

### 什么时候使用 _xxx

+ 折中方案，读的时候使用 _xxx，写的时候使用 self.xxx
+ 父类的 init 和 dealloc 尽量使用 _xxx 来访问，因为如果子类覆盖了 setter 方法并做了某些非空检查，那么父类初始化的时候会调用子类的 setter 方法，由于是在 init/dealloc，参数可能都是空的，此时报错
+ 如果实例变量在父类中声明，那么子类只能使用 self.xxx 来访问属性
+ 使用 lazy initialization 的情况下，必须通过 self.xxx 来访问属性，否则初始化失败
```objectivec
- (NSString *)str
{
	if (!_str)
		_str = [[NSString alloc] init];
	return _str;
}
```
## 第8条：理解“对象等同性”这一概念 


## 第9条：以“类族模式”隐藏实现细节 
## 第10条：在既有类中使用关联对象存放自定义数据 
“关联对象”（Associated Object）是用来为对象关联其他对象的，比如不定义子类的前提下为 UIAlertView 添加一个 Block 属性；比如为一些无法更改其属性（比如工作中的协议文件）的类添加属性

### 语法
```objc
void objc_setAssociatedObject (id object, void *key, id value, objc_AssociationPolicy policy);

id objc_getAssociatedObject(id object, void *key);

void objc_removeAssociatedObject(id object);    // 移除object上的所有关联对象
```
其中 objc_AssociationPolicy 是关联对象的属性，如下

```objc
OBJC_ASSOCIATION_ASSIGN             --- assign
OBJC_ASSOCIATION_RETAIN_NONATOMIC   --- nonatomic, retain
OBJC_ASSOCIATION_COPY_NONATOMIC     --- nonatomic, copy
OBJC_ASSOCIATION_RETAIN             --- retain
OBJC_ASSOCIATION_COPY               --- copy
```

### 与 NSDictionary 的区别
设置关联对象值时，若想令两个健匹配到相同的一个值，则二者必须是完全相同的指针才行。

所以 key 值（一般为 NSString）最好定义为一个全局静态变量，而不能每次都用 @"xxx"

### 例子1
假如一个页面有2个弹窗，那么代码可能是这样写

```objc
- (void)askUserAQuestion
{
    UIAlertView *alert = [[UIAlertView alloc]
            initWithTitle:@"Question"
                  message:@"What do you want to do?"
                 delegate:self
        cancelButtonTitle:@"Cancel"
        otherButtonTitles:@"Continue", nil];
    [alert show];
}

// UIAlertViewDelegate protocol method
- (void)alertView:(UIAlertView *)alertView clickedButtonAtIndex:(NSInteger)buttonIndex
{
    if (buttonIndex == 0)
    {
        [self doCancel];
    }
    else
    {
        [self doContinue];
    }
}
```

缺点是alertView的处理逻辑和初始化逻辑分离，不易阅读。有一种解决方法是为 UIAlertView 添加一个 block 属性

```objc
#import <objc/runtime.h>

static void *EOCMyAlertViewKey = "EOCMyAlertViewKey";

- (void)askUserAQuestion
{
	UIAlertView *alert = [[UIAlertView alloc]
	        initWithTitle:@"Question"
	              message:@"What do you want to do?"
	             delegate:self
	    cancelButtonTitle:@"Cancel"
	    otherButtonTitles:@"Continue", nil];

	void (^block)(NSInteger) = ^(NSInteger buttonIndex) {
	    if (buttonIndex == 0)
	    {
		    [self doCancel];
	    }
	    else
	    {
		    [self doContinue];
	    }
	};

	objc_setAssociatedObject(alert,
                             EOCMyAlertViewKey,
                             block,
                             OBJC_ASSOCIATION_COPY);

	[alert show];
}

// UIAlertViewDelegate protocol method
- (void)alertView:(UIAlertView *)alertView
    clickedButtonAtIndex:(NSInteger)buttonIndex
{
	void (^block)(NSInteger) = objc_getAssociatedObject(alertView, EOCMyAlertViewKey);
	block(buttonIndex);
}
```

优点就是处理逻辑和初始化逻辑不再分离，但是使用 block 一不小心可能会引起保留环。一种更好的方法是弄个子类，比如 SIAlertView

### 例子2 为协议文件添加属性
.h

```objc
#import "QLJCEONAVRSSFeed.h"

@interface QLJCEONAVRSSFeed (contentOffset)

@property (nonatomic, assign)CGPoint savedOffset;

@end
```
.m

```objc
#import "QLJCEONAVRSSFeed+contentOffset.h"

#define feed_saved_Off_set_x_key @"feed_saved_Off_set_x_key"
#define feed_saved_Off_set_y_key @"feed_saved_Off_set_y_key"

@implementation QLJCEONAVRSSFeed (contentOffset)

@dynamic savedOffset;

- (CGPoint)savedOffset
{
    NSNumber *xObj = objc_getAssociatedObject(self, feed_saved_Off_set_x_key);
    NSNumber *yObj = objc_getAssociatedObject(self, feed_saved_Off_set_y_key);
    
    CGPoint point = CGPointMake([xObj floatValue], [yObj floatValue]);
    
    return point;
}

- (void)setSavedOffset:(CGPoint)savedOffset
{
    objc_setAssociatedObject(self, feed_saved_Off_set_x_key, @(savedOffset.x), OBJC_ASSOCIATION_RETAIN_NONATOMIC);
    objc_setAssociatedObject(self, feed_saved_Off_set_y_key, @(savedOffset.y), OBJC_ASSOCIATION_RETAIN_NONATOMIC);
}
```


## 第11条：理解objc_msgSend的作用
见 [Objective-C中的消息转发机制](http://norcy.github.io/2016/09/25/Objective-C%E4%B8%AD%E7%9A%84%E6%B6%88%E6%81%AF%E8%BD%AC%E5%8F%91%E6%9C%BA%E5%88%B6/)
## 第12条：理解消息转发机制
见 [Objective-C中的消息转发机制](http://norcy.github.io/2016/09/25/Objective-C%E4%B8%AD%E7%9A%84%E6%B6%88%E6%81%AF%E8%BD%AC%E5%8F%91%E6%9C%BA%E5%88%B6/)

 
## 第13条：用“方法调配技术”调试“黑盒方法”
创建自己的方法

```objc
#import "NSString+MyAdditions.h"

@implementation NSString (MyAdditions)
- (NSString *)myLowercaseString
{
    NSString *lowercase = [self myLowercaseString];
    NSLog(@"This is my own method: %@", lowercase);
    return lowercase;
}
@end
```
替换

```objc
Method originalMethod = class_getInstanceMethod([NSString class], @selector(lowercaseString));
Method swappedMethod = class_getInstanceMethod([NSString class], @selector(myLowercaseString));
method_exchangeImplementations(originalMethod, swappedMethod);
```

 
## 第14条：理解“类对象”的用意 
### 我们所说的 Objective-C 对象究竟是什么

```objc
typedef struct objc_object{
  Class isa;  //=> 指向对象所属的类
} *id;
```
结论：Objective-C 对象 = id = objc_object

### 那么 Class 是什么
```objc
typedef struct objc_class *Class;  
```
### 那么 objc_class 又是什么
```objc
struct objc_class {  
    Class isa;
    Class super_class;  
    const char *name;  
    long version;  
    long info;  
    long instance_size;  
    struct objc_ivar_list *ivars;  
    struct objc_method_list **methodLists;  
    struct objc_cache *cache;  
    struct objc_protocol_list *protocols;  
}; 
```

### 类的继承体系
![](http://image.norcy.xyz/isa.png)

```objc
NSString *str = @"Hello";
```
str 是一个对象，is a NSString

NSString 是类，is a NSString metaclass

NSString metaclass 是元类，类方法就定义在这里


# 第3章 接口与API设计 
## done 第15条：用前缀避免命名空间冲突 
## done 第16条：提供“全能初始化方法”
详见[Designated Initializer](http://www.cnblogs.com/chenyg32/p/4870303.html)
## done 第17条：实现description方法
## done 第18条：尽量使用不可变对象
+ 如果某个属性只是内部可修改，则在 .h 中应该声明为 readonly，然后再在扩展里面声明为 readwrite
+ 不要把可变的 Collection 对象(NSMutableSet/NSMutableDictionary/NSMutableArray 等)作为属性公开，应该提供 readonly 版本以及读写方法

## done 第19条：使用清晰而协调的命名方式:
### 如果一个方法返回了某个变量，该方法命名不要使用 getXXX，直接使用 XXX 就行了

### 对于 BOOL 类型，可以在属性声明的时候，指定其 getter 为 isXXX
    @property (nonatomic, assign, getter = isOn) on;

## done 第20条：为私有方法名加前缀 
## done 第21条：理解Objective—C错误模型 
## done 第22条：理解NSCopying协议 
详见[浅析Objective-C的copy](http://www.cnblogs.com/chenyg32/p/5167194.html)
 
# 第4章 协议与分类 
## 第23条：通过委托与数据源协议进行对象间通信 
```objc
if([_delegate respondsToSelector:@selector(networkFetcher:didReceiveData:)])
{ 
    [_delegate networkFetcher:self didReceiveData:data];  
}
```

如果上面的代码写了很多次，则可以考虑以下优化：

```objc
// 在扩展中定义结构体
@interface EOCNetworkFetcher(
{ 
    struct { 
    unsigned int didReceiveData : 1; 
    unsigned int didFailWithError : 1; 
    } _delegateFlags; 
} 
@end  

@implementation 
EOCNetworkFetcher 
- (void)setDelegate:(id)delegate
{ 
    _delegate = delegate; // 缓存委托对象相应方法能力 
    _delegateFlags.didReceiveData = [delegate respondsToSelector:@selector(networkFetcher:didReceiveData:)]; 
    _delegateFlags.didFailWithError = [delegate respondsToSelector:@selector(networkFetcher:didFailWithError:)]; 
} 
@end

这样每次调用delegate相关方法之前就只需要直接查询标志：
if(_delegateFlags.didReceiveData)
{ 
    [_delegate networkFetcher:self didReceiveData:data]; 
}
```

## done 第24条：将类的实现代码分散到便于管理的数个分类之中 
## 第25条：总是为第三方类的分类名称加前缀
1. 为第三方类添加分类时，总应给其名称加上你专用的前缀
2. 为第三方类添加分类时，总应给方法名加上你专用的前缀

```objc
@interface NSString (ABC_HTTP)
-(NSString *)abc_urlEncodedString;
-(NSString *)abc_urlDecodedString;
@end
```

## 第26条：勿在分类中声明属性 
属性应该在主类中声明

如果分类中声明属性需要自己重写 setter 和 getter

方法如下：
```objc
#import <objc/runtime.h>

static const char *kFriendsPropertyKey = "kFriendsPropertyKey";

@implementation Person(Friendship)
@dynamic friends;

-(NSArray*)friends 
{
　　return objc_getAssociatedObject(self, kFriendsPropertyKey);
}

-(void)setFriends:(NSArray*)friends 
{
　　objc_setAssociaedObject(self, kFriendsPropertyKey, friends, OBJC_ASSOCIATION_NONATOMIC);
}
@end
```

缺点如下
1. 相似的代码要写很多遍
2. 极易忽略属性定义的内存管理语义，且不好维护

## 第27条：使用“class—continuation分类”隐藏实现细节
声明私有实例变量的3种方法

+ 方法1：对外暴露，声明为 private（暴露了细节，不建议）

    .h

    ```objectivec
    @interface ABC:NSObject
    {
    @private
        XYZ *_xyz;
    }
    @end
    ```
    1. 把私有变量放在头文件，暴露了细节，不好
    2. 假如该实例变量是 objective-c++ 类，则所有引入该头文件的类都要编译为 objective-c++，即使使用 @class 也无法解决这个问题
    3. 所以既然是私有变量，干嘛不放在 .m 中，偏偏要放到 .h 中作死呢？
    
    
+ 方法2：不对外暴露

    .m
    
    ```objectivec
    @interface ABC()
    {
        XYZ *_xyz;
    }
    @property (nonatomic, strong) XYZ *xyz2;
    @end
    ```
+ 方法3：对外只读，对内读写

    .h
    
    ```objectivec
    @property (nonatomic, readonly) XYZ *xyz;
    ```
    .m
    
    ```objectivec
    @interface ABC()
    @property (nonatomic, readwrite) XYZ *xyz;
    @end
    ```

## done 第28条：通过协议提供匿名对象 

# 第5章 内存管理 
## 第29条：理解引用计数 
### 悬浮指针

```objectivec
NSNumber *number = [[NSNumber alloc] initWithInt:1];
[array addObject:number];
[number release];
number = nil;   //如果 release 后不及时置为 nil，则 number 成为悬浮指针，指向的内存未知
```

### autorelease

```objectivec
- (NSString *)stringValue
{
    NSString *str = [[NSString alloc] initWithFormat:@"Hello"];
    return str;
}
```
这种情况下，str 如果在方法内部 release，则调用者得到的一定是一个空对象；所以只能由调用者来负责释放

但是，这是十分不合理的，因为从方法名上看（不含`alloc/new/copy/mutableCopy`），调用者并不知道它需要负责释放该对象

所以此时，autorelease 就应运而生了

```objectivec
- (NSString *)stringValue
{
    NSString *str = [[NSString alloc] initWithFormat:@"Hello"];
    return [str autorelease];
}
```

str 对象会在其所在的释放池释放的时候被释放

如果外部需要 retain 该返回值，则需要这样做

```objectivec
NSString *str = [[self stringValue] retain];
// ...
[str release];
```

> autorelease 能延长对象生命周期，使对象在方法结束后依然存活一段时间

## 第30条：以ARC简化引用计数
### ARC 的本质是自动添加 release/retian/autorelease 等
```objectivec
+ (XYZ *)newXYZ
{
    XYZ *xyz = [[XYZ alloc] init];
    return xyz;
}

+ (XYZ *)createXYZ
{
    XYZ *xyz = [[XYZ alloc] init];
    /*ARC自动添加
    xyz = [xyz autorelease];
     */
    return xyz;
}

- (void)f
{
    XYZ *xyz1 = [XYZ newXYZ];
    XYZ *xyz2 = [XYZ createXYZ];
    /*ARC自动添加
    [xyz1 release];
     */
}
```

### 扩展阅读：[iOS开发ARC内存管理技术要点](http://www.cnblogs.com/flyFreeZn/p/4264220.html)

## done 第31条：在dealloc方法中只释放引用并解除监听 
## done 第32条：编写“异常安全代码”时留意内存管理问题 
```objc
@try {
 EOCSomeClass *object = [[EOCSomeClass alloc] init];
 [object doSomethingThatMayThrow];
 [object release];
}
@catch (...) {
 NSLog(@"Whoops, there was an error. Oh well...");
}
```

假如在执行 doSomethingThatMayThrow 方法中抛出异常，则 release 方法不会执行，会发生内存泄漏

解决方法：

```objc
EOCSomeClass *object;
@try {
 object = [[EOCSomeClass alloc] init];
 [object doSomethingThatMayThrow];}
@catch (...) {
 NSLog(@"Whoops, there was an error. Oh well...");
}
@finally {
 [object release];
}
```

同理，ARC 下也会发生这个问题

```objc
@try {
 EOCSomeClass *object = [[EOCSomeClass alloc] init];
 [object doSomethingThatMayThrow];
}
@catch (...) {
 NSLog(@"Whoops, there was an error. Oh well...");
}
```

可通过打开 -fobjc-arc-exceptions 标记来解决这个问题，不过这个标记会带来性能问题

总结：

1. 当捕获到异常,应该注意确保@try中创建的对象被清理完成.
2. ARC在默认情况下不会清理抛出异常时的代码,但是可以通过打开一个编译器标记来完成.不过会产生大量的代码和运行时的成本.


## done 第33条：以弱引用避免保留环 
## done 第34条：以“自动释放池块”降低内存峰值 

ARC下，可以使用 @autoreleasepool 来降低内存峰值

```objc
for (int i = 0; i < 9999; ++i)
{
    @autoreleasepool{
        A *a = [[A alloc] init];
        [self handle:a];
    }
}
```

a 是临时对象，handle 方法中也可能创建一些临时对象，ARC 下，这些临时对象可能没有及时 release 而是放到自动释放池里，那么此时使用 @autoreleasepool 就能及时回收这些临时对象，从而降低内存峰值

使用 enumerateObjectsUsingBlock 时，内部会自动添加一个 AutoreleasePool，而普通for循环和for in循环中没有
```objc
[array enumerateObjectsUsingBlock:^(id obj, NSUInteger idx, BOOL *stop) {
    // 这里被一个局部@autoreleasepool包围着
}];
```

另外，@autoreleasepool 跟是否 ARC 无关，MRC 下也可以使用

另外，关于降低内存峰值的之前也有学习过，见[Objective-C 内存管理](http://www.cnblogs.com/chenyg32/p/3859110.html)
## done 第35条：用“僵尸对象”调试内存管理问题 
僵尸对象是调试内存管理问题的最佳方式

被回收对象的内存可能会被系统回收，也可能不会，这样调试起来就很困难，此时可以使用僵尸对象来调试。

打开僵尸对象的方法：

Xcode -> Run -> Diagnostics -> Enable Zombie Objects
![](http://img.blog.csdn.net/20150803102818758)


僵尸对象的原理：

替换 dealloc 方法，创建一个僵尸对象替换回收对象，从而达到不释放回收对象的内存

原理代码：

```objc
// Obtain the class of the object being deallocated
Class cls = object_getClass(self);

// Get the class's name
const char *clsName = class_getName(cls);

// Prepend _NSZombie_ to the class name
const char *zombieClsName = @"_NSZombie_" + clsName;

// See if the specific zombie class exists
Class zombieCls = objc_lookUpClass(zombieClsName);

// If the specific zombie class doesn't exists,
// then it needs to be created

if(!zombieCls){
// Obtain the template  zombie class, where the new class's 
// name is the prepended string from above
   zombieCls = objc_duplicateClass(baseZombieCls,   
   zombieClsName,0);
}

// Perform normal destruction of the object being deallocated
objc_destructInstance(self);

// Set the class of the object being deallocated
// to the zombie class
objc_setClass(self, zombieCls) 

// The class of "self" is now _NSZombie_OriginalClass
```

## done 第36条：不要使用retainCount 
 
# 第6章 块与大中枢派发 
## done 第37条：理解“块”这一概念 

	在Objective-C语言中，一共有3种类型的block：
	_NSConcreteGlobalBlock 全局的静态block，不会访问任何外部变量。
	_NSConcreteStackBlock 保存在栈中的block，当函数返回时会被销毁。
	_NSConcreteMallocBlock 保存在堆中的block，当引用计数为0时会被销毁。

+ 全局 Block：_NSConcreteGlobalBlock

    + 定义在函数外面的 block 是全局静态的，没有访问任何外部变量
    + 定义在函数内部的 block，但是没有捕获任何自动变量，那么它也是全局的

	问题：那么定义在函数外部的，捕获变量的，是 global 吗？

	```objc
	void f()
	{
	    ^{ printf("Hello, World!\n"); } ();
	}
	```

+ 栈 Block：_NSConcreteStackBlock

	```objc
	void f()
	{
	    char a = 'A';
	    ^{ printf("%c\n",a); } ();
	}
	```

+ 堆 Block：_NSConcreteMallocBlock

	NSConcreteMallocBlock 类型的 block 通常不会在源码中直接出现，当一个栈 block 被 copy 的时候，才会将这个 block 复制到堆中

	```objc
	void f()
	{
	    char a = 'A';
	    void (^block)() = [^{ printf("%c\n",a); } copy];
	}
	```

		对全局 Block 进行 copy 后，什么事也不会发生
		对栈 Block 进行 copy 后，会得到一个堆 Block
		对堆 Block 进行 copy 后，其引用计数会加1

+ 例子

	```objc
	void (^blcok)();
	if (1)
	{
	    block = ^{
	        NSLog(@"Hello");
	    }
	}
	block();
```

	block执行时，其内存可能已经被释放，因为它是一个栈 block，if 体结束时可能会被释放

	正确做法是

	```objc
	void (^blcok)();
	if (1)
	{
	    block = [^{
	        NSLog(@"Hello");
	    } copy];
	}
	block();
	```

+ 更多细节见[《谈Objective-C block的实现》](http://blog.devtang.com/2013/07/28/a-look-inside-blocks/)

## done 第38条：为常用的块类型创建typedef 
## done 第39条：用handler块降低代码分散程度 
## 第40条：用块引用其所属对象时不要出现保留环 
例子1

```objc
// EOCNetworkFetcher.h

#import <Foundation/Foundation.h>

typedef void(^EOCNetworkFetcherCompletionHandler)(NSData *data);

@interface EOCNetworkFetcher : NSObject

@property (nonatomic, strong, readonly) NSURL *url;

- (id)initWithURL:(NSURL*)url;

- (void)startWithCompletionHandler:(EOCNetworkFetcherCompletionHandler)completion;

@end
```

```objc
// EOCNetworkFetcher.m
#import "EOCNetworkFetcher.h"

@interface EOCNetworkFetcher ()
@property (nonatomic, strong, readwrite) NSURL *url;
@property (nonatomic, copy) EOCNetworkFetcherCompletionHandler completionHandler;
@property (nonatomic, strong) NSData *downloadedData;
@end


@implementation EOCNetworkFetcher

- (id)initWithURL:(NSURL*)url
{
		if ((self = [super init])) {
				_url = url;
		}
		return self;
}

- (void)startWithCompletionHandler:(EOCNetworkFetcherCompletionHandler)completion
{
		self.completionHandler = completion;
		// Start the request
		// Request sets downloadedData property
		// When request is finished, p_requestCompleted is called
}

- (void)p_requestCompleted {
		if (_completionHandler) {
				_completionHandler(_downloadedData);
		}
}

@end
```

```objc
@implementation EOCClass
{
    EOCNetworkFetcher* _networkFetcher;
    NSData* _fetchedData;
}

- (void)downloadData
{
    NSURL* url = [[NSURL alloc] initWithString:@"http://www.example.com/something.dat"];
		
    _networkFetcher = [[EOCNetworkFetcher alloc] initWithURL:url];

		[_networkFetcher startWithCompletionHandler:^(NSData *data){

				NSLog(@"Request URL %@ finished", _networkFetcher.url);
				_fetchedData = data;

		}];
}
@end
```

EoCClass -> networkFetcher -> block -> self(通过_fetchedData)

例子2

将 networkFetcher 变为局部变量，修改如下：

```objc
- (void)downloadData {
 NSURL *url = [[NSURL alloc] initWithString:
 @"http://www.example.com/something.dat"];
 EOCNetworkFetcher *networkFetcher =
 [[EOCNetworkFetcher alloc] initWithURL:url];
 [networkFetcher startWithCompletionHandler:^(NSData *data){
 NSLog(@"Request URL %@ finished", networkFetcher.url);
 _fetchedData = data;
 }];
}
```

networkFetcher -> block -> networkFetcher(通过url)

## 第41条：多用派发队列，少用同步锁
 
## 第42条：多用GCD，少用performSelector系列方法
### 如何延迟执行一个方法
```objc
// 方法1：使用 performSelector
[self performSelector:@selector(foo) withObject:nil afterDelay:5.0];

// 方法2：使用 dispatch_after
dispatch_after(dispatch_time(DISPATCH_TIME_NOW, (int64_t)(5.0 * NSEC_PER_SEC)), dispatch_get_main_queue(), ^{
    [self foo];
});
```
使用 dispatch_after 比使用 performSelector 更好，因为 performSelector 可能引起内存问题

当然，如果需要取消定时任务，则只能使用 performSelector，dispatch_after 无法取消


### 如何让一个方法在主线程执行
```objc
// 方法1：使用 performSelector
[self performSelectorOnMainThread:@selector(foo) withObject:nil waitUntilDone:NO];

// 方法2：使用 dispatch_after
dispatch_async(dispatch_get_main_queue(), ^{
    [self foo];
});
```
使用 dispatch_after 比使用 performSelector 更好，因为 performSelector 可能引起内存问题
 
## 第43条：掌握GCD及操作队列的使用时机
要知道有个东西叫做 NSOperationQueue 就行了
## 第44条：通过Dispatch Group机制，根据系统资源状况来执行任务 
## 第45条：使用dispatch_once来执行只需运行一次的线程安全代码
以后只要遇到“只需要执行一次的（线程安全）代码”，就应该想到 dispatch_once

比如单例的书写方式
```objc
+ (instancetype)sharedInstance
{
    static id sharedInstance = nil;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        sharedInstance = [[self alloc] init];
    });
    return sharedInstance;
}
```

 
## 第46条：不要使用`dispatch_get_current_queue`
尽量别用，该接口已废弃
 
# 第7章 系统框架 
## 第47条：熟悉系统框架
+ CFNetWork:网络接口，Foundation 框架将其部分内容封装为 Objective-C 接口（C语言）
+ CoreAudio:音频处理 API（C语言）
+ AVFoundation:视频处理接口（Objective-C）
+ CoreData:数据库接口（Objective-C）
+ CoreText:文字渲染排版接口（C语言）
 
## done 第48条：多用块枚举，少用for循环

## 第49条：对自定义其内存管理语义的collection使用无缝桥接 
### 使用无缝桥接技术，转换 Foundation 框架的 Objective-C 对象和 CoreFoundation 框架的 C 语言数据结构
```objc
NSArray *array = @[@1, @2, @3];
CFArrayRef cfArray = (__bridge CFArrayRef)array;
NSLog(@"%@ count: %li", cfArray, CFArrayGetCount(cfArray));
```
+ NSArray 在 CoreFoundation 框架对应的数据结构是 CFArray，但是只能通过 CFArrayRef 指针来操纵 CFArray
+ CFArrayGetCount 是 CoreFoundation 框架里获取数组大小的函数

### 桥式转换
+ `__bridge`：只做类型转换，不修改对象（内存）管理权；
+ `__bridge_retained`：将 Objective-C 的对象转换为 CoreFoundation 的对象，同时 ARC 交出对象（内存）的管理权，后续需要使用 CFRelease 或者相关方法来释放对象；
+ `__bridge_transfer`：将 CoreFoundation 的对象转换为Objective-C的对象，同时将对象（内存）的管理权交给 ARC

```objc
NSArray *array = @[@1, @2, @3];
CFArrayRef cfArray = (__bridge_retained CFArrayRef)array;
CFRelease(cfArray);  // 因为是 __bridge_retained，所以需要调用 CFRelease
```
```objc
NSArray *array = @[@1, @2, @3];
CFArrayRef cfArray = (__bridge_retained CFArrayRef)array;
NSArray *array2 = (__bridge_transfer NSArray *)cfArray;
//CFRelease(cfArray);  // 不需要 CFRelease，因为对象内存已经归 ARC 管理
```

### 使用无缝桥接修改 Collection 的内存管理语义
NSMutableDictionary 加入键值对的时候，字典会自动“拷贝”键并“保留”值，如果键的对象不支持拷贝操作（没有实现 NSCopying 协议）呢？就会出现 Runtime Error

关于拷贝协议可以查看：[浅析Objective-C的copy](http://www.cnblogs.com/chenyg32/p/5167194.html)

无缝桥接可以从 CoreFoundation 层创建一个不拷贝键的字典

创建函数

```objc
CFMutableDictionaryRef CFDictionaryCreateMutable(
    CFAllocatorRef allocator,  // 一般传NULL，采用系统默认的内存分配器
    CFIndex capacity,          // 初始大小，并非最大容量
    const CFDictionaryKeyCallBacks *keyCallBacks,    // 回调
    const CFDictionaryValueCallBacks *valueCallBacks // 回调
);
```

键值回调

```objc
typedef struct {
    CFIndex				version;    //一般为0
    CFDictionaryRetainCallBack		retain; //遇到retain的回调
    CFDictionaryReleaseCallBack		release;//遇到release的回调
    CFDictionaryCopyDescriptionCallBack	copyDescription;//一般传NULL，采用系统默认
    CFDictionaryEqualCallBack		equal;  //一般传CFEqual
    CFDictionaryHashCallBack		hash;   //一般传CFHash
} CFDictionaryKeyCallBacks;

typedef struct {
    CFIndex				version;    //一般为0
    CFDictionaryRetainCallBack		retain; //遇到retain的回调
    CFDictionaryReleaseCallBack		release;//遇到release的回调
    CFDictionaryCopyDescriptionCallBack	copyDescription;    //一般传NULL，采用系统默认
    CFDictionaryEqualCallBack		equal;  //一般传CFEqual
} CFDictionaryValueCallBacks;
```

创建“保留”键，“保留”值的 NSDictionary

```objc
const void* EOCRetainCallback (CFAllocatorRef allocator , const void *value)
{
    return CFRetain(value);
}

void EOCReleaseCallback(CFAllocatorRef allocator , const void *value)
{
    CFRelease(value);
}

CFDictionaryKeyCallBacks keyCallbacks = 
{
    0,
    EOCRetainCallback,
    EOCReleaseCallback,
    NULL,
    CFEqual,
    CFHash
};

CFDictionaryValueCallBacks valueCallbacks = 
{
    0,
    EOCRetainCallback,
    EOCReleaseCallback,
    NULL,
    CFEqual,
};
    
CFMutableDictionaryRef aCFDictionary = CFDictionaryCreateMutable(NULL, 0, &keyCallbacks, &valueCallbacks);
NSMutableDictionary *anNSdictionary = (__bridge_transfer NSMutableDictionary *)aCFDictionary;
```

## 第50条：构建缓存时选用NSCache而非NSDictionary 
+ 实现缓存时应选用 NSCache 而非 NSDictionary
+ 可以给 NSCache 设置缓存数量上限 countLimit 或缓存总和 totalCostLimit（单位 bytes），超过限制的时候系统会自动剔除部分缓存数据
+ NSCache 收到系统低内存警告的时候会被系统自动删除，且是线程安全的（多线程环境下不需要对 NSCache 加锁）
+ NSCache 不会像 NSDictionary 那样，拷贝对象（只会 retain，不会新建一个）
+ 使用 NSPurgeableData 作为 NSCache 的缓存时，系统收到低内存警告的时候，NSPurgeableData 对象所在内存会被系统释放，此时 NSCache 也会将其自动移除

扩展阅读：[利用NSCache提升效率](https://www.ganlvji.com/nscache/)

## 第51条：精简initialize与load的实现代码
参见：[iOS 的 initialize 和 load 区别](https://norcy.github.io/wiki/iOS/iOS%20%E7%9A%84%20initialize%20%E5%92%8C%20load%20%E5%8C%BA%E5%88%AB/)
## 第52条：别忘了NSTimer会保留其目标对象
参见：[NSTimer 会保留目标对象](http://norcy.github.io/2016/06/20/NSTimer%20%E4%BC%9A%E4%BF%9D%E7%95%99%E7%9B%AE%E6%A0%87%E5%AF%B9%E8%B1%A1/)