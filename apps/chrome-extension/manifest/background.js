
// Sophia AI Background Script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'sendToSophia') {
        sendToSophiaAI(request.platform, request.data)
            .then(result => sendResponse({success: true, result}))
            .catch(error => sendResponse({success: false, error: error.message}));
        return true; // Required for async response
    }
});

async function sendToSophiaAI(platform, data) {
    try {
        const response = await fetch('http://localhost:8000/api/platform-integration', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                platform: platform,
                data: data,
                action: 'context_import'
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Failed to send to Sophia AI:', error);
        throw error;
    }
}

// Context menu integration
chrome.contextMenus.create({
    id: 'sendToSophia',
    title: 'Send to Sophia AI',
    contexts: ['selection']
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === 'sendToSophia') {
        chrome.tabs.sendMessage(tab.id, {
            action: 'sendSelection',
            text: info.selectionText
        });
    }
});
