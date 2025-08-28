'use client';

import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

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
  const liveListRef = useRef<HTMLDivElement | null>(null);

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

  // Auto-scroll live stream to the latest message
  useEffect(() => {
    const el = liveListRef.current;
    if (el) {
      el.scrollTop = el.scrollHeight;
    }
  }, [liveMessages]);

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

  return (
    <div className="fixed top-0 right-0 bg-white shadow-lg w-96 h-screen flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-800">🤖 AI Agent</h3>
        <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}
          title={isConnected ? 'Connected' : 'Disconnected'} />
      </div>

      {/* Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Status and Controls */}
        <div className="p-4 space-y-3 border-b border-gray-200">
          {/* Connection Status */}
          <div className="text-sm text-gray-600">
            Status: {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
          </div>

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
            <div className="max-h-32 overflow-y-auto text-xs space-y-1">
              {agentStatus.results.slice(-5).map((result, index) => (
                <div key={index} className="text-black">
                  <span className="text-gray-400">[{formatTimestamp(result.timestamp)}]</span>
                  {result.type === 'action' && (
                    <span> {result.action} {result.success ? '✅' : '❌'}</span>
                  )}
                  {result.message && <span> {result.message}</span>}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Live Agent Stream - Full Height Chat */}
        <div className="flex-1 overflow-hidden">
          <div ref={liveListRef} className="h-full overflow-y-auto p-4 space-y-3">
            {liveMessages.map((m) => (
              <div key={m.id} className={`text-sm ${m.type === 'action' ? 'text-gray-600' : 'text-black'}`}>
                <div className="text-gray-400 text-xs mb-1">
                  [{new Date(m.timestamp).toLocaleTimeString()}]
                </div>
                <div className={`prose prose-sm max-w-none ${m.type === 'action' ? 'text-gray-600' : 'text-black'}`}>
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      // Custom styling for markdown elements
                      p: ({ children }) => <p className="mb-2">{children}</p>,
                      code: ({ children, className }) => (
                        <code className={`${className} bg-gray-100 px-1 py-0.5 rounded text-xs`}>
                          {children}
                        </code>
                      ),
                      pre: ({ children }) => (
                        <pre className="bg-gray-100 p-2 rounded text-xs overflow-x-auto mb-2">
                          {children}
                        </pre>
                      ),
                      ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                      ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
                      li: ({ children }) => <li className="text-sm">{children}</li>,
                      strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                      em: ({ children }) => <em className="italic">{children}</em>,
                      blockquote: ({ children }) => (
                        <blockquote className="border-l-4 border-gray-300 pl-3 italic text-gray-600 mb-2">
                          {children}
                        </blockquote>
                      ),
                      h1: ({ children }) => <h1 className="text-lg font-bold mb-2">{children}</h1>,
                      h2: ({ children }) => <h2 className="text-base font-bold mb-2">{children}</h2>,
                      h3: ({ children }) => <h3 className="text-sm font-bold mb-1">{children}</h3>,
                    }}
                  >
                    {m.text}
                  </ReactMarkdown>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
