/**
 * Main Application Logic for Phantom Link BBS
 * Integrates WebSocketClient, CommandLineBar, ChatDisplay, and SidePanel
 * Requirements: 5.1, 5.2, 5.3, 6.3, 6.4, 6.5, 7.1, 7.2, 7.3, 7.5, 9.3
 */

import { CommandLineBar } from './commandBar.js';
import { ChatDisplay } from './chatDisplay.js';
import { SidePanel } from './sidePanel.js';

// Application state
let wsClient = null;
let commandBar = null;
let chatDisplay = null;
let sidePanel = null;
let currentRoom = 'Lobby';
let activeUsers = [];

/**
 * Initialize the application
 */
function init() {
    // Check if user is authenticated
    const token = localStorage.getItem('jwt_token');
    
    if (!token) {
        // Redirect to auth page if no token
        window.location.href = '/auth.html';
        return;
    }
    
    // Initialize ChatDisplay
    chatDisplay = new ChatDisplay('chatDisplay');
    
    // Clear the initial connecting message
    chatDisplay.clear();
    
    // Initialize CommandLineBar with message and command handlers
    commandBar = new CommandLineBar(
        handleMessageSubmit,
        handleCommandSubmit
    );
    
    // Initialize SidePanel with room click handler (Requirement 4.3, 6.3, 6.4)
    sidePanel = new SidePanel('sidePanel', handleSidePanelRoomClick);
    
    // Initialize WebSocketClient
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws`;
    
    // Note: WebSocketClient is loaded as a global from websocket.js
    wsClient = new WebSocketClient(wsUrl);
    
    // Register WebSocket event handlers
    wsClient.onMessage(handleWebSocketMessage);
    wsClient.onConnect(handleWebSocketConnect);
    wsClient.onDisconnect(handleWebSocketDisconnect);
    
    // Listen for WebSocket status events
    window.addEventListener('ws-status', handleWebSocketStatus);
    
    // Connect to WebSocket server
    wsClient.connect();
    
    // Display connecting message
    chatDisplay.addMessage({
        type: 'system',
        content: 'Connecting to Phantom Link BBS...'
    });
}

/**
 * Handle regular message submission
 * @param {string} message - The message text
 */
function handleMessageSubmit(message) {
    if (!wsClient || !wsClient.isConnected()) {
        chatDisplay.addMessage({
            type: 'error',
            content: 'Not connected to server. Please wait...'
        });
        return;
    }
    
    // Send chat message via WebSocket (Requirement 5.1)
    wsClient.send({
        type: 'chat_message',
        content: message,
        room: currentRoom
    });
}

/**
 * Handle command submission
 * @param {string} command - The command name (without /)
 * @param {Array<string>} args - Command arguments
 * @param {string} fullInput - The full input string
 */
function handleCommandSubmit(command, args, fullInput) {
    if (!wsClient || !wsClient.isConnected()) {
        chatDisplay.addMessage({
            type: 'error',
            content: 'Not connected to server. Please wait...'
        });
        return;
    }
    
    // Handle client-side commands
    switch (command) {
        case 'clear':
            // Clear the terminal display (Requirement 7.4)
            chatDisplay.clear();
            break;
            
        case 'panel':
            // Toggle side panel visibility
            if (sidePanel) {
                sidePanel.toggle();
                const status = sidePanel.isHidden() ? 'hidden' : 'visible';
                chatDisplay.addMessage({
                    type: 'system',
                    content: `Side panel ${status}`
                });
            }
            break;
            
        case 'help':
            // Send help command to server (Requirement 7.1)
            wsClient.send({
                type: 'command',
                command: 'help'
            });
            break;
            
        case 'rooms':
            // Send rooms command to server (Requirement 7.2)
            wsClient.send({
                type: 'command',
                command: 'rooms'
            });
            break;
            
        case 'users':
            // Send users command to server (Requirement 7.3)
            wsClient.send({
                type: 'command',
                command: 'users'
            });
            break;
            
        case 'join':
            // Join a room
            if (args.length === 0) {
                chatDisplay.addMessage({
                    type: 'error',
                    content: 'Usage: /join <room_name>'
                });
            } else {
                const roomName = args.join(' ');
                wsClient.send({
                    type: 'join_room',
                    room: roomName
                });
            }
            break;
            
        case 'disconnect':
            // Manually disconnect
            wsClient.disconnect();
            chatDisplay.addMessage({
                type: 'system',
                content: 'Disconnected from server'
            });
            break;
            
        case 'reconnect':
            // Manually reconnect
            chatDisplay.addMessage({
                type: 'system',
                content: 'Attempting to reconnect...'
            });
            wsClient.reconnect();
            break;
            
        default:
            // Unknown command - send to server for handling (Requirement 7.5)
            wsClient.send({
                type: 'command',
                command: command,
                args: args
            });
            break;
    }
}

/**
 * Handle incoming WebSocket messages
 * Route messages to appropriate handlers (Requirement 9.3)
 * @param {Object} message - The message object from server
 */
function handleWebSocketMessage(message) {
    switch (message.type) {
        case 'chat_message':
            handleChatMessage(message);
            break;
            
        case 'system':
            handleSystemMessage(message);
            break;
            
        case 'error':
            handleErrorMessage(message);
            break;
            
        case 'user_list':
            handleUserList(message);
            break;
            
        case 'room_list':
            handleRoomList(message);
            break;
            
        case 'room_change':
            handleRoomChange(message);
            break;
            
        case 'help':
            handleHelpMessage(message);
            break;
            
        default:
            console.warn('Unknown message type:', message.type);
            break;
    }
}

/**
 * Handle chat messages (Requirement 5.2, 5.3)
 * @param {Object} message - Chat message object
 */
function handleChatMessage(message) {
    chatDisplay.addMessage({
        type: 'chat_message',
        username: message.username,
        content: message.content,
        timestamp: message.timestamp
    });
}

/**
 * Handle system messages
 * @param {Object} message - System message object
 */
function handleSystemMessage(message) {
    chatDisplay.addMessage({
        type: 'system',
        content: message.content,
        timestamp: message.timestamp
    });
}

/**
 * Handle error messages (Requirement 7.5)
 * @param {Object} message - Error message object
 */
function handleErrorMessage(message) {
    chatDisplay.addMessage({
        type: 'error',
        content: message.content,
        timestamp: message.timestamp
    });
}

/**
 * Handle user list updates (Requirement 6.3, 6.4)
 * @param {Object} message - User list message
 */
function handleUserList(message) {
    activeUsers = message.users || [];
    
    // Update side panel with active users (Requirement 6.3, 6.4)
    if (sidePanel) {
        sidePanel.updateUsers(activeUsers);
    }
    
    // Display active users list in chat if content is provided
    if (message.content) {
        chatDisplay.addMessage({
            type: 'system',
            content: message.content
        });
    }
}

/**
 * Handle room list (Requirement 7.2)
 * @param {Object} message - Room list message
 */
function handleRoomList(message) {
    const rooms = message.rooms || [];
    
    // Update side panel with rooms (Requirement 7.2)
    if (sidePanel) {
        sidePanel.updateRooms(rooms);
    }
    
    // Display room list with user counts in chat if content is provided
    if (message.content) {
        chatDisplay.addMessage({
            type: 'system',
            content: message.content
        });
    }
}

/**
 * Handle room change notification (Requirement 6.5)
 * @param {Object} message - Room change message
 */
function handleRoomChange(message) {
    if (message.room) {
        currentRoom = message.room;
        
        // Update side panel to highlight current room (Requirement 6.5)
        if (sidePanel) {
            sidePanel.highlightCurrentRoom(currentRoom);
        }
    }
    
    chatDisplay.addMessage({
        type: 'system',
        content: message.content || `You are now in: ${currentRoom}`,
        timestamp: message.timestamp
    });
}

/**
 * Handle help command response (Requirement 7.1)
 * @param {Object} message - Help message
 */
function handleHelpMessage(message) {
    chatDisplay.addMessage({
        type: 'system',
        content: message.content,
        timestamp: message.timestamp
    });
}

/**
 * Handle room click from side panel (Requirement 4.3)
 * @param {string} roomName - Name of the room to join
 */
function handleSidePanelRoomClick(roomName) {
    if (!wsClient || !wsClient.isConnected()) {
        chatDisplay.addMessage({
            type: 'error',
            content: 'Not connected to server. Please wait...'
        });
        return;
    }
    
    // Send join room request via WebSocket
    wsClient.send({
        type: 'join_room',
        room: roomName
    });
}

/**
 * Handle WebSocket connection established
 * @param {Event} event - Connection event
 */
function handleWebSocketConnect(event) {
    chatDisplay.addMessage({
        type: 'system',
        content: 'Connected to Phantom Link BBS'
    });
    
    // Enable command bar
    commandBar.enable();
    
    // Side panel will be automatically populated by server-sent room_list and user_list messages
}

/**
 * Handle WebSocket disconnection
 * @param {Event} event - Disconnection event
 */
function handleWebSocketDisconnect(event) {
    chatDisplay.addMessage({
        type: 'system',
        content: 'Disconnected from server'
    });
    
    // Disable command bar during disconnection
    commandBar.disable();
}

/**
 * Handle WebSocket status events
 * @param {CustomEvent} event - Status event
 */
function handleWebSocketStatus(event) {
    const { message, type } = event.detail;
    
    chatDisplay.addMessage({
        type: type === 'error' ? 'error' : 'system',
        content: message
    });
}

/**
 * Handle logout
 */
function logout() {
    // Disconnect WebSocket
    if (wsClient) {
        wsClient.disconnect();
    }
    
    // Clear token
    localStorage.removeItem('jwt_token');
    
    // Redirect to auth page
    window.location.href = '/auth.html';
}

// Initialize application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Export for testing or external use
export {
    init,
    handleMessageSubmit,
    handleCommandSubmit,
    handleWebSocketMessage,
    handleSidePanelRoomClick,
    logout
};
