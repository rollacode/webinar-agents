'use client';

import { useState, useEffect } from 'react';

interface AgentStatus {
  running: boolean;
  results: Array<{
    timestamp: number;
    type: string;
    message?: string;
    action?: string;
    success?: boolean;
    turn?: number;
  }>;
}

export default function AgentControls() {
  const [agentStatus, setAgentStatus] = useState<AgentStatus | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [liveMessages, setLiveMessages] = useState<Array<{ id: number; text: string; type: string; timestamp: number }>>([]);

  const AGENT_SERVER_URL = 'http://localhost:5001';

  // Test connection to agent server
  const testConnection = async () => {
    try {
      const response = await fetch(`${AGENT_SERVER_URL}/api/agent/test`);
      const data = await response.json();
      setIsConnected(data.success);
      return data;
    } catch (error) {
      setIsConnected(false);
      console.error('Failed to connect to agent server:', error);
      return null;
    }
  };

  // Get agent status
  const getAgentStatus = async () => {
    try {
      const response = await fetch(`${AGENT_SERVER_URL}/api/agent/status`);
      const data = await response.json();
      setAgentStatus(data);
    } catch (error) {
      console.error('Failed to get agent status:', error);
    }
  };

  // Start agent
  const startAgent = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${AGENT_SERVER_URL}/api/agent/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      if (data.success) {
        console.log('Agent started successfully');
        // Start polling for status updates
        const statusInterval = setInterval(getAgentStatus, 1000);
        setTimeout(() => clearInterval(statusInterval), 60000); // Stop after 1 minute
      } else {
        console.error('Failed to start agent:', data.error);
      }
    } catch (error) {
      console.error('Error starting agent:', error);
    } finally {
      setLoading(false);
    }
  };

  // Stop agent
  const stopAgent = async () => {
    try {
      const response = await fetch(`${AGENT_SERVER_URL}/api/agent/stop`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      if (data.success) {
        console.log('Agent stopped successfully');
        getAgentStatus();
      } else {
        console.error('Failed to stop agent:', data.error);
      }
    } catch (error) {
      console.error('Error stopping agent:', error);
    }
  };

  useEffect(() => {
    testConnection();
    const interval = setInterval(testConnection, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (agentStatus?.running) {
      const interval = setInterval(getAgentStatus, 1000);
      return () => clearInterval(interval);
    }
  }, [agentStatus?.running]);

  // Subscribe to live agent events via SSE
  useEffect(() => {
    const eventSource = new EventSource('/api/agent/events');

    eventSource.onopen = () => {
      console.log('Agent SSE connected');
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'agent_message_add') {
          setLiveMessages((prev) => [
            ...prev,
            { id: data.id, text: data.message.text, type: data.message.type, timestamp: data.message.timestamp }
          ].slice(-50));
        } else if (data.type === 'agent_message_update') {
          setLiveMessages((prev) => prev.map((m) => (
            m.id === data.id ? { ...m, text: data.message.text, type: data.message.type, timestamp: data.message.timestamp } : m
          )));
        }
      } catch (e) {
        console.error('Failed to parse agent SSE event', e);
      }
    };

    eventSource.onerror = (e) => {
      console.error('Agent SSE error', e);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, []);

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleTimeString();
  };

  const getStatusColor = (type: string) => {
    switch (type) {
      case 'success': return 'text-green-500';
      case 'error': return 'text-red-500';
      case 'warning': return 'text-yellow-500';
      case 'action': return 'text-blue-500';
      default: return 'text-gray-500';
    }
  };

  return (
    <div className="fixed top-4 right-4 bg-white rounded-lg shadow-lg p-4 w-80 max-h-96 overflow-hidden">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">🤖 AI Agent</h3>
        <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}
          title={isConnected ? 'Connected' : 'Disconnected'} />
      </div>

      <div className="space-y-3">
        {/* Connection Status */}
        <div className="text-sm text-gray-600">
          Status: {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
        </div>

        {/* Agent Status */}
        {agentStatus && (
          <div className="text-sm">
            <div className="font-medium">
              Agent: {agentStatus.running ? '🟢 Running' : '⚪ Stopped'}
            </div>
          </div>
        )}

        {/* Control Buttons */}
        <div className="flex space-x-2">
          <button
            onClick={startAgent}
            disabled={!isConnected || loading || agentStatus?.running}
            className={`px-3 py-1 text-sm rounded ${!isConnected || loading || agentStatus?.running
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-green-500 text-white hover:bg-green-600'
              }`}
          >
            {loading ? 'Starting...' : 'Start Agent'}
          </button>

          <button
            onClick={stopAgent}
            disabled={!agentStatus?.running}
            className={`px-3 py-1 text-sm rounded ${!agentStatus?.running
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-red-500 text-white hover:bg-red-600'
              }`}
          >
            Stop Agent
          </button>
        </div>

        {/* Results Log */}
        {agentStatus?.results && agentStatus.results.length > 0 && (
          <div className="mt-3">
            <div className="text-sm font-medium text-gray-700 mb-2">Recent Actions:</div>
            <div className="max-h-32 overflow-y-auto text-xs space-y-1">
              {agentStatus.results.slice(-5).map((result, index) => (
                <div key={index} className={`${getStatusColor(result.type)}`}>
                  <span className="text-gray-400">[{formatTimestamp(result.timestamp)}]</span>
                  {result.type === 'action' && (
                    <span> {result.action} {result.success ? '✅' : '❌'}</span>
                  )}
                  {result.message && <span> {result.message}</span>}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Live Agent Stream */}
        <div className="mt-3">
          <div className="max-h-40 overflow-y-auto text-xs space-y-1">
            {liveMessages.map((m) => (
              <div key={m.id} className={`${getStatusColor(m.type)}`}>
                <span className="text-gray-400">[{new Date(m.timestamp).toLocaleTimeString()}]</span>
                <span> {m.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
