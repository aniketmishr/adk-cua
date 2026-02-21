/**
 * Configuration File
 * 
 * Update these URLs based on your setup, then the JavaScript files
 * will automatically use the correct endpoints.
 * 
 * INSTRUCTIONS:
 * 1. Copy this file's content
 * 2. Update the URLs below
 * 3. Paste the updated values into:
 *    - app.js (line 12): API_BASE_URL
 *    - novnc-control.js (line 23): baseUrl
 */

// ========================================
// CONFIGURATION - UPDATE THESE VALUES
// ========================================

const CONFIG = {
  // Backend API URL
  // Where your FastAPI backend is running
  API_BASE_URL: 'http://localhost:8000',
  
  // noVNC URL
  // Where your Playwright browser stream is accessible
  NOVNC_URL: 'http://localhost:6080/vnc.html',
  
  // Session settings
  DEFAULT_SESSION_ID: 'session_001',
  DEFAULT_USER_ID: 'user_1'
};

// ========================================
// COMMON CONFIGURATIONS
// ========================================

// Option 1: Everything running locally (no Docker)
// API_BASE_URL: 'http://localhost:8000'
// NOVNC_URL: 'http://localhost:6080/vnc.html'

// Option 2: Using Docker Compose (all services in same network)
// API_BASE_URL: 'http://backend:8000'
// NOVNC_URL: 'http://playwright:6080/vnc.html'

// Option 3: Frontend local, Backend and Playwright in Docker
// API_BASE_URL: 'http://localhost:8000'
// NOVNC_URL: 'http://localhost:6080/vnc.html'

// Option 4: Custom ports
// API_BASE_URL: 'http://localhost:9000'  // If backend on port 9000
// NOVNC_URL: 'http://localhost:7080/vnc.html'  // If VNC on port 7080

// Option 5: Remote server
// API_BASE_URL: 'http://your-server.com:8000'
// NOVNC_URL: 'http://your-server.com:6080/vnc.html'

// ========================================
// HOW TO APPLY THIS CONFIGURATION
// ========================================

/*

STEP 1: Update app.js
----------------------
Open: app.js
Find: Line 12
Change:
    this.API_BASE_URL = 'http://localhost:8000';
To:
    this.API_BASE_URL = CONFIG.API_BASE_URL;  // Or paste the URL directly


STEP 2: Update novnc-control.js
--------------------------------
Open: novnc-control.js
Find: Line 23
Change:
    const baseUrl = 'http://localhost:6080/vnc.html';
To:
    const baseUrl = CONFIG.NOVNC_URL;  // Or paste the URL directly


STEP 3: Test your changes
--------------------------
1. Save both files
2. Refresh your browser (or restart the server)
3. Check browser console (F12) for any errors
4. Try sending a test message

*/

// ========================================
// TROUBLESHOOTING
// ========================================

/*

ERROR: "Failed to fetch" or "Network Error"
-------------------------------------------
Problem: Frontend can't reach backend
Solution: 
  - Verify backend is running: curl http://localhost:8000/health
  - Check if API_BASE_URL is correct
  - Make sure CORS is enabled in backend


ERROR: VNC panel shows "Unable to connect"
-------------------------------------------
Problem: Frontend can't reach noVNC
Solution:
  - Test VNC directly in browser: http://localhost:6080/vnc.html
  - Check if NOVNC_URL is correct
  - Verify Playwright container is running: docker ps


ERROR: CORS policy blocking requests
-------------------------------------
Problem: Browser blocking requests due to CORS
Solution:
  - Make sure your backend has CORS middleware enabled
  - Add your frontend URL to allowed origins in backend
  - Example in FastAPI:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8080"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

*/

// ========================================
// TESTING YOUR CONFIGURATION
// ========================================

/*

Test 1: Backend Health Check
-----------------------------
Open in browser: http://localhost:8000/health
Expected: JSON response with "status": "healthy"


Test 2: noVNC Connection
-------------------------
Open in browser: http://localhost:6080/vnc.html
Expected: VNC connection screen (may need to click Connect)


Test 3: Frontend Loading
-------------------------
Open in browser: http://localhost:8080 (or wherever you're serving frontend)
Expected: Chat panel on left, browser panel on right


Test 4: End-to-End Test
------------------------
1. Type a task in chat: "Open Google"
2. Click Send
3. Watch for:
   - Messages streaming in chat
   - Browser performing actions on right panel

*/
