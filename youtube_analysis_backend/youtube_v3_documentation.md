# YouTube Data API v3 – End-to-End Guide for Channel Analysis (AI-Readable)

## Purpose

This document defines how to use the **YouTube Data API v3** to analyze a public YouTube channel.

The system workflow is:
- User submits a YouTube channel link
- Backend fetches public channel and video data using YouTube Data API v3
- Video content is analyzed by an AI model (Gemini / Claude)
- A channel-level summary is generated
- Results are stored in a database and cache

This guide is intended for **backend systems and AI agents**, not frontend applications.

---

## Authentication

### API Used
- YouTube Data API v3

### Authentication Method
- **API Key only**

OAuth is NOT required because:
- Only public data is accessed
- No private creator analytics are requested
- No actions are performed on behalf of a user

Do NOT use:
- YouTube Analytics API
- OAuth Client IDs
- Service Accounts

Restrict the API key to:
- YouTube Data API v3
- Backend IP address (recommended)

---

## High-Level Workflow

User Channel Link
→ Resolve Channel ID
→ Fetch Channel Metadata
→ Get Uploads Playlist ID
→ Fetch All Uploaded Videos
→ Fetch Per-Video Details
→ Send Content to AI
→ Store Results in DB and Cache


---

## Step 1: Resolve Channel ID

A YouTube channel may be provided as:
- Channel ID (UCxxxx)
- Handle (@channelname)
- Username (legacy)

### Endpoint
GET https://www.googleapis.com/youtube/v3/channels


### Required Parameters
- part=snippet,contentDetails,statistics
- ONE of:
  - forHandle=@handle
  - id=CHANNEL_ID
  - forUsername=username

### Output Used
- items[0].id → channelId
- items[0].contentDetails.relatedPlaylists.uploads → uploadsPlaylistId

---

## Step 2: Fetch Channel Metadata

### Endpoint
GET https://www.googleapis.com/youtube/v3/channels


### Recommended Parts
- snippet
- statistics
- brandingSettings
- contentDetails
- topicDetails (optional)

### Data Extracted
- Channel name
- Description
- Subscriber count
- Total views
- Total videos
- Profile image
- Banner image
- Uploads playlist ID

### Storage
- Database: persistent channel metadata
- Cache (TTL ~24h): channel overview

---

## Step 3: Fetch All Videos from Channel

YouTube does not provide a direct “list all videos by channel” endpoint.

All uploaded videos are stored in the channel’s **uploads playlist**.

### Endpoint
GET https://www.googleapis.com/youtube/v3/playlistItems


### Required Parameters
- part=snippet,contentDetails
- playlistId=UPLOADS_PLAYLIST_ID
- maxResults=50
- pageToken (for pagination)

### Pagination
- Use nextPageToken until empty
- Each request costs 1 quota unit

### Data Extracted
- Video ID
- Title
- Description
- Published date

### Storage
- Database: video records (videoId as primary key)
- Cache: recent playlist fetches

---

## Step 4: Fetch Per-Video Details

Playlist data does not include statistics.

### Endpoint
GET https://www.googleapis.com/youtube/v3/videos


### Required Parameters
- part=snippet,statistics,contentDetails,topicDetails
- id=comma-separated video IDs (max 50)

### Data Extracted
- View count
- Like count
- Comment count
- Duration
- Tags
- Category ID
- Topics (if available)

### Optimization
- Batch up to 50 video IDs per request
- Cache responses aggressively

---

## Step 5: Transcripts and Content Text

Important:
- YouTube Data API does NOT provide transcripts

Content preparation rules:
- If captions are available → use transcript
- Else → use title + description

AI input per video:
Title
Description
Transcript (if available)


---

## Step 6: AI Analysis (External to YouTube API)

Prepared video content is sent to an AI model to:
- Summarize each video
- Identify main topics
- Determine intent and tone
- Generate a channel-level summary

### AI Output Examples
- Channel niche
- Target audience
- Content style
- Key recurring topics
- Strengths and weaknesses

---

## Data Storage Strategy

### Database (Persistent)
Store:
- Channel metadata
- Video metadata
- AI-generated summaries
- Analysis timestamps

### Cache (Temporary)
Cache:
- Channel overview
- Video lists
- AI results

### Cache TTL Guidelines
- Channel metadata: 24 hours
- Video list: 6–12 hours
- AI summaries: long TTL (content rarely changes)

---

## Handling Repeat Requests

When the same channel is requested again:
1. Check if channel exists in database
2. Fetch only newly uploaded videos
3. Run AI only on new videos
4. Update channel summary incrementally

This reduces:
- API quota usage
- AI cost
- Processing time

---

## Quota Costs

| Endpoint | Quota Cost |
|--------|------------|
| channels.list | 1 |
| playlistItems.list | 1 |
| videos.list | 1 |
| search.list | 100 |

### Recommendation
- Avoid search.list when possible
- Prefer forHandle or direct channelId

---

## API Limitations

The YouTube Data API CANNOT provide:
- Revenue
- Watch time
- Audience retention
- CTR
- Private analytics

These require YouTube Analytics API with OAuth.

---

## Final Summary

- Use YouTube Data API v3 only
- Authenticate with API key
- Fetch channel → uploads playlist → videos → stats
- Prepare clean text for AI analysis
- Store results using DB + cache
- Avoid unnecessary API calls

This is the correct, scalable, and policy-compliant way to analyze public YouTube channels.