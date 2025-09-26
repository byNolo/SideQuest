# SideQuest Development Progress

**Last Updated:** September 26, 2025
**Current Phase:** Phase 1.5 (User Onboarding) → Active Sprint

---

## 🎯 **Project Overview**

SideQuest is a location-aware, weather-responsive daily quest app that encourages real-world exploration and creativity. Users receive personalized daily challenges based on their location, current weather, and preferences.

**Tech Stack:** React + Vite + Tailwind | Flask + Celery + Redis | PostgreSQL | MinIO | Nginx | KeyN OAuth

---

## ✅ **Completed Features**

### **Phase 0 - Infrastructure & Auth** ✅ **COMPLETE**
- [x] **Docker Infrastructure** - PostgreSQL, Redis, MinIO, Nginx all configured
- [x] **KeyN OAuth Integration** - Full login/logout flow with JWT tokens
- [x] **Database Schema** - All 11 tables implemented with Alembic migrations
- [x] **Basic API Skeleton** - Health, auth, and core endpoints
- [x] **React Frontend** - Basic UI with authentication flow
- [x] **Alembic Setup** - Database migrations working properly

### **Phase 1 - Quests Core** ✅ **COMPLETE**
- [x] **Quest Templates System** 
  - 6 diverse templates (Neighborhood Snapshot, Weather Witness, Urban Explorer, Street Artist, Social Connection, Seasonal Treasure)
  - Rarity system (common, rare, legendary)
  - Constraint-based generation
  - Template seeding and management

- [x] **Weather Integration**
  - Open-Meteo API integration
  - Real-time weather data fetching
  - Weather-aware quest modifiers
  - Caching system for API efficiency

- [x] **Location & Place Lookup**
  - OpenStreetMap/Overpass API integration
  - Dynamic place finding based on quest requirements
  - Distance calculation and sorting
  - Place type filtering

- [x] **Quest Generation Engine**
  - User-specific personalized quests
  - Deterministic generation (same quest per user per day)
  - Weather-responsive template selection
  - Weighted rarity-based selection
  - Context-aware placeholder replacement

- [x] **Enhanced Frontend**
  - Rich quest display with weather info
  - Difficulty and rarity indicators
  - Quest context and location suggestions
  - Real-time weather display
  - Responsive Tailwind CSS design

- [x] **API Endpoints**
  - `GET /api/quests/today` - Generate/retrieve daily quest
  - `GET /api/templates` - List available quest templates
  - `POST /api/admin/seed-templates` - Initialize templates
  - Debug authentication for testing

---

## 🚧 **In Progress**

**Phase 1.5 - User Onboarding & Preferences** 🚧 **ACTIVE**

---

## 📋 **Next Steps - Phase 1.5: User Onboarding & Preferences** 

### **Priority 1 - User Information Collection**
- [ ] **Location Permission & Setup**
  - [x] Browser geolocation API integration (debug onboarding panel)
  - [x] Location permission flow in React (debug onboarding panel)
  - [x] Fallback manual location entry (city search)
  - [x] Store user's default location in preferences

- [ ] **Onboarding Flow**
  - [x] First-time user welcome screen
  - [x] Location setup wizard (debug panel onboarding page)
  - [x] Quest preference questionnaire
  - [x] Privacy settings selection

- [ ] **User Preferences API**
  - [x] `PATCH /api/me/preferences` - Update user preferences
  - [x] `POST /api/me/location` - Update current location
  - [x] `GET /api/me` - Fetch consolidated profile snapshot
  - [x] `POST /api/me/notifications/register` - Store simulated push subscription
  - [ ] Location history tracking (for "recent locations")

- [ ] **Notification Opt-in (Web Push)**
  - [x] Debug onboarding UI to simulate push registration
  - [x] Backend endpoints to save/clear web push subscription data
  - [ ] Service worker subscription flow with real browser prompts
  - [ ] User-facing copy for permissions & troubleshooting

### **Priority 2 - Enhanced Quest Personalization**
- [ ] **Location-Aware Quest Generation**
  - Use real user location instead of defaults
  - Multiple location support (home, work, current)
  - Location-based quest radius adaptation
  - "Nearby places" integration with user's actual location

- [ ] **Preference-Based Quest Filtering**
  - Filter templates by user's activity preferences
  - Respect spending limits for quest suggestions
  - Time-based quest filtering (quick vs. extended quests)
  - Indoor/outdoor preference handling

### **Priority 3 - User Profile Management**
- [ ] **Profile Settings Page**
  - Edit basic info (display name, bio, avatar)
  - Update location and radius preferences
  - Manage quest preferences and limits
  - Privacy settings control

---

## 📋 **Phase 2: Media & Submissions**

### **Priority 1 - Media Pipeline**
- [ ] **MinIO Integration**
  - Configure bucket creation on startup
  - Implement pre-signed URL generation for uploads
  - Set up media serving with Nginx

- [ ] **File Upload System**
  - React drag/drop upload component
  - Mobile camera capture support
  - Client-side file validation (size, type)
  - Progress tracking for uploads

- [ ] **Media Processing (Celery)**
  - Image resizing and thumbnail generation
  - Video transcoding (H.264, thumbnails)
  - EXIF data extraction and sanitization
  - Content hashing for deduplication

### **Priority 2 - Submissions**
- [ ] **Submission Model Enhancement**
  - Link to media files in MinIO
  - Caption processing and validation
  - Status management (pending, visible, flagged)

- [ ] **Submission API**
  - `POST /api/submissions` - Create submission
  - `GET /api/submissions/feed` - Global feed
  - Media metadata handling
  - Input validation and sanitization

- [ ] **Submission Frontend**
  - Quest completion interface
  - Photo/video capture and upload
  - Caption input with character limits
  - Upload progress and success states

### **Priority 3 - Feed Implementation**
- [ ] **Global Feed**
  - Chronological submission display
  - Image/video rendering
  - Infinite scroll or pagination
  - Basic filtering options

---

## 📅 **Future Phases**

### **Phase 3 - Voting & Scoring** 🔮
- [ ] Multi-criteria voting system (effort, creativity, execution)
- [ ] Bayesian average scoring algorithm
- [ ] Leaderboard generation and caching
- [ ] Streak tracking and bonuses
- [ ] Anti-cheat heuristics

### **Phase 4 - Social & Push** 🔮
- [ ] Friendship system (request, accept, block)
- [ ] Friends-only feed
- [ ] Web Push notifications with VAPID
- [ ] Delivery window scheduling using user preferences
- [ ] Advanced notification customization

### **Phase 5 - Moderation & Polish** 🔮
- [ ] Content moderation queue
- [ ] Automated flagging system
- [ ] User reporting functionality
- [ ] Admin dashboard
- [ ] Performance optimizations

---

## 🏗️ **Technical Architecture**

### **Database Schema** ✅
```
users, quest_templates, quests, submissions, votes, 
friendships, locations, streaks, notifications, 
leaderboard_snapshots, moderation_flags
```

### **API Structure** ✅
```
/api/health, /api/auth/*, /api/quests/*, 
/api/templates, /api/admin/*
```

### **External Integrations** ✅
- **Weather:** Open-Meteo (free, no API key)
- **Maps:** Overpass API (OpenStreetMap)
- **Auth:** KeyN OAuth (byNolo)
- **Storage:** MinIO (S3-compatible)

---

## 🧪 **Testing Status**

### **Working Endpoints** ✅
- `GET /api/health` - Service health check
- `GET /api/auth/me` - Authentication status
- `GET /api/quests/today` - Quest generation (with/without auth)
- `GET /api/templates` - Template listing
- `POST /api/admin/seed-templates` - Template initialization
- `GET /api/me` - Consolidated user profile for onboarding
- `PATCH /api/me/preferences` - Save quest and global preferences
- `POST /api/me/location` - Persist default location
- `POST /api/me/notifications/register` - Record simulated push subscription
- `DELETE /api/me/notifications/register` - Clear stored push subscription
- `GET /api/geocode/reverse` - Reverse geocode coordinates for geolocation flow

### **Verified Features** ✅
- Weather API integration (real-time data)
- Place lookup (OpenStreetMap integration)
- Quest variation by user (deterministic seeding)
- Database migrations (Alembic)
- Frontend quest display (weather, difficulty, context)
- Docker container orchestration
- Onboarding wizard with location search, preference saving, and debug push opt-in
- Geolocation-assisted location setup with reverse geocoding
- Privacy controls surfaced during onboarding and dashboard snapshot
- Welcome hero for first-time onboarding to guide initial setup
- Dashboard timeout + helpful error messaging for unreachable API scenarios

---

## 🔧 **Development Commands**

```bash
# Start all services
docker compose up -d

# Rebuild specific service
docker compose build api && docker compose up -d api

# Check logs
docker compose logs api --tail=20

# Database migration
docker compose exec api alembic revision --autogenerate -m "description"
docker compose exec api alembic upgrade head

# Test endpoints
curl -H "X-Debug-User: testuser" http://localhost:8080/api/quests/today
```

---

## 📊 **Metrics & Progress**

- **Database Tables:** 11/11 implemented ✅
- **Core APIs:** 6/6 working ✅
- **Quest Templates:** 6 diverse templates ✅
- **External APIs:** 2/2 integrated (Weather + Maps) ✅
- **Authentication:** KeyN OAuth fully working ✅
- **Frontend Components:** Quest display complete ✅

**Overall Progress:** ~30% complete (Phases 0-1 of 5)

---

## 🎯 **Success Criteria for Phase 2**

1. **Media Upload Working** - Users can upload photos/videos from web and mobile
2. **Submission Creation** - Users can complete quests with media + captions
3. **Global Feed** - All submissions visible in chronological feed
4. **Media Processing** - Automatic thumbnails and optimization
5. **MinIO Integration** - Reliable file storage and serving

**Target Completion:** Phase 2 estimated at 1-2 weeks

---

## 📝 **Notes**

- **KeyN Integration:** Fully functional OAuth flow with JWT validation
- **Quest Variety:** Deterministic but varied based on user hash and date
- **Weather Responsiveness:** Quests adapt to current conditions automatically
- **Scalability:** Redis caching for weather/places, PostgreSQL for persistence
- **Development:** Debug authentication (X-Debug-User header) for easy testing

**Current Status:** Infrastructure solid, quest generation polished, ready for media pipeline.