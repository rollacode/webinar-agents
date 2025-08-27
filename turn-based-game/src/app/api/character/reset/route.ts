import { gameState } from '@/lib/gameState';
import { NextResponse } from 'next/server';
import { broadcastPositionUpdate } from '../events/route';

export async function POST() {
  try {
    // Get starting position from current level
    const currentLevel = gameState.getCurrentLevel();
    const startingPosition = currentLevel.starting_position;
    
    gameState.setPosition(startingPosition);
    
    // Broadcast the position reset to all clients
    broadcastPositionUpdate();
    
    return NextResponse.json({
      success: true,
      data: {
        message: 'Character position reset to starting position',
        position: startingPosition,
        currentLevel: currentLevel
      }
    });
    
  } catch (error) {
    return NextResponse.json({
      success: false,
      error: 'Failed to reset character position'
    }, { status: 500 });
  }
} 