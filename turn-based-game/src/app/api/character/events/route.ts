import { gameState } from '@/lib/gameState';
import { NextRequest } from 'next/server';

// Store connected SSE clients
const clients = new Set<ReadableStreamDefaultController>();

// Broadcast position updates to all connected clients
export function broadcastPositionUpdate() {
  const message = `data: ${JSON.stringify({
    type: 'position_update',
    agents: gameState.getAllAgentPositions(),
    activeAgent: gameState.getActiveAgent(),
    agentCount: gameState.getAgentCount(),
    position: gameState.getPosition(), // Current active agent position for backward compatibility
    bridgesActivated: gameState.areBridgesActivated(), // Bridge state
    map: gameState.getCurrentLevel().layout,
    timestamp: Date.now()
  })}\n\n`;

  clients.forEach(controller => {
    try {
      controller.enqueue(new TextEncoder().encode(message));
    } catch (error) {
      clients.delete(controller);
    }
  });
}

export async function GET(request: NextRequest) {
  // Server-Sent Events (SSE) implementation
  const stream = new ReadableStream({
    start(controller) {
      // Add client to the set
      clients.add(controller);

      // Send initial position data
      const initialMessage = `data: ${JSON.stringify({
        type: 'position_update',
        agents: gameState.getAllAgentPositions(),
        activeAgent: gameState.getActiveAgent(),
        agentCount: gameState.getAgentCount(),
        position: gameState.getPosition(), // Current active agent position for backward compatibility
        bridgesActivated: gameState.areBridgesActivated(), // Bridge state
        map: gameState.getCurrentLevel().layout,
        timestamp: Date.now()
      })}\n\n`;

      controller.enqueue(new TextEncoder().encode(initialMessage));

      // Handle client disconnect
      request.signal.addEventListener('abort', () => {
        clients.delete(controller);
        controller.close();
      });
    }
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    },
  });
}