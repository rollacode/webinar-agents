import { gameState } from '@/lib/gameState';
import { NextRequest, NextResponse } from 'next/server';
import { broadcastPositionUpdate } from '../../character/events/route';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { levelData } = body;

    if (!levelData || !levelData.size || !levelData.layout || !levelData.starting_position) {
      return NextResponse.json({
        success: false,
        error: 'Invalid level data. Need size, layout, and starting_position'
      }, { status: 400 });
    }

    // Set the current level on the server
    gameState.setCurrentLevel(levelData);

    // Set position to the level's starting position
    gameState.setPosition(levelData.starting_position);

    // Broadcast the position update to all clients
    broadcastPositionUpdate();

    return NextResponse.json({
      success: true,
      data: {
        message: 'Level set successfully',
        levelSize: levelData.size,
        startingPosition: levelData.starting_position,
        currentPosition: gameState.getPosition()
      }
    });

  } catch (error) {
    console.error('Error setting level:', error);
    return NextResponse.json({
      success: false,
      error: 'Failed to set level'
    }, { status: 500 });
  }
} 