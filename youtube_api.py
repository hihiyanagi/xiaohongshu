#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YouTube API Script
-----------------
This script uses the YouTube Data API v3 to retrieve video information.
Before running, you need to:
1. Create a project in Google Cloud Console
2. Enable the YouTube Data API v3
3. Create an API key
4. Set the API key in this script or as an environment variable

For detailed instructions on getting an API key, visit:
https://developers.google.com/youtube/v3/getting-started
"""

import os
import sys
import requests
import json
from typing import Dict, List, Any, Optional

class YouTubeAPI:
    """A class to interact with the YouTube Data API v3."""

    BASE_URL = "https://www.googleapis.com/youtube/v3/"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the YouTube API client.

        Args:
            api_key: Your YouTube Data API key. If not provided, will try to get it from 
                     the YOUTUBE_API_KEY environment variable.
        """
        self.api_key = api_key or os.environ.get("YOUTUBE_API_KEY")
        
        if not self.api_key:
            print("Error: API key is required. Please provide it in the constructor or set the YOUTUBE_API_KEY environment variable.")
            sys.exit(1)

    def search_videos(self, query: str, max_results: int = 5, language: str = "zh-CN") -> List[Dict[str, Any]]:
        """
        Search for videos based on a query.

        Args:
            query: The search query
            max_results: Maximum number of results to return (default: 5)
            language: The language preference for search results (default: zh-CN for Chinese)

        Returns:
            A list of video information dictionaries
        """
        search_url = f"{self.BASE_URL}search"
        params = {
            "key": self.api_key,
            "part": "snippet",
            "q": query,
            "maxResults": max_results,
            "type": "video",
            "relevanceLanguage": language,
        }

        try:
            response = requests.get(search_url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            search_results = response.json()
            
            # Extract the video IDs
            video_ids = [item["id"]["videoId"] for item in search_results.get("items", [])]
            
            # If there are no results, return an empty list
            if not video_ids:
                return []
                
            # Get detailed information for each video
            return self.get_videos_info(video_ids)
                
        except requests.exceptions.RequestException as e:
            print(f"Error making search request: {e}")
            return []

    def get_videos_info(self, video_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Get detailed information for specific videos by their IDs.

        Args:
            video_ids: A list of YouTube video IDs

        Returns:
            A list of video information dictionaries
        """
        if not video_ids:
            return []
            
        videos_url = f"{self.BASE_URL}videos"
        params = {
            "key": self.api_key,
            "part": "snippet,contentDetails,statistics",
            "id": ",".join(video_ids)
        }

        try:
            response = requests.get(videos_url, params=params)
            response.raise_for_status()
            videos_data = response.json()
            
            return videos_data.get("items", [])
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting video details: {e}")
            return []

    def get_channel_info(self, channel_id: str) -> Dict[str, Any]:
        """
        Get information about a YouTube channel.

        Args:
            channel_id: The YouTube channel ID

        Returns:
            A dictionary with channel information
        """
        channels_url = f"{self.BASE_URL}channels"
        params = {
            "key": self.api_key,
            "part": "snippet,contentDetails,statistics",
            "id": channel_id
        }

        try:
            response = requests.get(channels_url, params=params)
            response.raise_for_status()
            channel_data = response.json()
            
            if channel_data.get("items"):
                return channel_data["items"][0]
            return {}
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting channel details: {e}")
            return {}

    def get_video_comments(self, video_id: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Get comments for a specific video.

        Args:
            video_id: The YouTube video ID
            max_results: Maximum number of comments to return (default: 10)

        Returns:
            A list of comment dictionaries
        """
        comments_url = f"{self.BASE_URL}commentThreads"
        params = {
            "key": self.api_key,
            "part": "snippet",
            "videoId": video_id,
            "maxResults": max_results,
        }

        try:
            response = requests.get(comments_url, params=params)
            response.raise_for_status()
            comments_data = response.json()
            
            return comments_data.get("items", [])
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting video comments: {e}")
            return []

# Example usage
if __name__ == "__main__":
    # Replace with your actual API key or set the YOUTUBE_API_KEY environment variable
    API_KEY = ""  # Your API key here
    
    # Check if API key is provided as command line argument
    if len(sys.argv) > 1:
        API_KEY = sys.argv[1]
    
    youtube = YouTubeAPI(API_KEY)
    
    # Example: Search for videos
    query = input("Enter search query: ")
    results = youtube.search_videos(query, max_results=5)
    
    # Print the results
    if results:
        print("\nSearch Results:")
        for i, video in enumerate(results, 1):
            snippet = video.get("snippet", {})
            statistics = video.get("statistics", {})
            
            print(f"\n{i}. {snippet.get('title')}")
            print(f"   Channel: {snippet.get('channelTitle')}")
            print(f"   Description: {snippet.get('description')[:100]}...")
            print(f"   Published: {snippet.get('publishedAt')}")
            print(f"   Views: {statistics.get('viewCount', 'N/A')}")
            print(f"   Likes: {statistics.get('likeCount', 'N/A')}")
            print(f"   Video ID: {video.get('id')}")
    else:
        print("No results found or an error occurred.") 