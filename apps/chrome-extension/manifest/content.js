
// Sophia AI Platform Integration Content Script
(function() {
    console.log('Sophia AI Platform Integration loaded');

    // Add Sophia AI button to GitHub issues
    if (window.location.hostname === 'github.com') {
        addGitHubIntegration();
    }

    // Add Sophia AI button to Linear issues
    if (window.location.hostname.includes('linear.app')) {
        addLinearIntegration();
    }

    // Add Sophia AI button to Jira issues
    if (window.location.hostname.includes('atlassian.net')) {
        addJiraIntegration();
    }

    function addGitHubIntegration() {
        const issueHeader = document.querySelector('.gh-header-actions');
        if (issueHeader && !document.querySelector('.sophia-ai-button')) {
            const sophiaButton = createSophiaButton('Send to Sophia AI', () => {
                const issueData = extractGitHubIssueData();
                sendToSophiaAI('github', issueData);
            });
            issueHeader.appendChild(sophiaButton);
        }
    }

    function addLinearIntegration() {
        // Wait for Linear to load
        setTimeout(() => {
            const issueActions = document.querySelector('[data-testid="issue-actions"]');
            if (issueActions && !document.querySelector('.sophia-ai-button')) {
                const sophiaButton = createSophiaButton('Sophia AI', () => {
                    const issueData = extractLinearIssueData();
                    sendToSophiaAI('linear', issueData);
                });
                issueActions.appendChild(sophiaButton);
            }
        }, 2000);
    }

    function createSophiaButton(text, onClick) {
        const button = document.createElement('button');
        button.textContent = text;
        button.className = 'sophia-ai-button';
        button.style.cssText = `
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            margin-left: 8px;
            transition: all 0.3s ease;
        `;

        button.addEventListener('click', onClick);
        button.addEventListener('mouseover', () => {
            button.style.transform = 'translateY(-2px)';
            button.style.boxShadow = '0 4px 8px rgba(0,0,0,0.2)';
        });
        button.addEventListener('mouseout', () => {
            button.style.transform = 'translateY(0)';
            button.style.boxShadow = 'none';
        });

        return button;
    }

    function extractGitHubIssueData() {
        return {
            title: document.querySelector('.js-issue-title')?.textContent?.trim(),
            description: document.querySelector('.comment-body')?.textContent?.trim(),
            labels: Array.from(document.querySelectorAll('.IssueLabel')).map(l => l.textContent.trim()),
            assignee: document.querySelector('.assignee')?.textContent?.trim(),
            url: window.location.href
        };
    }

    function extractLinearIssueData() {
        return {
            title: document.querySelector('[data-testid="issue-title"]')?.textContent?.trim(),
            description: document.querySelector('[data-testid="issue-description"]')?.textContent?.trim(),
            status: document.querySelector('[data-testid="issue-status"]')?.textContent?.trim(),
            assignee: document.querySelector('[data-testid="issue-assignee"]')?.textContent?.trim(),
            url: window.location.href
        };
    }

    function sendToSophiaAI(platform, data) {
        // Show notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #28a745;
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            z-index: 10000;
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
        `;
        notification.textContent = `Sending to Sophia AI...`;
        document.body.appendChild(notification);

        // Send to background script
        chrome.runtime.sendMessage({
            action: 'sendToSophia',
            platform: platform,
            data: data
        }, (response) => {
            notification.textContent = response.success ?
                '✅ Sent to Sophia AI!' :
                '❌ Failed to send to Sophia AI';

            setTimeout(() => {
                notification.remove();
            }, 3000);
        });
    }
})();
