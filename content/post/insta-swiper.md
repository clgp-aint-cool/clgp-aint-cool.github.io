---
title: "Insta Swiper"
author: clgp
date: "2026-02-14T00:58:20+07:00"
categories:
  -
tags:
  -
---

# Building IG Swiper: An Instagram Photo Gallery Scraper

---

## 🎯 What is IG Swiper?

IG Swiper is a full-stack web application designed to crawl and display Instagram user photos in an elegant, swipeable gallery format. Think of it as your personal Instagram photo archive manager - it downloads photos from public Instagram profiles and presents them in a beautiful, user-friendly interface where you can browse, organize, and enjoy the content.

## 💡 The Purpose & Motivation

Instagram is a wonderful platform for sharing visual content, but it has limitations:

- **No bulk download options** - You can't easily save entire photo collections from your favorite accounts
- **Internet dependency** - You need to be online to view photos
- **Rate limiting & restrictions** - Instagram limits how much you can view without logging in
- **Content preservation** - Posts can be deleted or accounts can go private

## 🏗️ Architecture & Technology Stack

The project is built as a modern full-stack application with clear separation of concerns:

### Backend (Node.js + Express)

- **Framework**: Express.js for RESTful API
- **Database**: Better-SQLite3 for local data storage
- **Scraping Engine**: Node-fetch + Instagram API integration
- **Authentication**: Cookie-based Instagram authentication
- **Security**: Helmet for security headers, CORS for cross-origin protection
- **Performance**: Rate limiting to avoid Instagram blocks, compression middleware

### Frontend (React + Vite)

- **Framework**: React 18 with modern hooks
- **Build Tool**: Vite for fast development and optimized builds
- **Routing**: React Router for navigation
- **Styling**: Modern CSS with responsive design
- **UI/UX**: Swipeable galleries, lazy loading, and smooth animations

### Deployment & Process Management

- **PM2**: Process manager for production deployment
- **Cloudflare Tunnel**: Secure public access without exposing local network
- **Environment Variables**: Flexible configuration for different environments

## 🛠️ The Development Journey

### Phase 1: Core Scraping Engine

The first challenge was understanding Instagram's API structure. Instagram doesn't provide an official public API for downloading photos, so I had to reverse-engineer their web interface:

```javascript
// The core scraping approach uses authenticated requests
async function instagramRequest(url, options = {}) {
  const cookieHeader = getCookieHeader();
  const csrfToken = getCsrfToken();

  const headers = {
    "User-Agent": "Mozilla/5.0 ...",
    Cookie: cookieHeader,
    "X-CSRFToken": csrfToken,
    "X-IG-App-ID": "936619743392459",
    // ... other headers
  };

  return fetch(url, { ...options, headers });
}
```

**Key learnings:**

- Instagram requires valid session cookies for API access
- CSRF tokens must be included in requests
- Rate limiting is crucial (1.5 seconds between requests)
- The API returns paginated results with `next_max_id` cursors

### Phase 2: Handling Different Post Types

Instagram has various content types that needed special handling:

1. **Single image posts** - Straightforward image downloads
2. **Carousel posts** - Multiple images in one post (handled via `carousel_media` array)
3. **Videos** - Skipped during image crawling (media_type === 2)
4. **High-resolution images** - Accessed via `image_versions2.candidates[0].url`

```javascript
// Extract images from carousel posts
if (item.carousel_media) {
  for (const carouselItem of item.carousel_media) {
    if (carouselItem.media_type === 2) continue; // Skip videos

    const url = carouselItem.image_versions2?.candidates?.[0]?.url;
    if (url) {
      allImages.push({ id: carouselItem.id, display_url: url });
    }
  }
}
```

### Phase 3: Database Design

I chose Better-SQLite3 for several reasons:

- **Serverless** - No separate database process needed
- **Fast** - Synchronous API is actually faster for small-scale apps
- **Portable** - Single file database, easy to backup
- **Zero configuration** - Works out of the box

The database schema tracks:

- **Users**: Instagram usernames, display names, crawl status
- **Images**: Downloaded photos with metadata (captions, original URLs)
- **Crawl state**: Status tracking (crawling, completed, stopped, error)

### Phase 4: Crawl State Management

One of the trickiest parts was implementing a robust crawl control system:

```javascript
let crawlState = {
  isActive: false,
  shouldStop: false,
  currentUser: null,
  imagesFound: 0,
};

export function stopCrawl() {
  crawlState.shouldStop = true;
  const stoppedCount = stopAllCrawling(); // Update DB
  return { success: true, message: `${stoppedCount} user(s) stopped` };
}
```

**Challenges solved:**

- Graceful stopping mid-crawl
- Status synchronization between memory and database
- Handling multiple simultaneous crawl requests
- Error recovery and retry logic

### Phase 5: Frontend Development

The frontend needed to be both functional and beautiful:

- **Gallery view** with smooth scrolling and lazy loading
- **Add user interface** with real-time status updates
- **Crawl controls** (start, stop, reset)
- **Responsive design** that works on mobile and desktop
- **Image optimization** for fast loading

### Phase 6: Deployment Strategy

Deploying locally with public access required:

1. **PM2 Configuration**:

```javascript
module.exports = {
  apps: [
    {
      name: "ig-swiper",
      script: "./backend/server.js",
      env: {
        NODE_ENV: "production",
        PORT: 3002,
      },
    },
  ],
};
```

2. **Cloudflare Tunnel**: Secure HTTPS access without port forwarding
3. **Environment variables**: Separate dev/prod configurations
4. **Build optimization**: Production build with Vite

## 🚀 Features & Capabilities

### Current Features

✅ **Batch downloading** - Crawl up to 500 posts per user  
✅ **Carousel support** - Extract all images from multi-image posts  
✅ **Rate limiting** - Intelligent delays to avoid Instagram blocks  
✅ **Status tracking** - Real-time crawl progress updates  
✅ **Error handling** - Graceful failure recovery  
✅ **Duplicate prevention** - Skip already-downloaded images  
✅ **Cookie-based auth** - Use your Instagram session for access  
✅ **Production deployment** - PM2 + Cloudflare Tunnel ready

### Future Enhancements

🔜 **User authentication** - Multi-user support with role-based access  
🔜 **Search & filtering** - Find images by caption or date  
🔜 **Collections** - Organize images into custom albums  
🔜 **Export options** - Bulk download as ZIP files  
🔜 **Video support** - Download and play videos  
🔜 **Privacy controls** - Public/private galleries

## 📊 Technical Challenges & Solutions

### Challenge 1: Instagram Rate Limiting

**Problem**: Instagram blocks aggressive scraping  
**Solution**: Implemented 1.5s delays, max 500 posts limit, and exponential backoff on errors

### Challenge 2: Cookie Expiration

**Problem**: Instagram sessions expire, breaking the scraper  
**Solution**: Cookie validation checks and user-friendly error messages to refresh cookies

### Challenge 3: Image Storage

**Problem**: Where to store potentially thousands of images  
**Solution**: Local filesystem with UUID filenames, configurable via `IMAGES_DIR` env variable
**Problem after problem**: Local machine still the main storage

### Challenge 4: Concurrent Crawls

**Problem**: Multiple users crawling simultaneously could cause conflicts  
**Solution**: Global crawl state with stop flags and database-level status tracking

### Challenge 5: Production Deployment

**Problem**: Running locally but accessible publicly without exposing home network  
**Solution**: Cloudflare Tunnel for secure HTTPS access + PM2 for process stability

## 🎓 Key Learnings

1. **Reverse engineering APIs** - Instagram's web API isn't documented, but network inspection reveals patterns
2. **Rate limiting importance** - Respectful scraping prevents IP bans
3. **State management complexity** - Coordinating async operations requires careful planning
4. **Database choice matters** - SQLite is perfect for single-user, local-first applications
5. **Deployment isn't just hosting** - Process management, monitoring, and tunneling are crucial

## 🔒 Ethical Considerations

IG Swiper is designed for **personal use only**:

- Only scrapes **public** Instagram profiles
- Respects Instagram's rate limits
- Requires user's own Instagram cookies (no credential theft)
- Not intended for commercial use or redistribution
- Users should comply with Instagram's Terms of Service

## 🎯 Conclusion

Building IG Swiper was an educational journey through full-stack development, API reverse engineering, and production deployment. The project demonstrates:

- Modern JavaScript/Node.js best practices
- RESTful API design
- React component architecture
- Database management
- Production deployment strategies
- Security and rate limiting considerations

---

## 📦 Project Resources

- **Stack**: Node.js, Express, React, Vite, SQLite
- **Deployment**: PM2 + Cloudflare Tunnel

---

_Built with ❤️ by a developer who loves beautiful photo galleries and offline-first applications._
