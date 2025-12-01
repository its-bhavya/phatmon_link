/**
 * Side Panel Component for Phantom Link BBS
 * Displays rooms and active users with real-time updates
 * Requirements: 4.3, 6.3, 6.4, 7.2, 7.3
 */

export class SidePanel {
    /**
     * Initialize the side panel
     * @param {string} panelId - ID of the side panel container
     * @param {Function} onRoomClick - Callback when a room is clicked
     */
    constructor(panelId, onRoomClick) {
        this.panel = document.getElementById(panelId);
        this.roomsList = document.getElementById('roomsList');
        this.usersList = document.getElementById('usersList');
        this.toggleButton = document.getElementById('panelToggle');
        this.expandButton = document.getElementById('expandButton');
        this.onRoomClick = onRoomClick;
        
        this.currentRoom = 'Lobby';
        this.rooms = [];
        this.users = [];
        this.isCollapsed = false;
        
        this.init();
    }
    
    /**
     * Initialize event listeners
     */
    init() {
        // Toggle button click handler
        if (this.toggleButton) {
            this.toggleButton.addEventListener('click', () => {
                this.toggle();
            });
        }
        
        // Expand button click handler
        if (this.expandButton) {
            this.expandButton.addEventListener('click', () => {
                this.show();
            });
        }
        
        // Keyboard shortcut: Alt+P to toggle panel
        document.addEventListener('keydown', (e) => {
            if (e.altKey && e.key === 'p') {
                e.preventDefault();
                this.toggle();
            }
        });
    }
    
    /**
     * Toggle panel visibility
     */
    toggle() {
        this.isCollapsed = !this.isCollapsed;
        
        if (this.isCollapsed) {
            this.panel.classList.add('collapsed');
            if (this.expandButton) {
                this.expandButton.classList.add('visible');
            }
        } else {
            this.panel.classList.remove('collapsed');
            if (this.expandButton) {
                this.expandButton.classList.remove('visible');
            }
        }
    }
    
    /**
     * Show the panel
     */
    show() {
        this.isCollapsed = false;
        this.panel.classList.remove('collapsed');
        if (this.expandButton) {
            this.expandButton.classList.remove('visible');
        }
    }
    
    /**
     * Hide the panel
     */
    hide() {
        this.isCollapsed = true;
        this.panel.classList.add('collapsed');
        if (this.expandButton) {
            this.expandButton.classList.add('visible');
        }
    }
    
    /**
     * Update rooms list with counts
     * @param {Array} rooms - Array of room objects with name and count
     * Requirements: 7.2
     */
    updateRooms(rooms) {
        this.rooms = rooms;
        
        if (!this.roomsList) return;
        
        // Clear existing rooms
        this.roomsList.innerHTML = '';
        
        if (!rooms || rooms.length === 0) {
            this.roomsList.innerHTML = '<div class="room-item loading">No rooms available</div>';
            return;
        }
        
        // Create room items
        rooms.forEach(room => {
            const roomItem = document.createElement('div');
            roomItem.className = 'room-item';
            roomItem.dataset.roomName = room.name;
            
            // Highlight current room
            if (room.name === this.currentRoom) {
                roomItem.classList.add('active');
            }
            
            // Room name and count
            const roomName = document.createElement('span');
            roomName.className = 'room-name';
            roomName.textContent = room.name;
            
            const roomCount = document.createElement('span');
            roomCount.className = 'room-count';
            roomCount.textContent = `(${room.count})`;
            
            roomItem.appendChild(roomName);
            roomItem.appendChild(roomCount);
            
            // Click handler to join room
            roomItem.addEventListener('click', () => {
                if (room.name !== this.currentRoom) {
                    this.handleRoomClick(room.name);
                }
            });
            
            this.roomsList.appendChild(roomItem);
        });
    }
    
    /**
     * Update active users list
     * @param {Array} users - Array of user objects with username and room
     * Requirements: 6.3, 6.4, 7.3
     */
    updateUsers(users) {
        this.users = users;
        
        if (!this.usersList) return;
        
        // Clear existing users
        this.usersList.innerHTML = '';
        
        if (!users || users.length === 0) {
            this.usersList.innerHTML = '<div class="user-item loading">No users online</div>';
            return;
        }
        
        // Create user items
        users.forEach(user => {
            const userItem = document.createElement('div');
            userItem.className = 'user-item';
            
            // User name
            const userName = document.createElement('span');
            userName.className = 'user-name';
            userName.textContent = user.username;
            
            // User room
            const userRoom = document.createElement('span');
            userRoom.className = 'user-room';
            userRoom.textContent = `[${user.room}]`;
            
            userItem.appendChild(userName);
            userItem.appendChild(userRoom);
            
            this.usersList.appendChild(userItem);
        });
    }
    
    /**
     * Handle room click - join room via WebSocket
     * @param {string} roomName - Name of the room to join
     * Requirements: 4.3
     */
    handleRoomClick(roomName) {
        if (this.onRoomClick) {
            this.onRoomClick(roomName);
        }
    }
    
    /**
     * Highlight current room in the list
     * @param {string} roomName - Name of the current room
     */
    highlightCurrentRoom(roomName) {
        this.currentRoom = roomName;
        
        if (!this.roomsList) return;
        
        // Remove active class from all rooms
        const allRooms = this.roomsList.querySelectorAll('.room-item');
        allRooms.forEach(item => {
            item.classList.remove('active');
        });
        
        // Add active class to current room
        const currentRoomItem = this.roomsList.querySelector(`[data-room-name="${roomName}"]`);
        if (currentRoomItem) {
            currentRoomItem.classList.add('active');
        }
    }
    
    /**
     * Get current room name
     * @returns {string} Current room name
     */
    getCurrentRoom() {
        return this.currentRoom;
    }
    
    /**
     * Check if panel is collapsed
     * @returns {boolean} True if collapsed
     */
    isHidden() {
        return this.isCollapsed;
    }
}
