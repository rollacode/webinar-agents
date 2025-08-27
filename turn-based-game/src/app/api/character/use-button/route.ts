import { gameState } from '@/lib/gameState';
import { NextRequest, NextResponse } from 'next/server';
import { broadcastPositionUpdate } from '../events/route';

export async function POST(request: NextRequest) {
  try {
    const buttonCheck = gameState.canUseButton();

    if (!buttonCheck.canUse) {
      return NextResponse.json({
        success: false,
        error: buttonCheck.reason || 'Cannot use button'
      }, { status: 400 });
    }

    // Button pressed - activate bridges!
    gameState.activateBridges();
    
    // Broadcast update to all clients immediately
    broadcastPositionUpdate();

    return NextResponse.json({
      success: true,
      data: {
        message: 'Button pressed! Bridges activated!',
        bridgesActivated: gameState.areBridgesActivated(),
        position: gameState.getPosition()
      }
    });

  } catch (error) {
    return NextResponse.json({
      success: false,
      error: 'Failed to use button'
    }, { status: 500 });
  }
} 