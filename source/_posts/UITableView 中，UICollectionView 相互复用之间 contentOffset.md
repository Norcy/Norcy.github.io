---
title: UITableView 中，UICollectionView 相互复用之间 contentOffset
date: 2016-03-28
categories:
- iOS
photos: images/view.jpg
keywords: UITableView;UITableViewCell;UICollectionView;contentOffset;复用;reuse
---

# 问题描述
UIViewController 中有一个 UITableView，UITableViewCell 的 contentView 上添加了横滑列表，横滑列表是用 UICollectionView 实现的。
如下图所示

![](http://image.norcy.xyz/contentOffset1.png)

抽象出来就是这样

![](http://image.norcy.xyz/contentOffset2.png)


其中 UITableView 的 DataSource/Delegate 是 Controller，而 UICollectionView 的 DataSource/Delegate 是 UITableViewCell。
UITableView 的 DataSource 抽象如下：

	- (UITableViewCell *)tableView:(UITableView *)tableView cellForRowAtIndexPath:(NSIndexPath *)indexPath 
	{
		JceObject *cellObj = [_dataModel.aryItems objectAtIndex:indexPath.row];
		UITableViewCell *cell = [QLThumbsMgr makeCellWithJCEPoster:cellObj tableView:tableView userInfo:self];
		return cell;
	}

好像看似没什么问题是吧，UITableView 的使用一向都是这样的嘛。可是当 UITableViewCell 碰上了 UICollectionView，问题就出来了。
左右滑动一个 UICollectionView 使其 contentOffset 不为初始值，再上下滑动 UITableView，你会发现，其他的横滑列表也被横滑了，上个动图直观感受一下

![](http://image.norcy.xyz/contentOffset3.gif)

# 问题分析
如果对于 UITableView 的 Cell 复用机制有一定了解的同学一定很容易看出问题，就是因为 Cell 之间的复用导致了 UICollectionView 的 contentOffset 也被复用了。

那么之前我们是如何解决 UITableViewCell 的复用问题呢？就是每次 Cell 出现的时候，就根据数据源更新 Cell 的内容，这样就保证了每次看到的 Cell 是正确的。

但是现在棘手的是数据源中并没有包含 UICollectionView 的 contentOffset。

问题可以转化为如何在 UITableViewCell 出现的时候，更新其 UICollectionView 的 contentOffset。依赖 UITableViewCell 去记住是行不通的，因为它自己就是被复用的对象，那么就要外部去帮它记住，这个外部可以是 UITableView 的 Delegate——UIViewController，也可以 UITableViewCell 的数据源。

如果是数据源，则需要对数据源做一个扩展 or 分类，由于数据源与前后台协议是相关的，改动数据源或许不是一个好的选择。所以这里我选择了让 UIViewController 去完成这个记忆的任务。

# 解决方法
我们可以为 UIViewController 添加一个 NSMutableDictionary 类型的实例变量，该字典存储的是 UITableViewCell 的位置和其 UICollectionView 的横滑位置的映射关系。

+ UITableViewCell 即将从视野里消失的时候，UIViewController 用 NSMutableDictionary 记录该 Cell 的 indexPath.row 和其 UICollectionView 的 contentOffset；（这里只讨论 UITableView 只有一个 section 的情况，多个 section 的处理原理是一样的）

+ UITableViewCell 即将出现在视野里的时候，UIViewController 根据该 Cell 的 indexPath.row，从 NSMutableDictionary 中读取相应的值去设置该 Cell 上的 UICollectionView 的 contentOffset；

UIViewController 是 UITableView 的 Delegate，UITableViewCell 的出现和消失事件可以在以下2个代理方法中捕捉到。
`- (void)tableView:(UITableView *)tableView willDisplayCell:(UITableViewCell *)cell forRowAtIndexPath:(NSIndexPath *)indexPath;`
和
`- (void)tableView:(UITableView *)tableView didEndDisplayingCell:(UITableViewCell *)cell forRowAtIndexPath:(NSIndexPath*)indexPath;`

那么，UIViewController 中的代码应该类似这样。


	- (void)tableView:(UITableView *)tableView willDisplayCell:(UITableViewCell *)cell forRowAtIndexPath:(NSIndexPath *)indexPath
	{
	    if ([cell isKindOfClass:[QLONAListCell class]])
		{
	        QLONAListCell *listCell = (QLONAListCell *)cell;
	        NSInteger row = indexPath.row;
	        CGFloat horizontalOffset;
	        horizontalOffset = [self.contentOffsetDict[[@(row) stringValue]] floatValue];
	        [listCell.horizontalScrollView setContentOffset:CGPointMake(horizontalOffset, 0)];
	    }
	}
	
	- (void)tableView:(UITableView *)tableView didEndDisplayingCell:(UITableViewCell *)cell forRowAtIndexPath:(NSIndexPath *)indexPath
	{
	    if ([cell isKindOfClass:[QLONAListCell class]])
	    {
	        QLONAListCell *listCell = (QLONAListCell *)cell;
	        NSInteger row = indexPath.row;
	        CGFloat horizontalOffset = listCell.horizontalScrollView.contentOffset.x;
	        self.contentOffsetDict[[@(row) stringValue]] = @(horizontalOffset);
	    }
	}

其中 QLONAListCell 是 UITableViewCell 的子类，它有一个 UICollectionView 类型的属性 horizontalScrollView。
contentOffsetDict 是 UIViewController 的实例变量，它是一个 NSMutableDictionary。

哦，还有一个注意点。当对 UITableView 进行下拉刷新的时候，新数据可能与老数据不一样（比如多了某个 Cell 或少了某个 Cell），那么这种情况下，contentOffsetDict 的记录就不再正确，所以每次在数据请求回来的时候，最好清空一下 contentOffsetDict。这样做的后果就是每次下拉刷新就会清空横滑列表的 contentOffset，不过看起来也似乎合情合理。

# 参考链接
[Putting a UICollectionView in a UITableViewCell](https://ashfurrow.com/blog/putting-a-uicollectionview-in-a-uitableviewcell/)