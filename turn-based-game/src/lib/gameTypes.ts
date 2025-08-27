export interface Position {
  x: number;
  y: number;
}

export interface Character {
  id: string;
  name: string;
  position: Position;
  health: number;
  maxHealth: number;
  attack: number;
  moveRange: number;
  attackRange: number;
  isPlayer: boolean;
  team: 'red' | 'blue';
}

export interface GameField {
  width: number;
  height: number;
  characters: Character[];
  obstacles: Position[];
}

export interface GameState {
  field: GameField;
  currentTurn: 'red' | 'blue';
  gameStatus: 'setup' | 'playing' | 'finished';
  winner?: 'red' | 'blue';
  turnNumber: number;
}

export type Direction = 'up' | 'down' | 'left' | 'right';

export interface MoveRequest {
  direction: Direction;
}

export interface AttackRequest {
  target: Position;
}

export interface GameSettings {
  redPlayerHP: number;
  bluePlayerHP: number;
  moveRange: number;
  attackRange: number;
  obstacleCount: number;
}

export interface EndTurnRequest {
  team: 'red' | 'blue';
}

export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

// New types for character movement system
export type TileType = 'platform' | 'ladder' | 'empty' | 'computer' | 'agent';

export type ActionType = 'multi_move[left]' | 'multi_move[right]' | 'multi_move[up]' | 'multi_move[down]' | 'use_pc' | 'use_button';

export interface MoveStepResult {
  result: boolean;
  available_actions: ActionType[];
  reason?: string;
  position?: Position;
  level_completed?: boolean;
}

export interface MultiMoveRequest {
  direction: 'left' | 'right' | 'up' | 'down';
  steps: number;
  agentIndex?: number; // Optional agent index (defaults to 0)
}

export interface MultiMoveResponse {
  success: boolean;
  steps: MoveStepResult[];
  final_position: Position;
  level_completed: boolean;
}

export interface LevelCharacter {
  id: string;
  position: Position;
  sprite?: string;
}

export interface LevelData {
  size: {
    width: number;
    height: number;
  };
  legend: {
    [key: string]: string;
  };
  layout: string[];
  character?: LevelCharacter;
}

// WebSocket message types
export interface WebSocketMessage {
  type: string;
  timestamp: number;
}

export interface PositionUpdateMessage extends WebSocketMessage {
  type: 'position_update';
  position: Position;
}

export interface EventsResponse {
  position: Position;
  timestamp: number;
  message?: string;
} 