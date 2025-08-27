import { NextRequest, NextResponse } from 'next/server';

// Store connected SSE clients
const clients = new Set<ReadableStreamDefaultController>();

// Simple incremental id for messages
let lastMessageId = 0;

type AgentMessage = {
  type?: string;
  text: string;
  timestamp?: number;
};

function broadcast(payload: any) {
  const message = `data: ${JSON.stringify(payload)}\n\n`;
  const encoded = new TextEncoder().encode(message);
  clients.forEach((controller) => {
    try {
      controller.enqueue(encoded);
    } catch (error) {
      clients.delete(controller);
    }
  });
}

export async function GET(request: NextRequest) {
  const stream = new ReadableStream({
    start(controller) {
      clients.add(controller);

      // Send initial ready event
      const initial = {
        type: 'agent_stream_ready',
        timestamp: Date.now()
      };
      controller.enqueue(new TextEncoder().encode(`data: ${JSON.stringify(initial)}\n\n`));

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
      'Connection': 'keep-alive'
    }
  });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const action = body?.action as 'add' | 'update_last';
    const message = (body?.message || {}) as AgentMessage;

    if (!action) {
      return NextResponse.json({ success: false, error: 'Missing action' }, { status: 400 });
    }

    if (action === 'add') {
      lastMessageId += 1;
      const payload = {
        type: 'agent_message_add',
        id: lastMessageId,
        message: {
          text: message.text,
          type: message.type || 'info',
          timestamp: message.timestamp ?? Date.now()
        }
      };
      broadcast(payload);
      return NextResponse.json({ success: true, id: lastMessageId });
    }

    if (action === 'update_last') {
      if (lastMessageId === 0) {
        return NextResponse.json({ success: false, error: 'No messages to update' }, { status: 400 });
      }
      const payload = {
        type: 'agent_message_update',
        id: lastMessageId,
        message: {
          text: message.text,
          type: message.type || 'info',
          timestamp: message.timestamp ?? Date.now()
        }
      };
      broadcast(payload);
      return NextResponse.json({ success: true, id: lastMessageId });
    }

    return NextResponse.json({ success: false, error: 'Unsupported action' }, { status: 400 });
  } catch (error) {
    return NextResponse.json({ success: false, error: 'Invalid request body' }, { status: 400 });
  }
}


