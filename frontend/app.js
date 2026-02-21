/**
 * Agent Chat Application
 * Handles communication with the backend API and UI updates
 */

class AgentChat {
  constructor() {
    this.messages = [];
    this.isProcessing = false;
    
    // IMPORTANT: Update this URL based on your setup
    // If backend is running locally: http://localhost:8000
    // If using Docker Compose: http://backend:8000
    this.API_BASE_URL = 'http://localhost:8000';
    
    this.sessionId = 'session_001';
    this.userId = 'user_1';
  }

  /**
   * Send a task to the agent and stream responses
   * @param {string} task - The task for the agent to execute
   */
  async sendTask(task) {
    if (this.isProcessing) {
      console.warn('Already processing a task, please wait');
      return;
    }

    if (!task || task.trim().length === 0) {
      console.warn('Task cannot be empty');
      return;
    }

    this.isProcessing = true;
    
    // Add user message to chat
    this.addMessage('user', task);
    
    // Create a placeholder for agent response with loading state
    const agentMessageId = this.addMessage('agent', '', true);
    
    // Disable send button during processing
    this.toggleSendButton(false);

    try {
      console.log('Sending task to agent:', task);
      
      const response = await fetch(`${this.API_BASE_URL}/api/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          task: task,
          session_id: this.sessionId,
          user_id: this.userId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Read the SSE stream
      await this.readStream(response.body, agentMessageId);
      
    } catch (error) {
      console.error('Error sending task:', error);
      this.updateMessage(agentMessageId, `❌ Error: ${error.message}`, false, true);
    } finally {
      this.isProcessing = false;
      this.toggleSendButton(true);
    }
  }

  /**
   * Read and process the SSE stream from backend
   * @param {ReadableStream} body - Response body stream
   * @param {number} messageId - ID of the message to update
   */
  async readStream(body, messageId) {
    const reader = body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let accumulatedContent = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          console.log('Stream completed');
          break;
        }

        // Decode chunk and add to buffer
        buffer += decoder.decode(value, { stream: true });
        
        // Process complete lines (SSE format: "data: {...}\n\n")
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep incomplete line in buffer

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6); // Remove "data: " prefix
            
            if (dataStr.trim()) {
              try {
                const data = JSON.parse(dataStr);
                
                // Check if stream is done
                if (data.done) {
                  console.log('Received done signal');
                  this.updateMessage(messageId, accumulatedContent, false, false);
                  return;
                }
                
                // Process and accumulate content
                const content = this.formatStreamData(data);
                if (content) {
                  accumulatedContent += content;
                  this.updateMessage(messageId, accumulatedContent, false, false);
                }
                
              } catch (parseError) {
                console.error('Error parsing SSE data:', parseError, dataStr);
              }
            }
          }
        }
      }
    } catch (error) {
      console.error('Error reading stream:', error);
      throw error;
    }
  }

  /**
   * Format streaming data from backend into readable text
   * @param {Object} data - Data object from SSE stream
   * @returns {string} Formatted content
   */
  formatStreamData(data) {
    let content = '';
    
    if (data.error) {
      content += `❌ <strong>Error:</strong> ${data.error}\n\n`;
    }
    
    if (data.reasoning) {
      content += `🧠 <strong>Reasoning:</strong> ${data.reasoning}\n\n`;
    }
    
    if (data.tool_call) {
      content += `🔧 <strong>Tool Call:</strong> ${data.tool_call}\n\n`;
    }
    
    // if (data.tool_response) {
    //   content += `📋 <strong>Tool Response:</strong> ${data.tool_response}\n\n`;
    // }
    
    if (data.final_answer) {
      content += `✅ <strong>Final Answer:</strong> ${data.final_answer}\n\n`;
    }
    
    return content;
  }

  /**
   * Add a new message to the chat
   * @param {string} role - 'user' or 'agent'
   * @param {string} content - Message content
   * @param {boolean} isLoading - Whether to show loading state
   * @returns {number} Message ID
   */
  addMessage(role, content, isLoading = false) {
    const id = Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    messageDiv.id = `msg-${id}`;
    
    if (isLoading) {
      messageDiv.innerHTML = '<span class="loading">Agent is thinking...</span>';
    } else {
      messageDiv.innerHTML = `<div class="content">${this.formatContent(content)}</div>`;
    }
    
    const container = document.getElementById('chat-messages');
    
    // Remove welcome message if it exists
    const welcomeMsg = container.querySelector('.welcome-message');
    if (welcomeMsg && role === 'user') {
      welcomeMsg.remove();
    }
    
    container.appendChild(messageDiv);
    this.scrollToBottom();
    
    return id;
  }

  /**
   * Update an existing message
   * @param {number} id - Message ID
   * @param {string} content - New content
   * @param {boolean} isLoading - Whether to show loading state
   * @param {boolean} isError - Whether this is an error message
   */
  updateMessage(id, content, isLoading, isError = false) {
    const msg = document.getElementById(`msg-${id}`);
    if (msg) {
      if (isLoading) {
        msg.innerHTML = '<span class="loading">Agent is thinking...</span>';
      } else {
        msg.innerHTML = `<div class="content">${this.formatContent(content)}</div>`;
        if (isError) {
          msg.classList.add('error');
        }
      }
      this.scrollToBottom();
    }
  }

  /**
   * Format content with basic HTML
   * @param {string} text - Raw text content
   * @returns {string} HTML formatted content
   */
  formatContent(text) {
    if (!text) return '';
    
    return text
      .replace(/\n\n/g, '<br><br>')
      .replace(/\n/g, '<br>')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/&lt;strong&gt;/g, '<strong>')
      .replace(/&lt;\/strong&gt;/g, '</strong>')
      .replace(/&lt;br&gt;/g, '<br>');
  }

  /**
   * Scroll chat to bottom
   */
  scrollToBottom() {
    const container = document.getElementById('chat-messages');
    container.scrollTop = container.scrollHeight;
  }

  /**
   * Toggle send button state
   * @param {boolean} enabled - Whether button should be enabled
   */
  toggleSendButton(enabled) {
    const sendBtn = document.getElementById('send-btn');
    const input = document.getElementById('task-input');
    
    if (sendBtn) {
      sendBtn.disabled = !enabled;
      sendBtn.textContent = enabled ? 'Send' : 'Processing...';
    }
    
    if (input) {
      input.disabled = !enabled;
    }
  }

  /**
   * Reset the current session
   */
  async resetSession() {
    if (this.isProcessing) {
      alert('Cannot reset while processing. Please wait.');
      return;
    }

    if (!confirm('Are you sure you want to reset the session? All chat history will be cleared.')) {
      return;
    }

    try {
      console.log('Resetting session:', this.sessionId);
      
      const response = await fetch(`${this.API_BASE_URL}/api/reset-session?session_id=${this.sessionId}`, {
        method: 'POST'
      });

      if (!response.ok) {
        throw new Error(`Failed to reset session: ${response.status}`);
      }

      const result = await response.json();
      console.log('Session reset:', result);
      
      // Clear chat messages
      this.messages = [];
      const container = document.getElementById('chat-messages');
      container.innerHTML = `
        <div class="welcome-message">
          <h3>👋 Session Reset</h3>
          <p>Your session has been cleared. Start a new conversation!</p>
          <p class="example">Example: "Open Google and search for Python tutorials"</p>
        </div>
      `;
      
    } catch (error) {
      console.error('Error resetting session:', error);
      alert(`Failed to reset session: ${error.message}`);
    }
  }

  /**
   * Check backend health
   */
  async checkHealth() {
    try {
      const response = await fetch(`${this.API_BASE_URL}/health`);
      const data = await response.json();
      console.log('Backend health:', data);
      return data.agent_initialized;
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }
}