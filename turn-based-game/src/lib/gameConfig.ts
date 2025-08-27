import level1Data from './level1.json';
import level2Data from './level2.json';
import level3Data from './level3.json';

export interface GameConfig {
  tileSize: number;
  backgroundColor: string;
  width: number;
  height: number;
  zoom: number;
}

export const GAME_CONFIG: GameConfig = {
  tileSize: 64,
  backgroundColor: '#2c3e50',
  width: 1000,
  height: 800,
  zoom: 0.9
};

export interface TileMapping {
  [key: string]: { x: number; y: number };
}

// Direct mapping from tile symbols to UV coordinates
export const TILE_UV_MAPPING = {
  'C': { tileset: 'tileset', uMin: 0.5, uMax: 1.0, vMin: 0.0, vMax: 0.5 }, // computer
  '#': { tileset: 'tileset', uMin: 0.0, uMax: 0.5, vMin: 0.5, vMax: 1.0 }, // platform
  '|': { tileset: 'tileset', uMin: 0.5, uMax: 1.0, vMin: 0.5, vMax: 1.0 }, // ladder
  '░': { tileset: 'tileset', uMin: 0.0, uMax: 0.5, vMin: 0.0, vMax: 0.5 }, // empty
  'B': { tileset: 'tileset2', uMin: 0.0, uMax: 0.5, vMin: 0.0, vMax: 0.5 }, // button
  'Z': { tileset: 'tileset2', uMin: 0.0, uMax: 0.5, vMin: 0.5, vMax: 1.0 }, // bridge up (impassable)
  'T': { tileset: 'tileset2', uMin: 0.5, uMax: 1.0, vMin: 0.5, vMax: 1.0 }  // bridge down (passable)
};

export const LEVELS = [
  {
    id: 1,
    name: 'Level 1',
    data: level1Data,
    description: 'Simple level with a computer and a ladder'
  },
  {
    id: 2,
    name: 'Level 2',
    data: level2Data,
    description: 'Level with a computer and a ladder, but the computer is in a different position'
  },
  {
    id: 3,
    name: 'Level 3',
    data: level3Data,
    description: 'Co-op puzzle! Two agents, buttons (B) and bridges (Z). Press E on buttons!'
  }
];