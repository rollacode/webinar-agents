import { gameState } from '@/lib/gameState';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const computerCheck = gameState.canUseComputer();

    if (!computerCheck.canUse) {
      return NextResponse.json({
        success: false,
        error: computerCheck.reason || 'Cannot use computer'
      }, { status: 400 });
    }

    // Computer used successfully - level completed!
    return NextResponse.json({
      success: true,
      data: {
        message: 'Computer accessed successfully!',
        level_completed: true,
        position: gameState.getPosition(),
        victory: true
      }
    });

  } catch (error) {
    return NextResponse.json({
      success: false,
      error: 'Failed to use computer'
    }, { status: 500 });
  }
}

export async function GET() {
  return NextResponse.json({
    success: true,
    message: 'Use computer endpoint',
    usage: 'POST /api/character/use-pc',
    description: 'Use computer when standing on it or adjacent to it'
  });
} 