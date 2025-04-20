# YouTube API 使用指南

这个指南将帮助你使用 YouTube API 脚本获取视频信息。

## 准备工作

1. **获取 YouTube API 密钥**
   
   要使用 YouTube API，你需要先创建一个 Google Cloud 项目并获取 API 密钥：
   
   1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
   2. 创建一个新项目
   3. 在左侧导航栏中，点击「API 和服务」>「库」
   4. 搜索并启用「YouTube Data API v3」
   5. 点击「创建凭据」并选择「API 密钥」
   6. 复制生成的 API 密钥

2. **安装所需的依赖**
   
   ```bash
   pip install -r requirements.txt
   ```

## 使用脚本

本项目包含两个主要脚本：

1. `youtube_api.py` - YouTube API 的核心功能库
2. `youtube_examples.py` - 提供更友好的用户界面和示例

### 使用方法

你可以通过以下两种方式提供 API 密钥：

1. **作为命令行参数**:
   ```bash
   python youtube_examples.py YOUR_API_KEY
   ```

2. **设置环境变量**:
   ```bash
   # 在 Linux/Mac 上
   export YOUTUBE_API_KEY=YOUR_API_KEY
   
   # 在 Windows 上
   set YOUTUBE_API_KEY=YOUR_API_KEY
   ```
   然后直接运行:
   ```bash
   python youtube_examples.py
   ```

### 示例脚本功能

`youtube_examples.py` 提供了一个交互式菜单，可以执行以下操作：

1. **搜索视频**
   - 输入搜索关键词和想要返回的结果数量
   - 显示视频标题、频道名称、发布日期、观看次数和点赞数

2. **获取视频详细信息**
   - 通过视频 ID 获取单个视频的详细信息
   - 显示视频标题、频道、发布日期、时长、观看次数、点赞数、评论数和描述

3. **获取频道信息**
   - 通过频道 ID 获取频道的详细信息
   - 显示频道名称、描述、订阅数、视频数、总观看次数和创建日期

4. **获取视频评论**
   - 通过视频 ID 获取视频评论
   - 显示评论作者、发布日期、点赞数和内容

5. **保存结果到 JSON 文件**
   - 将上一次操作的结果保存到 JSON 文件中
   - 可以指定文件名或使用默认名称（基于时间戳）

## 直接使用 API 库

如果你想在自己的项目中使用 YouTube API 功能，你可以直接导入 `YouTubeAPI` 类：

```python
from youtube_api import YouTubeAPI

# 创建 API 客户端
youtube = YouTubeAPI("YOUR_API_KEY")

# 搜索视频
results = youtube.search_videos("搜索关键词", max_results=5)

# 获取特定视频的信息
video_info = youtube.get_videos_info(["VIDEO_ID"])

# 获取频道信息
channel_info = youtube.get_channel_info("CHANNEL_ID")

# 获取视频评论
comments = youtube.get_video_comments("VIDEO_ID", max_results=10)
```

## 常见问题

### 1. API 配额限制

YouTube API 有每日配额限制。基本配额是每天 10,000 个单位，不同操作消耗不同数量的单位：

- 搜索操作: 100 单位
- 视频/频道/评论获取: 1 单位

如果遇到错误消息提示超出配额，你需要等到第二天再继续使用。

### 2. 找不到视频 ID 怎么办？

在 YouTube 视频 URL 中，`v` 参数就是视频 ID。例如，在 URL `https://www.youtube.com/watch?v=dQw4w9WgXcQ` 中，视频 ID 是 `dQw4w9WgXcQ`。

### 3. 找不到频道 ID 怎么办？

频道 ID 通常以 `UC` 开头。你可以通过在频道页面上点击「关于」标签，然后查看页面源代码来找到它，或者使用我们的搜索功能先找到该频道的视频，然后从视频信息中获取频道 ID。 