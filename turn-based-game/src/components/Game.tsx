'use client';

import { useRef } from 'react';
import { PhaserGame, IRefPhaserGame } from './PhaserGame';

interface LevelData {
  id: number;
  name: string;
  data: {
    size: { width: number; height: number };
    starting_position: { x: number; y: number };
    legend: { [key: string]: string };
    layout: string[];
  };
  description: string;
}

interface GameProps {
  selectedLevel: LevelData;
  onBackToMenu?: () => void;
}

export default function Game({ selectedLevel, onBackToMenu }: GameProps) {
  const phaserRef = useRef<IRefPhaserGame>(null);

  const currentActiveScene = (scene: Phaser.Scene) => {
    console.log('Current active scene:', scene);
    console.log('Game controls: WASD to move, E to interact with computer');
    console.log('Playing level:', selectedLevel.name);
  };

  return (
    <div className="w-full h-full bg-gray-800 flex items-center justify-center">
      <PhaserGame
        ref={phaserRef}
        currentActiveScene={currentActiveScene}
        selectedLevel={selectedLevel}
        onBackToMenu={onBackToMenu}
      />
    </div>
  );
} 