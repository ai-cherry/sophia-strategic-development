import React, { useState, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { Box, Typography, CircularProgress, Paper, IconButton, Tooltip } from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import SettingsIcon from '@mui/icons-material/Settings';
import FullscreenIcon from '@mui/icons-material/Fullscreen';
import FullscreenExitIcon from '@mui/icons-material/FullscreenExit';

/**
 * AG-UI Retool Embed Component
 *
 * Embeds the Agno UI within a Retool dashboard
 */
const AgUIRetoolEmbed = ({
  agentId = 'default',
  height = 600,
  width = '100%',
  title = 'Sophia AI Assistant',
  defaultInstructions = [
    'You are Sophia AI, an enterprise AI assistant for Pay Ready',
    'You have access to various tools to help you accomplish tasks',
    'Always provide clear, concise responses',
    'When using tools, explain your reasoning'
  ],
  showToolbar = true,
  darkMode = false,
  apiEndpoint = '/api/agno'
}) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [agentStats, setAgentStats] = useState(null);
  const containerRef = useRef(null);
  const iframeRef = useRef(null);

  // Initialize the agent on component mount
  useEffect(() => {
    const initializeAgent = async () => {
      try {
        setLoading(true);
        setError(null);

        // Check if agent exists or create it
        const response = await fetch(`${apiEndpoint}/agents`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            agent_id: agentId,
            instructions: defaultInstructions
          }),
        });

        if (!response.ok) {
          throw new Error(`Failed to initialize agent: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('Agent initialized:', data);

        // Get agent stats
        await fetchAgentStats();

        setLoading(false);
      } catch (err) {
        console.error('Error initializing agent:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    initializeAgent();

    // Cleanup function
    return () => {
      // Any cleanup needed
    };
  }, [agentId, apiEndpoint]);

  // Fetch agent stats
  const fetchAgentStats = async () => {
    try {
      const response = await fetch(`${apiEndpoint}/stats`);
      if (!response.ok) {
        throw new Error(`Failed to fetch agent stats: ${response.statusText}`);
      }

      const data = await response.json();
      setAgentStats(data.stats);
    } catch (err) {
      console.error('Error fetching agent stats:', err);
      // Don't set error state here to avoid disrupting the UI
    }
  };

  // Handle refresh
  const handleRefresh = () => {
    if (iframeRef.current) {
      iframeRef.current.src = iframeRef.current.src;
    }
    fetchAgentStats();
  };

  // Handle fullscreen toggle
  const toggleFullscreen = () => {
    if (!isFullscreen) {
      if (containerRef.current.requestFullscreen) {
        containerRef.current.requestFullscreen();
      } else if (containerRef.current.mozRequestFullScreen) {
        containerRef.current.mozRequestFullScreen();
      } else if (containerRef.current.webkitRequestFullscreen) {
        containerRef.current.webkitRequestFullscreen();
      } else if (containerRef.current.msRequestFullscreen) {
        containerRef.current.msRequestFullscreen();
      }
      setIsFullscreen(true);
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      } else if (document.mozCancelFullScreen) {
        document.mozCancelFullScreen();
      } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen();
      } else if (document.msExitFullscreen) {
        document.msExitFullscreen();
      }
      setIsFullscreen(false);
    }
  };

  // Listen for fullscreen change events
  useEffect(() => {
    const handleFullscreenChange = () => {
      setIsFullscreen(
        document.fullscreenElement ||
        document.mozFullScreenElement ||
        document.webkitFullscreenElement ||
        document.msFullscreenElement
      );
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('mozfullscreenchange', handleFullscreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange);
    document.addEventListener('msfullscreenchange', handleFullscreenChange);

    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
      document.removeEventListener('mozfullscreenchange', handleFullscreenChange);
      document.removeEventListener('webkitfullscreenchange', handleFullscreenChange);
      document.removeEventListener('msfullscreenchange', handleFullscreenChange);
    };
  }, []);

  // Construct the iframe URL
  const iframeUrl = `/ag-ui/?agent=${encodeURIComponent(agentId)}&theme=${darkMode ? 'dark' : 'light'}`;

  return (
    <Paper
      ref={containerRef}
      elevation={3}
      sx={{
        width: isFullscreen ? '100vw' : width,
        height: isFullscreen ? '100vh' : height,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        bgcolor: darkMode ? '#1a1a1a' : '#ffffff',
        color: darkMode ? '#ffffff' : '#000000',
      }}
    >
      {showToolbar && (
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            p: 1,
            borderBottom: 1,
            borderColor: darkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
          }}
        >
          <Typography variant="h6" component="div">
            {title}
          </Typography>

          <Box sx={{ display: 'flex', gap: 1 }}>
            {agentStats && (
              <Tooltip title={`Agent pool: ${agentStats.pool_size}/${agentStats.max_pool_size}`}>
                <Typography variant="body2" sx={{ alignSelf: 'center', mr: 1 }}>
                  {agentId}
                </Typography>
              </Tooltip>
            )}

            <Tooltip title="Refresh">
              <IconButton onClick={handleRefresh} size="small" color="inherit">
                <RefreshIcon />
              </IconButton>
            </Tooltip>

            <Tooltip title="Settings">
              <IconButton size="small" color="inherit">
                <SettingsIcon />
              </IconButton>
            </Tooltip>

            <Tooltip title={isFullscreen ? "Exit Fullscreen" : "Fullscreen"}>
              <IconButton onClick={toggleFullscreen} size="small" color="inherit">
                {isFullscreen ? <FullscreenExitIcon /> : <FullscreenIcon />}
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      )}

      <Box sx={{ flexGrow: 1, position: 'relative' }}>
        {loading ? (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
            }}
          >
            <CircularProgress size={40} />
            <Typography variant="body1" sx={{ mt: 2 }}>
              Initializing Sophia AI...
            </Typography>
          </Box>
        ) : error ? (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              p: 3,
            }}
          >
            <Typography variant="h6" color="error" gutterBottom>
              Error
            </Typography>
            <Typography variant="body1" align="center">
              {error}
            </Typography>
            <Box sx={{ mt: 2 }}>
              <button onClick={handleRefresh}>Retry</button>
            </Box>
          </Box>
        ) : (
          <iframe
            ref={iframeRef}
            src={iframeUrl}
            title="Sophia AI Assistant"
            width="100%"
            height="100%"
            frameBorder="0"
            allow="microphone; camera"
            style={{ border: 'none' }}
          />
        )}
      </Box>
    </Paper>
  );
};

AgUIRetoolEmbed.propTypes = {
  agentId: PropTypes.string,
  height: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  width: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  title: PropTypes.string,
  defaultInstructions: PropTypes.arrayOf(PropTypes.string),
  showToolbar: PropTypes.bool,
  darkMode: PropTypes.bool,
  apiEndpoint: PropTypes.string,
};

export default AgUIRetoolEmbed;
