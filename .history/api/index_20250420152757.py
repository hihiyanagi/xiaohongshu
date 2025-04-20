from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from typing import List, Optional
import sys

# Add the parent directory to sys.path to be able to import youtube_api module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from youtube_api import YouTubeAPI

app = FastAPI(title="YouTube API", description="API for retrieving YouTube video information")

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create a dependency for the YouTube API
def get_youtube_api():
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="YouTube API key is not configured")
    
    return YouTubeAPI(api_key)

@app.get("/")
def read_root():
    return {"message": "Welcome to the YouTube API", "version": "1.0.0"}

@app.get("/search")
def search_videos(
    query: str = Query(..., description="Search query"),
    max_results: int = Query(5, description="Maximum number of results to return", ge=1, le=50),
    language: str = Query("zh-CN", description="Language preference for search results"),
    youtube_api: YouTubeAPI = Depends(get_youtube_api)
):
    """
    Search for videos on YouTube based on a query.
    
    Returns detailed information about the videos matching the search query.
    """
    results = youtube_api.search_videos(query, max_results, language)
    
    if not results:
        return {"results": [], "message": "No videos found for the given query"}
    
    return {"results": results, "count": len(results)}

@app.get("/videos/{video_id}")
def get_video_info(
    video_id: str,
    youtube_api: YouTubeAPI = Depends(get_youtube_api)
):
    """
    Get detailed information about a specific YouTube video by its ID.
    """
    results = youtube_api.get_videos_info([video_id])
    
    if not results:
        raise HTTPException(status_code=404, detail=f"Video with ID {video_id} not found")
    
    return results[0]

@app.get("/videos")
def get_videos_info(
    video_ids: str = Query(..., description="Comma-separated list of video IDs"),
    youtube_api: YouTubeAPI = Depends(get_youtube_api)
):
    """
    Get detailed information about multiple YouTube videos by their IDs.
    
    Provide video_ids as a comma-separated list of YouTube video IDs.
    """
    ids_list = [vid.strip() for vid in video_ids.split(",")]
    
    if not ids_list:
        raise HTTPException(status_code=400, detail="No video IDs provided")
    
    results = youtube_api.get_videos_info(ids_list)
    
    if not results:
        return {"results": [], "message": "No videos found for the given IDs"}
    
    return {"results": results, "count": len(results)}

@app.get("/channels/{channel_id}")
def get_channel_info(
    channel_id: str,
    youtube_api: YouTubeAPI = Depends(get_youtube_api)
):
    """
    Get detailed information about a YouTube channel by its ID.
    """
    channel_info = youtube_api.get_channel_info(channel_id)
    
    if not channel_info:
        raise HTTPException(status_code=404, detail=f"Channel with ID {channel_id} not found")
    
    return channel_info

@app.get("/videos/{video_id}/comments")
def get_video_comments(
    video_id: str,
    max_results: int = Query(10, description="Maximum number of comments to return", ge=1, le=100),
    youtube_api: YouTubeAPI = Depends(get_youtube_api)
):
    """
    Get comments for a specific YouTube video by its ID.
    """
    comments = youtube_api.get_video_comments(video_id, max_results)
    
    if not comments:
        return {"results": [], "message": f"No comments found for video with ID {video_id}"}
    
    return {"results": comments, "count": len(comments)}

# This is used when running the app locally with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("index:app", host="0.0.0.0", port=8000, reload=True) 