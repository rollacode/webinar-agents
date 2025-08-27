import { gameState } from '@/lib/gameState';
import { NextRequest, NextResponse } from 'next/server';
import { broadcastPositionUpdate } from '../events/route';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { agentIndex } = body;

    if (typeof agentIndex !== 'number' || agentIndex < 0 || agentIndex >= gameState.getAgentCount()) {
      return NextResponse.json({
        success: false,
        error: `Invalid agent index. Must be between 0 and ${gameState.getAgentCount() - 1}`
      }, { status: 400 });
    }

    // Switch to the specified agent
    gameState.setActiveAgent(agentIndex);
    
    // Broadcast position update to reflect the change
    broadcastPositionUpdate();
    
    return NextResponse.json({
      success: true,
      data: {
        message: `Switched to agent ${agentIndex}`,
        activeAgent: gameState.getActiveAgent(),
        position: gameState.getPosition(),
        agentCount: gameState.getAgentCount(),
        allAgents: gameState.getAllAgentPositions()
      }
    });
    
  } catch (error) {
    return NextResponse.json({
      success: false,
      error: 'Failed to switch agent'
    }, { status: 500 });
  }
} 