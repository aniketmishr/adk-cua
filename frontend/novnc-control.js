/**
 * VNC Controller
 * Manages the noVNC iframe connection and view-only mode toggle
 */

class VNCController {
  constructor(iframeId) {
    this.iframe = document.getElementById(iframeId);
    this.viewOnly = true; // Start in view-only mode
    this.connected = false;
    
    if (!this.iframe) {
      console.error(`VNC iframe with id "${iframeId}" not found`);
    }
  }

  /**
   * Auto-connect to VNC with initial view-only mode
   */
  autoConnect() {
    console.log('Initiating VNC auto-connect...');
    
    // IMPORTANT: Change this URL to match your Docker setup
    // If running locally, use: http://localhost:6080/vnc.html
    // If using Docker Compose service name, use: http://playwright:6080/vnc.html
    const baseUrl = 'http://localhost:6080/vnc.html';
    
    const params = new URLSearchParams({
      autoconnect: 'true',      // Automatically connect on load
      resize: 'scale',           // Scale to fit the iframe
      view_only: 'true',         // Start in view-only mode (no interaction)
      reconnect: 'true',         // Auto-reconnect if connection drops
      reconnect_delay: '2000'    // Wait 2 seconds before reconnecting
    });
    
    const fullUrl = `${baseUrl}?${params.toString()}`;
    console.log('Connecting to:', fullUrl);
    
    this.iframe.src = fullUrl;
    this.connected = true;
    
    // Listen for iframe load events
    this.iframe.onload = () => {
      console.log('VNC iframe loaded successfully');
    };
    
    this.iframe.onerror = (error) => {
      console.error('VNC iframe error:', error);
      this.connected = false;
    };
  }

  /**
   * Toggle between view-only and interactive mode
   * @returns {string} Button text for the current state
   */
  toggleControl() {
    this.viewOnly = !this.viewOnly;
    
    console.log(`Toggling control mode: view_only=${this.viewOnly}`);
    
    // Reload iframe with updated view_only parameter
    const url = new URL(this.iframe.src);
    url.searchParams.set('view_only', this.viewOnly.toString());
    
    this.iframe.src = url.toString();
    
    // Return the button text based on current state
    return this.viewOnly ? 'Take Control' : 'Release Control';
  }

  /**
   * Reconnect to VNC (useful if connection is lost)
   */
  reconnect() {
    console.log('Manual reconnect initiated');
    this.autoConnect();
  }

  /**
   * Check if VNC is connected
   * @returns {boolean}
   */
  isConnected() {
    return this.connected;
  }

  /**
   * Get current control mode
   * @returns {boolean} true if view-only, false if interactive
   */
  isViewOnly() {
    return this.viewOnly;
  }
}