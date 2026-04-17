class ChatApp {
    constructor() {
        this.messagesContainer = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.clearButton = document.getElementById('clearButton');
        this.themeToggle = document.getElementById('themeToggle');
        this.emptyState = document.getElementById('emptyState');
        
        this.messages = this.loadMessages();
        this.isTyping = false;
        
        this.init();
    }
    
    init() {
        // Event listeners
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        this.clearButton.addEventListener('click', () => this.clearChat());
        this.themeToggle.addEventListener('click', () => this.toggleTheme());
        
        // Auto-resize textarea
        this.messageInput.addEventListener('input', () => {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = this.messageInput.scrollHeight + 'px';
        });
        
        // Suggestion cards
        document.querySelectorAll('.suggestion-card').forEach(card => {
            card.addEventListener('click', () => {
                const text = card.querySelector('.suggestion-card-text').textContent;
                this.messageInput.value = text;
                this.messageInput.focus();
            });
        });
        
        // Load theme
        this.loadTheme();
        
        // Render existing messages
        this.renderMessages();
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isTyping) return;
        
        // Add user message
        this.addMessage('user', message);
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            
            // Remove typing indicator and add bot response
            this.hideTypingIndicator();
            this.addMessage('bot', data.response);
            
        } catch (error) {
            console.error('Error:', error);
            this.hideTypingIndicator();
            this.addMessage('bot', 'Sorry, I encountered an error. Please try again.');
        }
    }
    
    addMessage(role, content) {
        const message = { role, content, timestamp: Date.now() };
        this.messages.push(message);
        this.saveMessages();
        this.renderMessage(message);
        this.scrollToBottom();
        this.hideEmptyState();
    }
    
    renderMessages() {
        this.messagesContainer.innerHTML = '';
        if (this.messages.length === 0) {
            this.showEmptyState();
        } else {
            this.hideEmptyState();
            this.messages.forEach(message => this.renderMessage(message));
            this.scrollToBottom();
        }
    }
    
    renderMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.role}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = message.role === 'user' ? '👤' : '🤖';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        content.innerHTML = this.formatMessage(message.content);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        this.messagesContainer.appendChild(messageDiv);
    }
    
    formatMessage(text) {
        // Simple markdown-like formatting
        let formatted = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
        
        // Convert URLs to links
        formatted = formatted.replace(
            /(https?:\/\/[^\s]+)/g,
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );
        
        return formatted;
    }
    
    showTypingIndicator() {
        this.isTyping = true;
        this.sendButton.disabled = true;
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot';
        typingDiv.id = 'typingIndicator';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = '🤖';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        
        const indicator = document.createElement('div');
        indicator.className = 'typing-indicator';
        indicator.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
        
        content.appendChild(indicator);
        typingDiv.appendChild(avatar);
        typingDiv.appendChild(content);
        
        this.messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }
    
    hideTypingIndicator() {
        this.isTyping = false;
        this.sendButton.disabled = false;
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }
    
    clearChat() {
        if (confirm('Are you sure you want to clear all messages?')) {
            this.messages = [];
            this.saveMessages();
            this.renderMessages();
        }
    }
    
    toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        // Update icon
        this.themeToggle.textContent = newTheme === 'dark' ? '☀️' : '🌙';
    }
    
    loadTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        document.documentElement.setAttribute('data-theme', savedTheme);
        this.themeToggle.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
    }
    
    saveMessages() {
        localStorage.setItem('chatMessages', JSON.stringify(this.messages));
    }
    
    loadMessages() {
        const saved = localStorage.getItem('chatMessages');
        return saved ? JSON.parse(saved) : [];
    }
    
    showEmptyState() {
        this.emptyState.style.display = 'flex';
    }
    
    hideEmptyState() {
        this.emptyState.style.display = 'none';
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});
