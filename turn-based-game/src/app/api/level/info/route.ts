import { gameState } from '@/lib/gameState';
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const currentLevel = gameState.getCurrentLevel();
    const currentPosition = gameState.getPosition();
    
    if (!currentLevel) {
      return NextResponse.json({
        success: false,
        error: 'No level currently set'
      }, { status: 404 });
    }
    
    return NextResponse.json({
      success: true,
      data: {
        level: currentLevel,
        currentPosition: currentPosition
      }
    });
    
  } catch (error) {
    console.error('Error getting level info:', error);
    return NextResponse.json({
      success: false,
      error: 'Failed to get level info'
    }, { status: 500 });
  }
}
