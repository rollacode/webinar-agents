'use client';

import { useState } from 'react';
import Game from './Game';
import { LEVELS } from '@/lib/gameConfig';

export default function MainMenu() {
  const [showGame, setShowGame] = useState(false);
  const [selectedLevel, setSelectedLevel] = useState(LEVELS[0]);

  console.log('MainMenu render - showGame:', showGame, 'selectedLevel:', selectedLevel);

  if (showGame) {
    console.log('Rendering Game component with level:', selectedLevel);
    return (
      <div className="w-full h-screen">
        <div className="absolute top-4 left-4 z-10">
          <button
            onClick={() => setShowGame(false)}
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded shadow-lg transition-colors duration-200"
          >
            Back to Menu
          </button>
        </div>
        <Game 
          selectedLevel={selectedLevel} 
          onBackToMenu={() => setShowGame(false)} 
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900 flex items-center justify-center">
      <div className="text-center bg-gray-800 p-8 rounded-2xl shadow-2xl border border-gray-700 max-w-md w-full mx-4">
        {/* Title */}
        <h1 className="text-4xl font-bold text-white mb-2">AI Agents Game</h1>
        
        {/* Level Selector */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">Select Level</h2>
          <div className="space-y-3">
            {LEVELS.map((level) => (
              <div
                key={level.id}
                onClick={() => setSelectedLevel(level)}
                className={`
                  cursor-pointer p-5 rounded-lg border-2 transition-all duration-200 hover:scale-105
                  ${selectedLevel.id === level.id 
                    ? 'border-green-500 bg-green-500/20 shadow-lg shadow-green-500/25' 
                    : 'border-gray-600 bg-gray-700/50 hover:border-gray-500 hover:bg-gray-700'
                  }
                `}
              >
                <div className="flex items-center justify-between">
                  <div className="text-left">
                    <h3 className="font-bold text-white text-lg">{level.name}</h3>
                    <p className="text-gray-300 text-sm">{level.description}</p>
                  </div>
                  <div className={`
                    w-4 h-4 rounded-full border-2 transition-all duration-200
                    ${selectedLevel.id === level.id 
                      ? 'border-green-500 bg-green-500' 
                      : 'border-gray-500'
                    }
                  `}>
                    {selectedLevel.id === level.id && (
                      <div className="w-2 h-2 bg-white rounded-full m-0.5"></div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Start Button */}
        <button
          onClick={() => setShowGame(true)}
          className="w-full bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white font-bold py-4 px-8 rounded-lg text-xl shadow-lg hover:shadow-xl transition-all duration-200 transform hover:scale-105"
        >
          Start {selectedLevel.name}
        </button>
      </div>
    </div>
  );
} 