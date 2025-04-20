#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YouTube API Examples
-------------------
This script demonstrates various use cases for the YouTube API.

Examples include:
1. Searching for videos
2. Getting detailed video information
3. Getting channel information
4. Getting video comments
5. Saving results to a JSON file

Usage:
    python youtube_examples.py [API_KEY]
"""

import os
import sys
import json
from datetime import datetime
from youtube_api import YouTubeAPI

def save_to_json(data, filename=None):
    """
    Save data to a JSON file.
    
    Args:
        data: The data to save
        filename: The filename to save to (default: based on current timestamp)
    
    Returns:
        The path to the saved file
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"youtube_results_{timestamp}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return filename

def search_and_display_videos(youtube, query, max_results=5):
    """
    Search for videos and display the results.
    
    Args:
        youtube: The YouTubeAPI instance
        query: The search query
        max_results: Maximum number of results to return
    
    Returns:
        The results from the API
    """
    print(f"\n正在搜索 '{query}' 相关的视频...")
    results = youtube.search_videos(query, max_results=max_results)
    
    if results:
        print(f"\n找到 {len(results)} 个结果:")
        for i, video in enumerate(results, 1):
            snippet = video.get("snippet", {})
            statistics = video.get("statistics", {})
            
            print(f"\n{i}. {snippet.get('title')}")
            print(f"   频道: {snippet.get('channelTitle')}")
            print(f"   发布日期: {snippet.get('publishedAt')}")
            print(f"   观看次数: {statistics.get('viewCount', 'N/A')}")
            print(f"   点赞数: {statistics.get('likeCount', 'N/A')}")
    else:
        print("未找到结果或发生错误。")
    
    return results

def get_and_display_video_details(youtube, video_id):
    """
    Get and display detailed information for a specific video.
    
    Args:
        youtube: The YouTubeAPI instance
        video_id: The YouTube video ID
    
    Returns:
        The video information
    """
    print(f"\n获取视频 ID '{video_id}' 的详细信息...")
    results = youtube.get_videos_info([video_id])
    
    if results:
        video = results[0]
        snippet = video.get("snippet", {})
        statistics = video.get("statistics", {})
        content_details = video.get("contentDetails", {})
        
        print("\n视频详细信息:")
        print(f"标题: {snippet.get('title')}")
        print(f"频道: {snippet.get('channelTitle')}")
        print(f"发布日期: {snippet.get('publishedAt')}")
        print(f"视频时长: {content_details.get('duration')}")
        print(f"观看次数: {statistics.get('viewCount', 'N/A')}")
        print(f"点赞数: {statistics.get('likeCount', 'N/A')}")
        print(f"评论数: {statistics.get('commentCount', 'N/A')}")
        print(f"描述: \n{snippet.get('description')}")
        return video
    else:
        print("未找到视频或发生错误。")
        return None

def get_and_display_channel_info(youtube, channel_id):
    """
    Get and display information about a YouTube channel.
    
    Args:
        youtube: The YouTubeAPI instance
        channel_id: The YouTube channel ID
    
    Returns:
        The channel information
    """
    print(f"\n获取频道 ID '{channel_id}' 的信息...")
    channel_info = youtube.get_channel_info(channel_id)
    
    if channel_info:
        snippet = channel_info.get("snippet", {})
        statistics = channel_info.get("statistics", {})
        
        print("\n频道信息:")
        print(f"名称: {snippet.get('title')}")
        print(f"描述: {snippet.get('description', '')[:100]}...")
        print(f"订阅数: {statistics.get('subscriberCount', 'N/A')}")
        print(f"视频数: {statistics.get('videoCount', 'N/A')}")
        print(f"总观看次数: {statistics.get('viewCount', 'N/A')}")
        print(f"创建日期: {snippet.get('publishedAt')}")
        return channel_info
    else:
        print("未找到频道或发生错误。")
        return None

def get_and_display_video_comments(youtube, video_id, max_results=10):
    """
    Get and display comments for a specific video.
    
    Args:
        youtube: The YouTubeAPI instance
        video_id: The YouTube video ID
        max_results: Maximum number of comments to return
    
    Returns:
        The comments data
    """
    print(f"\n获取视频 ID '{video_id}' 的评论...")
    comments = youtube.get_video_comments(video_id, max_results=max_results)
    
    if comments:
        print(f"\n找到 {len(comments)} 条评论:")
        for i, comment_thread in enumerate(comments, 1):
            comment = comment_thread.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
            print(f"\n{i}. 作者: {comment.get('authorDisplayName')}")
            print(f"   日期: {comment.get('publishedAt')}")
            print(f"   点赞数: {comment.get('likeCount', 0)}")
            print(f"   评论内容: {comment.get('textDisplay')}")
        return comments
    else:
        print("未找到评论或发生错误。")
        return None

def main():
    # Get API key from command line argument or environment variable
    api_key = None
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    
    # Create YouTube API client
    youtube = YouTubeAPI(api_key)
    
    while True:
        print("\n============ YouTube API 示例 ============")
        print("1. 搜索视频")
        print("2. 获取视频详细信息")
        print("3. 获取频道信息")
        print("4. 获取视频评论")
        print("5. 保存上一次的结果到 JSON 文件")
        print("0. 退出")
        
        choice = input("\n请选择一个选项 (0-5): ")
        
        # Variables to store the last results
        last_results = None
        
        if choice == "1":
            query = input("请输入搜索关键词: ")
            max_results = int(input("请输入返回结果数量 (1-50): ") or "5")
            last_results = search_and_display_videos(youtube, query, max_results)
            
        elif choice == "2":
            video_id = input("请输入视频 ID: ")
            last_results = get_and_display_video_details(youtube, video_id)
            
        elif choice == "3":
            channel_id = input("请输入频道 ID: ")
            last_results = get_and_display_channel_info(youtube, channel_id)
            
        elif choice == "4":
            video_id = input("请输入视频 ID: ")
            max_comments = int(input("请输入返回评论数量 (1-100): ") or "10")
            last_results = get_and_display_video_comments(youtube, video_id, max_comments)
            
        elif choice == "5":
            if last_results:
                filename = input("请输入文件名 (留空使用默认名称): ")
                saved_file = save_to_json(last_results, filename or None)
                print(f"结果已保存到: {saved_file}")
            else:
                print("没有结果可保存。请先执行一个操作。")
            
        elif choice == "0":
            print("退出程序。")
            break
            
        else:
            print("无效选择，请重试。")
        
        input("\n按 Enter 键继续...")

if __name__ == "__main__":
    main() 