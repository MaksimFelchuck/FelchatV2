// Modern Chat JavaScript

class ModernChat {
    constructor() {
        this.ws = null;
        this.currentUser = null;
        this.currentChatUser = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.isManualClose = false; // Flag to prevent reconnection on manual close
        
        this.init();
    }
    
    init() {
        console.log('=== ModernChat init() called ===');
        
        this.setupEventListeners();
        this.setupAutoResize();
        this.setupKeyboardShortcuts();
        this.setupNotifications();
        
        // Initialize WebSocket if we have a current chat user (e.g., from URL)
        if (this.currentChatUser) {
            this.initializeWebSocket();
        }
        
        // Setup event listeners for dynamically created elements
        this.setupDynamicEventListeners();
        
        // Initialize UI based on current chat user's blocked status
        console.log('Calling initializeBlockUI from init()');
        this.initializeBlockUI();
    }
    
    setupEventListeners() {
        // Send message on Enter (Shift+Enter for new line)
        const messageInput = document.getElementById('message-input');
        if (messageInput) {
            messageInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
            
            messageInput.addEventListener('input', () => {
                this.autoResizeTextarea(messageInput);
            });
        }
        
        // Send button
        const sendBtn = document.getElementById('send-btn');
        if (sendBtn) {
            console.log('Setting up send button listener in setupEventListeners');
            sendBtn.addEventListener('click', (e) => {
                console.log('Send button clicked (setupEventListeners)');
                e.preventDefault();
                this.sendMessage();
            });
        } else {
            console.log('Send button not found in setupEventListeners');
        }
        
        // User list items - only on chat page
        if (window.location.pathname.includes('/chat')) {
            document.querySelectorAll('.user-item').forEach(item => {
                item.addEventListener('click', (e) => {
                    e.preventDefault();
                    const userId = item.dataset.userId;
                    const username = item.dataset.username;
                    console.log('User clicked:', userId, username);
                    this.selectUser(userId, username);
                });
            });
        }
        
        // Block/Unblock buttons - only on chat page
        if (window.location.pathname.includes('/chat')) {
            document.querySelectorAll('.block-btn, .unblock-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    const userId = btn.dataset.userId;
                    const action = btn.classList.contains('block-btn') ? 'block' : 'unblock';
                    console.log('Block/Unblock button clicked:', action, 'for user:', userId);
                    if (action === 'block') {
                        this.blockUserFromButton(btn);
                    } else {
                        this.unblockUserFromButton(btn);
                    }
                });
            });
        }
        
        // Window events
        window.addEventListener('beforeunload', () => {
            if (this.ws) {
                this.ws.close();
            }
        });
        
        window.addEventListener('focus', () => {
            this.markMessagesAsRead();
        });
    }
    
    setupDynamicEventListeners() {
        // Use event delegation for user items and send button
        document.addEventListener('click', (e) => {
            if (e.target.closest('.user-item')) {
                const userItem = e.target.closest('.user-item');
                const userId = userItem.dataset.userId;
                const username = userItem.dataset.username;
                
                console.log('User clicked (delegated):', userId, username);
                console.log('User item found:', userItem);
                console.log('Dataset:', userItem.dataset);
                
                if (userId && username) {
                    this.selectUser(userId, username);
                } else {
                    console.error('Missing userId or username in dataset');
                }
            }
            
            // Handle send button clicks
            if (e.target.closest('#send-btn') || e.target.id === 'send-btn') {
                console.log('Send button clicked (delegated)');
                console.log('Target element:', e.target);
                console.log('Target id:', e.target.id);
                console.log('Target classList:', e.target.classList);
                e.preventDefault();
                e.stopPropagation();
                this.sendMessage();
            }
        });
        
        // Also add direct event listeners after a short delay to ensure DOM is ready
        setTimeout(() => {
            console.log('Setting up direct event listeners for user items');
            const userItems = document.querySelectorAll('.user-item');
            console.log('Found user items:', userItems.length);
            
            userItems.forEach((item, index) => {
                console.log(`User item ${index}:`, item.dataset);
                item.addEventListener('click', (e) => {
                    e.preventDefault();
                    const userId = item.dataset.userId;
                    const username = item.dataset.username;
                    console.log('User clicked (direct):', userId, username);
                    this.selectUser(userId, username);
                });
            });
            
            // Also setup send button listener
            const sendBtn = document.getElementById('send-btn');
            if (sendBtn) {
                console.log('Setting up send button listener');
                sendBtn.addEventListener('click', (e) => {
                    e.preventDefault();
                    console.log('Send button clicked');
                    this.sendMessage();
                });
            } else {
                console.log('Send button not found');
            }
        }, 100);
    }
    
    setupAutoResize() {
        const textareas = document.querySelectorAll('textarea');
        textareas.forEach(textarea => {
            textarea.addEventListener('input', () => {
                this.autoResizeTextarea(textarea);
            });
        });
    }
    
    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + Enter to send message
            if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                e.preventDefault();
                this.sendMessage();
            }
            
            // Escape to clear input
            if (e.key === 'Escape') {
                const messageInput = document.getElementById('message-input');
                if (messageInput && document.activeElement === messageInput) {
                    messageInput.value = '';
                    this.autoResizeTextarea(messageInput);
                }
            }
        });
    }
    
    initializeWebSocket() {
        if (!this.currentChatUser) {
            console.log('No chat user selected, skipping WebSocket connection');
            return;
        }
        
        // Prevent multiple connections
        if (this.ws && (this.ws.readyState === WebSocket.CONNECTING || this.ws.readyState === WebSocket.OPEN)) {
            console.log('WebSocket already connecting or connected, skipping');
            return;
        }
        
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/chat?user_id=${this.currentUser}&other_user=${this.currentChatUser}`;
        
        console.log('=== WebSocket Connection Details ===');
        console.log('Connecting to WebSocket:', wsUrl);
        console.log('Current user:', this.currentUser);
        console.log('Chat user:', this.currentChatUser);
        console.log('Current user type:', typeof this.currentUser);
        console.log('Chat user type:', typeof this.currentChatUser);
        
        if (!this.currentUser) {
            console.error('ERROR: currentUser is not set!');
            this.showNotification('Ошибка: пользователь не определен', 'danger');
            return;
        }
        this.updateConnectionStatus('connecting');
        this.ws = new WebSocket(wsUrl);
        
        // Add connection timeout
        const connectionTimeout = setTimeout(() => {
            if (this.ws && this.ws.readyState === WebSocket.CONNECTING) {
                console.log('WebSocket connection timeout');
                this.ws.close();
                this.updateConnectionStatus('disconnected');
                this.showNotification('Таймаут подключения', 'danger');
            }
        }, 5000); // 5 second timeout
        
        this.ws.onopen = () => {
            clearTimeout(connectionTimeout);
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.updateConnectionStatus('connected');
            console.log('=== WebSocket connected successfully ===');
            console.log('Connected to user:', this.currentChatUser);
            console.log('WebSocket state:', this.ws.readyState);
            console.log('isConnected flag:', this.isConnected);
            
            // Force status update after a short delay
            setTimeout(() => {
                this.updateConnectionStatus('connected');
            }, 100);
        };
        
        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };
        
        this.ws.onclose = (event) => {
            this.isConnected = false;
            
            console.log('WebSocket disconnected:', event.code, event.reason, 'Manual close:', this.isManualClose);
            console.log('Close event details:', {
                code: event.code,
                reason: event.reason,
                wasClean: event.wasClean,
                manualClose: this.isManualClose
            });
            
            // Only update status if this wasn't a manual close
            if (event.code !== 1000 && !this.isManualClose) {
                this.updateConnectionStatus('disconnected');
                this.showNotification('Соединение разорвано', 'warning');
                // Don't attempt automatic reconnection - let user manually reconnect
            } else {
                // Manual close - don't show disconnected status or attempt reconnect
                console.log('WebSocket manually closed, not attempting reconnect');
                this.isManualClose = false; // Reset flag
            }
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            console.error('WebSocket error details:', {
                readyState: this.ws?.readyState,
                url: this.ws?.url,
                bufferedAmount: this.ws?.bufferedAmount
            });
            this.updateConnectionStatus('disconnected');
            this.showNotification('Ошибка WebSocket соединения', 'danger');
        };
    }
    
    handleMessage(data) {
        console.log('Received message:', data);
        
        // Handle different message formats
        if (typeof data === 'string') {
            try {
                const parsed = JSON.parse(data);
                this.handleMessage(parsed);
                return;
            } catch (e) {
                console.error('Failed to parse message as JSON:', e);
                return;
            }
        }
        
        if (data.type === 'message') {
            this.addMessage(data);
            this.scrollToBottom();
            this.playMessageSound();
        } else if (data.type === 'block_notification') {
            this.showNotification(data.message, 'warning');
        } else if (data.type === 'error') {
            this.showNotification(data.message, 'danger');
        } else if (data.from && data.message) {
            // Direct message format (from WebSocket)
            this.addMessage(data);
            this.scrollToBottom();
            this.playMessageSound();
        } else {
            console.warn('Unknown message format:', data);
        }
    }
    
    addMessage(data) {
        const messagesContainer = document.getElementById('messages');
        if (!messagesContainer) return;
        
        // Handle different message formats
        let messageText, fromUser, fromUsername, timestamp;
        
        if (typeof data === 'string') {
            // If data is a string, try to parse it as JSON
            try {
                const parsed = JSON.parse(data);
                messageText = parsed.message || data;
                fromUser = parsed.from || parsed.from_user_id;
                fromUsername = parsed.from_username;
                timestamp = parsed.timestamp || Date.now() / 1000;
            } catch (e) {
                messageText = data;
                fromUser = this.currentUser;
                fromUsername = null;
                timestamp = Date.now() / 1000;
            }
        } else if (data.type === 'message') {
            messageText = data.message;
            fromUser = data.from || data.from_user_id;
            fromUsername = data.from_username;
            timestamp = data.timestamp || Date.now() / 1000;
        } else if (data.message) {
            // Direct message object
            messageText = data.message;
            fromUser = data.from || data.from_user_id || this.currentUser;
            fromUsername = data.from_username;
            timestamp = data.timestamp || Date.now() / 1000;
        } else {
            // Fallback - don't display JSON
            console.warn('Unknown message format:', data);
            return;
        }
        
        // Don't display empty messages or JSON strings
        if (!messageText || messageText.trim() === '') {
            return;
        }
        
        // Don't display if messageText looks like JSON
        if (messageText.startsWith('{') && messageText.includes('"message"')) {
            try {
                const parsed = JSON.parse(messageText);
                if (parsed.message) {
                    messageText = parsed.message;
                } else {
                    console.warn('Message contains JSON but no message field:', messageText);
                    return;
                }
            } catch (e) {
                console.warn('Message looks like JSON but failed to parse:', messageText);
                return;
            }
        }
        
        const messageDiv = document.createElement('div');
        // Convert to numbers for proper comparison
        const fromUserId = parseInt(fromUser);
        const currentUserId = parseInt(this.currentUser);
        const isOwnMessage = fromUserId === currentUserId;
        messageDiv.className = `message ${isOwnMessage ? 'own' : ''}`;
        
        console.log('Adding message:', {
            fromUser: fromUser,
            fromUserId: fromUserId,
            currentUser: this.currentUser,
            currentUserId: currentUserId,
            isOwn: isOwnMessage,
            message: messageText,
            fromUsername: fromUsername,
            comparison: `${fromUserId} === ${currentUserId} = ${isOwnMessage}`
        });
        
        // Debug: Check if currentUser is set correctly
        if (!this.currentUser) {
            console.error('Current user is not set!');
        }
        
        // Additional debug info
        if (fromUserId === currentUserId) {
            console.log('✅ This is OWN message');
        } else {
            console.log('❌ This is OTHER message');
        }
        
        const timeDate = new Date(timestamp * 1000);
        const timeString = timeDate.toLocaleTimeString('ru-RU', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        const avatar = this.getUserAvatar(fromUser);
        // Use username from message if available, otherwise try to get from DOM
        const authorName = fromUsername || this.getUserName(fromUser);
        
        messageDiv.innerHTML = `
            <div class="message-avatar">${avatar}</div>
            <div class="message-content">
                <div class="message-header">
                    <span class="message-author">${authorName}</span>
                    <span class="message-time">${timeString}</span>
                </div>
                <div class="message-text">${this.escapeHtml(messageText)}</div>
            </div>
        `;
        
        messagesContainer.appendChild(messageDiv);
        
        // Add animation
        messageDiv.style.opacity = '0';
        messageDiv.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            messageDiv.style.transition = 'all 0.3s ease-out';
            messageDiv.style.opacity = '1';
            messageDiv.style.transform = 'translateY(0)';
        }, 10);
    }
    
    getUserAvatar(userId) {
        // Generate avatar based on user ID
        const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'];
        const color = colors[userId % colors.length];
        const letter = String.fromCharCode(65 + (userId % 26));
        
        return `<div style="background: ${color}; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; color: white;">${letter}</div>`;
    }
    
    getUserName(userId) {
        // Try to get username from DOM first
        const userElement = document.querySelector(`[data-user-id="${userId}"]`);
        if (userElement) {
            const usernameElement = userElement.querySelector('.user-name');
            if (usernameElement) {
                return usernameElement.textContent;
            }
        }
        
        // Try to get from data attribute
        if (userElement && userElement.dataset.username) {
            return userElement.dataset.username;
        }
        
        // Fallback to user ID if no DOM element found
        return `Пользователь ${userId}`;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    sendMessage() {
        const messageInput = document.getElementById('message-input');
        if (!messageInput || !this.currentChatUser) {
            console.log('Cannot send message:', {
                hasInput: !!messageInput,
                currentChatUser: this.currentChatUser
            });
            return;
        }
        
        const message = messageInput.value.trim();
        if (!message) return;
        
        console.log('Sending message:', message, 'to user:', this.currentChatUser);
        
        // Check WebSocket state
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            console.error('WebSocket not ready:', {
                hasWs: !!this.ws,
                readyState: this.ws?.readyState
            });
            this.showNotification('Соединение не установлено', 'danger');
            return;
        }
        
        const sendBtn = document.getElementById('send-btn');
        if (sendBtn) {
            sendBtn.disabled = true;
            sendBtn.innerHTML = '<div class="loading"></div>';
        }
        
        // Send just the message text, not JSON
        this.ws.send(message);
        
        // Clear input and reset button
        messageInput.value = '';
        this.autoResizeTextarea(messageInput);
        
        if (sendBtn) {
            setTimeout(() => {
                sendBtn.disabled = false;
                sendBtn.innerHTML = 'Отправить <i class="fas fa-paper-plane"></i>';
            }, 1000);
        }
        
        // Focus back to input
        messageInput.focus();
    }
    
    selectUser(userId, username) {
        // Prevent switching to the same user
        if (this.currentChatUser === parseInt(userId)) {
            console.log('Already chatting with this user, skipping switch');
            return;
        }
        
        console.log('Switching to user:', userId, username);
        console.log('Previous currentChatUser:', this.currentChatUser);
        
        this.currentChatUser = parseInt(userId);
        console.log('New currentChatUser:', this.currentChatUser);
        
        // Close existing WebSocket connection properly
        if (this.ws) {
            console.log('Closing existing WebSocket connection');
            this.isManualClose = true; // Set flag to prevent reconnection
            this.ws.onclose = null; // Prevent reconnect attempts
            this.ws.onerror = null; // Prevent error handlers
            this.ws.onmessage = null; // Prevent message handlers
            this.ws.onopen = null; // Prevent open handlers
            
            if (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING) {
                this.ws.close(1000, 'User switching');
            }
            this.ws = null;
        }
        
        // Reset connection state
        this.isConnected = false;
        this.reconnectAttempts = 0;
        
        // Update connection status immediately
        this.updateConnectionStatus('connecting');
        
        // Update active user in list
        document.querySelectorAll('.user-item').forEach(item => {
            item.classList.remove('active');
        });
        
        const selectedItem = document.querySelector(`[data-user-id="${userId}"]`);
        if (selectedItem) {
            selectedItem.classList.add('active');
        }
        
        // Update chat title
        const chatTitle = document.querySelector('.chat-title');
        if (chatTitle) {
            chatTitle.innerHTML = `<i class="fas fa-comment"></i> Чат с ${username}`;
        }
        
        // Clear messages and load history
        this.loadChatHistory(userId, username);
        
        // Initialize WebSocket connection after a longer delay to ensure old connection is closed
        setTimeout(() => {
            console.log('Initializing new WebSocket connection');
            this.initializeWebSocket();
        }, 500);
        
        // Initialize block UI for the new user
        setTimeout(async () => {
            console.log('Initializing block UI for new user');
            await this.initializeBlockUI();
        }, 600);
        
        // Update URL without page reload
        const url = new URL(window.location);
        url.pathname = '/chat'; // Ensure we're on the chat page
        url.searchParams.set('user', userId);
        window.history.pushState({}, '', url);
    }
    
    async loadChatHistory(userId, username = null) {
        const messagesContainer = document.getElementById('messages');
        if (!messagesContainer) return;
        
        // Show loading
        messagesContainer.innerHTML = '<div class="loading" style="margin: 2rem auto;"></div>';
        
        try {
            const response = await fetch(`/chat/history?user=${userId}`);
            const history = await response.json();
            
            messagesContainer.innerHTML = '';
            
            if (history.length === 0) {
                const displayName = username || this.getUserName(userId);
                messagesContainer.innerHTML = `
                    <div style="text-align: center; color: var(--text-secondary); margin: 2rem 0;">
                        <i class="fas fa-comments" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                        <p>Начните разговор с ${displayName}</p>
                    </div>
                `;
            } else {
                console.log('Loading chat history:', history);
                console.log('Current user for history:', this.currentUser);
                
                history.forEach(message => {
                    this.addMessage(message);
                });
            }
            
            this.scrollToBottom();
            
        } catch (error) {
            console.error('Error loading chat history:', error);
            messagesContainer.innerHTML = `
                <div class="alert alert-danger">
                    Ошибка загрузки истории сообщений
                </div>
            `;
        }
    }
    
    async toggleBlock(userId, action) {
        try {
            const response = await fetch(`/users/${action}/${userId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });
            
            if (response.ok) {
                // Reload the page to show updated state
                window.location.reload();
            } else {
                this.showNotification('Ошибка при выполнении действия', 'danger');
            }
        } catch (error) {
            console.error('Error toggling block:', error);
            this.showNotification('Ошибка сети', 'danger');
        }
    }
    
    updateBlockButton(userId, isBlocked) {
        console.log('updateBlockButton called with userId:', userId, 'isBlocked:', isBlocked);
        
        const buttonContainer = document.querySelector('.chat-status');
        console.log('Found button container:', buttonContainer);
        
        if (buttonContainer) {
            // Удаляем старую кнопку
            const existingButton = buttonContainer.querySelector('.block-btn, .unblock-btn');
            if (existingButton) {
                console.log('Removing existing button');
                existingButton.remove();
            }
            
            // Создаем новую кнопку
            const newButton = document.createElement('button');
            newButton.className = isBlocked ? 'status-badge unblock-btn' : 'status-badge block-btn';
            newButton.setAttribute('data-user-id', userId);
            newButton.onclick = isBlocked ? () => this.unblockUserFromButton(newButton) : () => this.blockUserFromButton(newButton);
            newButton.innerHTML = isBlocked ? 
                '<i class="fas fa-unlock"></i> РАЗБЛОКИРОВАТЬ' : 
                '<i class="fas fa-ban"></i> ЗАБЛОКИРОВАТЬ';
            
            buttonContainer.appendChild(newButton);
            console.log('Added new button:', newButton.innerHTML);
            
            // Обновляем форму ввода
            console.log('Calling updateChatInput with isBlocked:', isBlocked);
            this.updateChatInput(isBlocked);
        } else {
            console.error('Button container not found!');
        }
    }
    
    updateConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status');
        if (!statusElement) return;
        
        // Remove all status classes
        statusElement.classList.remove('status-connecting', 'status-connected', 'status-disconnected');
        
        // Add new status class
        statusElement.classList.add(`status-${status}`);
        
        switch (status) {
            case 'connected':
                statusElement.textContent = 'ПОДКЛЮЧЕНО';
                break;
            case 'disconnected':
                statusElement.textContent = 'ОТКЛЮЧЕНО';
                break;
            case 'connecting':
                statusElement.textContent = 'ПОДКЛЮЧЕНИЕ...';
                break;
        }
        
        console.log('Connection status updated:', status);
    }
    
    scrollToBottom() {
        const messagesContainer = document.getElementById('messages');
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
    }
    
    markMessagesAsRead() {
        // Implementation for marking messages as read
        // This could be used for read receipts in the future
    }
    
    playMessageSound() {
        // Play notification sound for new messages
        // This could be implemented with Web Audio API
    }
    
    setupNotifications() {
        // Request notification permission
        if ('Notification' in window) {
            Notification.requestPermission();
        }
    }
    
    showNotification(message, type = 'info') {
        // Create notification container if it doesn't exist
        let notificationContainer = document.getElementById('notification-container');
        if (!notificationContainer) {
            notificationContainer = document.createElement('div');
            notificationContainer.id = 'notification-container';
            notificationContainer.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                max-width: 300px;
                pointer-events: none;
            `;
            document.body.appendChild(notificationContainer);
        }
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            background: ${type === 'success' ? 'linear-gradient(135deg, #00b894, #00a085)' : 
                         type === 'danger' ? 'linear-gradient(135deg, #ff6b6b, #ee5a24)' :
                         type === 'warning' ? 'linear-gradient(135deg, #fdcb6e, #e17055)' :
                         'linear-gradient(135deg, #74b9ff, #0984e3)'};
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 10px;
            font-size: 14px;
            font-weight: 500;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            transform: translateX(100%);
            opacity: 0;
            transition: all 0.3s ease-out;
            pointer-events: auto;
            cursor: pointer;
        `;
        notification.textContent = message;
        
        // Add to container
        notificationContainer.appendChild(notification);
        
        // Animate in
        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
            notification.style.opacity = '1';
        }, 10);
        
        // Auto remove after 3 seconds
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }, 3000);
        
        // Click to dismiss
        notification.addEventListener('click', () => {
            notification.style.transform = 'translateX(100%)';
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        });
        
        // Browser notification (only for important messages)
        if (type === 'danger' && 'Notification' in window && Notification.permission === 'granted') {
            new Notification('Felchat', {
                body: message,
                icon: '/static/favicon.ico'
            });
        }
    }

    updateUserStatus(userId, isOnline) {
        const userElement = document.querySelector(`[data-user-id="${userId}"]`);
        if (userElement) {
            const statusElement = userElement.querySelector('.user-status');
            if (statusElement) {
                if (isOnline) {
                    statusElement.innerHTML = '<span class="status-online">Онлайн</span>';
                } else {
                    statusElement.innerHTML = '<span class="status-offline">Оффлайн</span>';
                }
            }
        }
    }
    
    async initializeBlockUI() {
        console.log('=== initializeBlockUI called ===');
        
        // Get current chat user from URL
        const urlParams = new URLSearchParams(window.location.search);
        const currentChatUserId = urlParams.get('user');
        
        if (!currentChatUserId) {
            console.log('No chat user in URL, skipping block UI initialization');
            return;
        }
        
        console.log('Initializing block UI for user:', currentChatUserId);
        console.log('Current URL:', window.location.href);
        
        try {
            // Fetch actual block status from server
            const url = `/users/block-status/${currentChatUserId}`;
            console.log('Fetching block status from:', url);
            
            const response = await fetch(url);
            console.log('Response status:', response.status);
            console.log('Response ok:', response.ok);
            
            if (response.ok) {
                const data = await response.json();
                console.log('Response data:', data);
                const isBlocked = data.is_blocked;
                console.log('Block status from server:', isBlocked);
                
                // Update UI based on actual server status
                this.updateBlockButton(currentChatUserId, isBlocked);
            } else {
                console.error('Failed to fetch block status:', response.status);
                const errorText = await response.text();
                console.error('Error response:', errorText);
                // Fallback to checking existing UI elements
                this.initializeBlockUIFallback(currentChatUserId);
            }
        } catch (error) {
            console.error('Error fetching block status:', error);
            console.error('Error details:', error.message);
            // Fallback to checking existing UI elements
            this.initializeBlockUIFallback(currentChatUserId);
        }
    }
    
    initializeBlockUIFallback(userId) {
        console.log('Using fallback block UI initialization for user:', userId);
        
        // Check if user is blocked by looking at the existing button
        const blockButton = document.querySelector('.block-btn');
        const unblockButton = document.querySelector('.unblock-btn');
        
        if (blockButton) {
            console.log('Found block button, user is not blocked');
            this.updateBlockButton(userId, false);
        } else if (unblockButton) {
            console.log('Found unblock button, user is blocked');
            this.updateBlockButton(userId, true);
        } else {
            console.log('No block/unblock button found, assuming user is not blocked');
            this.updateBlockButton(userId, false);
        }
    }
    
    updateChatInput(isBlocked) {
        console.log('updateChatInput called with isBlocked:', isBlocked);
        
        const chatInput = document.querySelector('.chat-input');
        console.log('Found chat input element:', chatInput);
        
        if (chatInput) {
            if (isBlocked) {
                console.log('Setting blocked input');
                chatInput.innerHTML = `
                    <div class="blocked-input" style="background: rgba(220, 53, 69, 0.1); border: 1px solid #dc3545; border-radius: 8px; padding: 1rem; text-align: center; color: #dc3545;">
                        <i class="fas fa-ban" style="font-size: 1.5rem; margin-bottom: 0.5rem;"></i>
                        <div style="font-weight: 600; margin-bottom: 0.5rem;">Чат заблокирован</div>
                        <div style="font-size: 0.9rem;">Вы не можете отправлять сообщения этому пользователю</div>
                    </div>
                `;
            } else {
                console.log('Setting normal input');
                chatInput.innerHTML = `
                    <div class="input-group">
                        <textarea 
                            id="message-input" 
                            class="message-input" 
                            placeholder="Введите сообщение..."
                            rows="1"
                        ></textarea>
                        <button id="send-btn" class="send-btn">
                            Отправить <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                `;
                
                // Re-setup event listeners for the new input
                setTimeout(() => {
                    const messageInput = document.getElementById('message-input');
                    const sendBtn = document.getElementById('send-btn');
                    
                    console.log('Re-setting up event listeners');
                    console.log('Found message input:', messageInput);
                    console.log('Found send button:', sendBtn);
                    
                    if (messageInput) {
                        messageInput.addEventListener('keydown', (e) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                this.sendMessage();
                            }
                        });
                        
                        messageInput.addEventListener('input', () => {
                            this.autoResizeTextarea(messageInput);
                        });
                    }
                    
                    if (sendBtn) {
                        sendBtn.addEventListener('click', (e) => {
                            e.preventDefault();
                            this.sendMessage();
                        });
                    }
                }, 100);
            }
        } else {
            console.error('Chat input element not found!');
        }
    }
    
    blockUserFromButton(button) {
        const userId = button.getAttribute('data-user-id');
        console.log('Blocking user from button:', userId);
        
        if (!userId) {
            this.showNotification('Ошибка: не удалось определить пользователя', 'danger');
            return;
        }
        
        const currentUrl = window.location.href;
        fetch(`/users/block/${userId}?redirect_to=${encodeURIComponent(currentUrl)}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        }).then(response => {
            if (response.ok) {
                // Обновляем кнопку без перезагрузки страницы
                this.updateBlockButton(userId, true);
                this.updateChatInput(true);
                // Показываем уведомление
                this.showNotification('Пользователь заблокирован', 'success');
            } else {
                this.showNotification('Ошибка при блокировке пользователя', 'danger');
            }
        }).catch(error => {
            console.error('Error:', error);
            this.showNotification('Ошибка сети', 'danger');
        });
    }
    
    unblockUserFromButton(button) {
        const userId = button.getAttribute('data-user-id');
        console.log('Unblocking user from button:', userId);
        
        if (!userId) {
            this.showNotification('Ошибка: не удалось определить пользователя', 'danger');
            return;
        }
        
        const currentUrl = window.location.href;
        fetch(`/users/unblock/${userId}?redirect_to=${encodeURIComponent(currentUrl)}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        }).then(response => {
            if (response.ok) {
                // Обновляем кнопку без перезагрузки страницы
                this.updateBlockButton(userId, false);
                this.updateChatInput(false);
                // Показываем уведомление
                this.showNotification('Пользователь разблокирован', 'success');
            } else {
                this.showNotification('Ошибка при разблокировке пользователя', 'danger');
            }
        }).catch(error => {
            console.error('Error:', error);
            this.showNotification('Ошибка сети', 'danger');
        });
    }
}

// Initialize chat when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const chat = new ModernChat();
    
    // Set current user from template data
    const currentUserElement = document.getElementById('current-user-data');
    const currentUserId = currentUserElement?.dataset?.userId;
    console.log('Current user element:', currentUserElement);
    console.log('Raw currentUserId from data attribute:', currentUserId);
    
    if (currentUserId) {
        chat.currentUser = parseInt(currentUserId);
        console.log('Current user set from template:', chat.currentUser);
    } else {
        console.error('Current user ID not found in template!');
        // Try to get from URL or other sources
        const urlParams = new URLSearchParams(window.location.search);
        const userFromUrl = urlParams.get('user');
        if (userFromUrl) {
            console.log('Trying to get current user from URL:', userFromUrl);
            // This might be the other user, not current user
        }
        
        // Try to get from debug info in template
        const debugScript = document.querySelector('script');
        if (debugScript && debugScript.textContent.includes('current_user_id:')) {
            console.log('Found debug script:', debugScript.textContent);
        }
    }
    
    // Add additional event listeners for user items and send button
    setTimeout(() => {
        console.log('Adding additional event listeners for user items');
        document.querySelectorAll('.user-item').forEach((item, index) => {
            console.log(`Setting up listener for user item ${index}:`, item.dataset);
            item.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                const userId = item.dataset.userId;
                const username = item.dataset.username;
                console.log('User clicked (additional):', userId, username);
                chat.selectUser(userId, username);
            });
        });
        
        // Also setup send button listener
        const sendBtn = document.getElementById('send-btn');
        if (sendBtn) {
            console.log('Setting up send button listener in DOMContentLoaded');
            sendBtn.addEventListener('click', (e) => {
                console.log('Send button clicked (DOMContentLoaded)');
                e.preventDefault();
                e.stopPropagation();
                chat.sendMessage();
            });
        } else {
            console.log('Send button not found in DOMContentLoaded');
        }
        
        // Also setup message input listener
        const messageInput = document.getElementById('message-input');
        if (messageInput) {
            console.log('Setting up message input listener in DOMContentLoaded');
            messageInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    console.log('Enter pressed in message input (DOMContentLoaded)');
                    e.preventDefault();
                    chat.sendMessage();
                }
            });
        } else {
            console.log('Message input not found in DOMContentLoaded');
        }
    }, 200);
    
    // Restore chat state from URL or localStorage
    const urlParams = new URLSearchParams(window.location.search);
    const savedChatUser = urlParams.get('user');
    
    if (savedChatUser) {
        // Find the user element and trigger selection
        const userElement = document.querySelector(`[data-user-id="${savedChatUser}"]`);
        if (userElement) {
            const username = userElement.dataset.username;
            chat.selectUser(savedChatUser, username);
        }
    } else {
        // If no user in URL, check if we're on a chat page
        const chatTitle = document.querySelector('.chat-title');
        if (chatTitle && chatTitle.textContent.includes('Чат с')) {
            // We're on a chat page, initialize with current chat user
            const otherUserId = document.querySelector('.chat-title')?.textContent?.match(/Чат с (.+)/)?.[1];
            if (otherUserId) {
                // Find the user element for this username
                const userElement = document.querySelector(`[data-username="${otherUserId}"]`);
                if (userElement) {
                    const userId = userElement.dataset.userId;
                    const username = userElement.dataset.username;
                    console.log('Initializing chat with current page user:', userId, username);
                    chat.currentChatUser = parseInt(userId);
                    chat.loadChatHistory(userId, username);
                    chat.initializeWebSocket();
                }
            }
        }
    }
});

// Export for potential use in other scripts
window.ModernChat = ModernChat; 