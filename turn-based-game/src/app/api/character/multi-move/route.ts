import { gameState } from '@/lib/gameState';
import { MoveStepResult, MultiMoveRequest, MultiMoveResponse } from '@/lib/gameTypes';
import { NextRequest, NextResponse } from 'next/server';
import { broadcastPositionUpdate } from '../events/route';

export async function POST(request: NextRequest) {
  try {
    const body: MultiMoveRequest = await request.json();
    const { direction, steps, agentIndex = 0 } = body;

    if (!direction || typeof steps !== 'number' || steps < 1 || steps > 10) {
      return NextResponse.json({
        success: false,
        error: 'Invalid request. Need direction and steps (1-10)'
      }, { status: 400 });
    }

    // Validate agent index
    if (agentIndex < 0 || agentIndex >= gameState.getAgentCount()) {
      return NextResponse.json({
        success: false,
        error: `Invalid agent index. Must be between 0 and ${gameState.getAgentCount() - 1}`
      }, { status: 400 });
    }

    const stepResults: MoveStepResult[] = [];
    let currentPos = gameState.getPosition(agentIndex);
    let levelCompleted = false;

    // Direction vectors
    const directionMap = {
      'left': { x: -1, y: 0 },
      'right': { x: 1, y: 0 },
      'up': { x: 0, y: -1 },
      'down': { x: 0, y: 1 }
    };

    const delta = directionMap[direction];

    // Process each step
    for (let i = 0; i < steps; i++) {
      const nextPos = {
        x: currentPos.x + delta.x,
        y: currentPos.y + delta.y
      };

      const moveCheck = gameState.canMoveToPosition(nextPos);

      if (moveCheck.canMove) {
        currentPos = nextPos;
        gameState.setPosition(currentPos, agentIndex);

        // Broadcast position update to WebSocket clients
        broadcastPositionUpdate();

        const targetTile = gameState.getEffectiveTileAt(currentPos.x, currentPos.y);

        // Check if reached computer
        if (targetTile === 'C') {
          levelCompleted = true;
          // Don't broadcast computer interaction here - only when actually using the computer
        }

        const availableActions = gameState.getAvailableActions();

        stepResults.push({
          result: true,
          available_actions: availableActions,
          position: { ...currentPos },
          level_completed: levelCompleted
        });

        // If reached computer, stop moving
        if (levelCompleted) {
          break;
        }
      } else {
        stepResults.push({
          result: false,
          available_actions: gameState.getAvailableActions(),
          reason: moveCheck.reason,
          position: { ...currentPos }
        });
        break; // Stop on first failed move
      }
    }

    const response: MultiMoveResponse = {
      success: true,
      steps: stepResults,
      final_position: currentPos,
      level_completed: levelCompleted
    };

    return NextResponse.json(response);

  } catch (error) {
    return NextResponse.json({
      success: false,
      error: 'Invalid request body'
    }, { status: 400 });
  }
}

// GET endpoint to get current character state
export async function GET() {
  return NextResponse.json({
    success: true,
    data: {
      agents: gameState.getAllAgentPositions(),
      activeAgent: gameState.getActiveAgent(),
      agentCount: gameState.getAgentCount(),
      position: gameState.getPosition(), // Current active agent position
      available_actions: gameState.getAvailableActions()
    }
  });
} 