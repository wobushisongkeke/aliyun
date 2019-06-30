# m3u8（ts）视频爬取
本项目为视频网站m3u8格式文件爬取，包括ts文件下载，解密和合并。为教学讲解用使用阿里云课堂视频作为示例，仅做技术讲解用，不涉及和教唆任何非法获取数据，非法使用数据，和非法占有数据的行为。对于没有经过授权的数据爬取行为都是违规的！对于任何个人，团体或者机构，使用该技术从事任何违法违规行为的，自担风险。

## 使用方法
将本项目下载到本地。

修改主函数中`url`，`cookie`，`referer`，`user_agent`，`save_path`，`ts_path`和`result_path`几项内容。
其中`url`为一级m3u8内容中的二级m3u8文件的url。`cookie`，`referer`和`user_agent`即为获取的一级m3u8文件的cookie，referer以及user agent。`save_path`，`ts_path`和`result_path`分别为ts文件下载地址，解密后的ts文件地址，以及合并后的ts文件地址。

## 学习资料
以下是几篇有用的文章，希望能帮助大家理解和运用代码：

[M3U8流视频数据爬虫详解一：M3U8视频文件详解](https://blog.csdn.net/wobushisongkeke/article/details/93378861)

[M3U8流视频数据爬虫详解二：M3U8视频网络数据分析与爬虫设计](https://blog.csdn.net/wobushisongkeke/article/details/94159705)

[M3U8流视频数据爬虫详解三：M3U8视频网络数据爬虫实现](https://blog.csdn.net/wobushisongkeke/article/details/94161956)

## 关于我们
作者为研二程序媛一枚，在爬虫方面也还是一个新手，如有不足之处请见谅。如果大家对本项目有任何建议，想法或者问题，欢迎交流和探讨。