import { Character, Direction, GameSettings, GameState, Position } from './gameTypes';

// Default game settings
let gameSettings: GameSettings = {
  redPlayerHP: 10,
  bluePlayerHP: 10,
  moveRange: 3,
  attackRange: 2,
  obstacleCount: 8
};

// Game state (in a real app, this would be in a database)
const gameState: GameState = {
  field: {
    width: 12,
    height: 8,
    characters: [],
    obstacles: []
  },
  currentTurn: 'red',
  gameStatus: 'setup',
  turnNumber: 1
};

// Initialize game with random obstacles
function initializeGame() {
  const obstacles: Position[] = [];

  // Generate random obstacles
  while (obstacles.length < gameSettings.obstacleCount) {
    const x = Math.floor(Math.random() * gameState.field.width);
    const y = Math.floor(Math.random() * gameState.field.height);

    // Don't place obstacles on starting positions
    if ((x === 0 && y === 3) || (x === 11 && y === 4)) continue;
    if (obstacles.some(obs => obs.x === x && obs.y === y)) continue;

    obstacles.push({ x, y });
  }

  gameState.field = {
    width: 12,
    height: 8,
    characters: [
      {
        id: 'red-player',
        name: 'Red Hero',
        position: { x: 0, y: 3 },
        health: gameSettings.redPlayerHP,
        maxHealth: gameSettings.redPlayerHP,
        attack: 3,
        moveRange: gameSettings.moveRange,
        attackRange: gameSettings.attackRange,
        isPlayer: true,
        team: 'red'
      },
      {
        id: 'blue-player',
        name: 'Blue Hero',
        position: { x: 11, y: 4 },
        health: gameSettings.bluePlayerHP,
        maxHealth: gameSettings.bluePlayerHP,
        attack: 3,
        moveRange: gameSettings.moveRange,
        attackRange: gameSettings.attackRange,
        isPlayer: false,
        team: 'blue'
      }
    ],
    obstacles
  };
  gameState.currentTurn = 'red';
  gameState.gameStatus = 'playing';
  gameState.turnNumber = 1;
}

export function getGameState(): GameState {
  if (gameState.field.characters.length === 0) {
    initializeGame();
  }
  return { ...gameState };
}

export function updateGameSettings(settings: Partial<GameSettings>): void {
  gameSettings = { ...gameSettings, ...settings };
  if (gameState.gameStatus === 'setup') {
    initializeGame();
  }
}

export function getGameSettings(): GameSettings {
  return { ...gameSettings };
}

export function isValidPosition(position: Position): boolean {
  const { x, y } = position;
  return x >= 0 && x < gameState.field.width && y >= 0 && y < gameState.field.height;
}

export function isPositionOccupied(position: Position): boolean {
  // Check for obstacles
  if (gameState.field.obstacles.some(obs => obs.x === position.x && obs.y === position.y)) {
    return true;
  }

  // Check for other characters
  return gameState.field.characters.some(char =>
    char.position.x === position.x && char.position.y === position.y
  );
}

export function moveCharacterToPosition(characterId: string, newPosition: Position): boolean {
  const character = gameState.field.characters.find(c => c.id === characterId);
  if (!character) return false;

  // Check if it's the character's turn
  if (character.team !== gameState.currentTurn) return false;

  // Check if position is within move range
  const distance = Math.abs(character.position.x - newPosition.x) +
    Math.abs(character.position.y - newPosition.y);

  if (distance > character.moveRange) return false;

  if (!isValidPosition(newPosition) || isPositionOccupied(newPosition)) {
    return false;
  }

  character.position = newPosition;
  return true;
}

export function moveCharacter(characterId: string, direction: Direction): boolean {
  const character = gameState.field.characters.find(c => c.id === characterId);
  if (!character) return false;

  const newPosition = getNewPosition(character.position, direction);
  return moveCharacterToPosition(characterId, newPosition);
}

export function getNewPosition(position: Position, direction: Direction): Position {
  switch (direction) {
    case 'up': return { x: position.x, y: position.y - 1 };
    case 'down': return { x: position.x, y: position.y + 1 };
    case 'left': return { x: position.x - 1, y: position.y };
    case 'right': return { x: position.x + 1, y: position.y };
    default: return position;
  }
}

export function attackTarget(attackerId: string, targetPosition: Position): boolean {
  const attacker = gameState.field.characters.find(c => c.id === attackerId);
  if (!attacker) return false;

  // Check if it's the attacker's turn
  if (attacker.team !== gameState.currentTurn) return false;

  const target = gameState.field.characters.find(c =>
    c.position.x === targetPosition.x && c.position.y === targetPosition.y
  );

  if (!target || target.id === attackerId || target.team === attacker.team) return false;

  // Check if target is within attack range
  const distance = Math.abs(attacker.position.x - target.position.x) +
    Math.abs(attacker.position.y - target.position.y);

  if (distance > attacker.attackRange) return false;

  target.health = Math.max(0, target.health - attacker.attack);

  // Check for game over
  if (target.health === 0) {
    gameState.gameStatus = 'finished';
    gameState.winner = attacker.team;
  }

  return true;
}

export function getCharactersInRange(position: Position, range: number): Character[] {
  return gameState.field.characters.filter(char => {
    const distance = Math.abs(char.position.x - position.x) +
      Math.abs(char.position.y - position.y);
    return distance <= range;
  });
}

export function endTurn(team: 'red' | 'blue'): boolean {
  if (gameState.currentTurn !== team || gameState.gameStatus !== 'playing') {
    return false;
  }

  // Switch turns
  gameState.currentTurn = team === 'red' ? 'blue' : 'red';
  gameState.turnNumber++;

  return true;
}

export function getValidMovePositions(characterId: string): Position[] {
  const character = gameState.field.characters.find(c => c.id === characterId);
  if (!character || character.team !== gameState.currentTurn) return [];

  const validPositions: Position[] = [];
  const { x: charX, y: charY } = character.position;

  for (let x = 0; x < gameState.field.width; x++) {
    for (let y = 0; y < gameState.field.height; y++) {
      const distance = Math.abs(x - charX) + Math.abs(y - charY);
      if (distance <= character.moveRange && distance > 0) {
        if (isValidPosition({ x, y }) && !isPositionOccupied({ x, y })) {
          validPositions.push({ x, y });
        }
      }
    }
  }

  return validPositions;
}

export function getValidAttackPositions(characterId: string): Position[] {
  const character = gameState.field.characters.find(c => c.id === characterId);
  if (!character || character.team !== gameState.currentTurn) return [];

  const validPositions: Position[] = [];
  const { x: charX, y: charY } = character.position;

  gameState.field.characters.forEach(target => {
    if (target.team !== character.team) {
      const distance = Math.abs(target.position.x - charX) + Math.abs(target.position.y - charY);
      if (distance <= character.attackRange) {
        validPositions.push(target.position);
      }
    }
  });

  return validPositions;
} 