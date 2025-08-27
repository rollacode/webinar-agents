import { ActionType, Position } from './gameTypes';
import level1Data from './level1.json';

interface LevelData {
  size: { width: number; height: number };
  starting_position: { x: number; y: number };
  starting_position_2?: { x: number; y: number }; // Optional second agent
  legend: { [key: string]: string };
  layout: string[];
}

// Shared character state (in real app would be database/Redis/etc)
class GameState {
  private agents: Position[] = [level1Data.starting_position]; // Array of agent positions
  private activeAgent: number = 0; // Index of currently active agent
  private currentLevel: LevelData = level1Data; // Default to level1
  private bridgesActivated: boolean = false; // Track if bridges are activated

  getPosition(agentIndex?: number): Position {
    const index = agentIndex !== undefined ? agentIndex : this.activeAgent;
    if (index < 0 || index >= this.agents.length) {
      return { x: 0, y: 0 };
    }
    return { ...this.agents[index] };
  }

  setPosition(newPosition: Position, agentIndex?: number): void {
    const index = agentIndex !== undefined ? agentIndex : this.activeAgent;
    this.agents[index] = { ...newPosition };
  }

  // Get all agent positions
  getAllAgentPositions(): Position[] {
    return this.agents.map(pos => ({ ...pos }));
  }

  // Switch active agent
  setActiveAgent(index: number): void {
    if (index >= 0 && index < this.agents.length) {
      this.activeAgent = index;
    }
  }

  getActiveAgent(): number {
    return this.activeAgent;
  }

  // Get number of agents
  getAgentCount(): number {
    return this.agents.length;
  }

  // Set the current level data
  setCurrentLevel(levelData: LevelData): void {
    this.currentLevel = levelData;

    // Initialize agents based on level data
    this.agents = [levelData.starting_position];
    if (levelData.starting_position_2) {
      this.agents.push(levelData.starting_position_2);
    }

    // Reset to first agent and bridge state
    this.activeAgent = 0;
    this.bridgesActivated = false;
  }

  // Check if agent stepped on a button and activate bridges
  checkForButtonPress(position: Position): boolean {
    const tileAtPosition = this.getTileAt(position.x, position.y);

    if (tileAtPosition === 'B' && !this.bridgesActivated) {
      this.activateBridges();
      return true; // Button was pressed
    }

    return false; // No button press
  }

  getCurrentLevel(): LevelData {
    return this.currentLevel;
  }

  // Helper functions
  getTileAt(x: number, y: number): string {
    if (x < 0 || x >= this.currentLevel.size.width || y < 0 || y >= this.currentLevel.size.height) {
      return '░';
    }
    return this.currentLevel.layout[y][x];
  }

  // Get effective tile (considering bridge state)
  getEffectiveTileAt(x: number, y: number): string {
    const originalTile = this.getTileAt(x, y);

    // If bridges are activated, Z becomes T (passable)
    if (this.bridgesActivated && originalTile === 'Z') {
      return 'T';
    }

    return originalTile;
  }

  // Check if bridges are activated
  areBridgesActivated(): boolean {
    return this.bridgesActivated;
  }

  // Activate all bridges
  activateBridges(): void {
    this.bridgesActivated = true;
    console.log('Bridges activated! Z bridges are now passable.');
  }

  // Reset bridge state
  resetBridges(): void {
    this.bridgesActivated = false;
  }

  getAvailableActions(): ActionType[] {
    const { x, y } = this.getPosition();
    const currentTile = this.getTileAt(x, y);
    const actions: ActionType[] = [];

    // Check what's under our feet
    const groundTile = this.getTileAt(x, y + 1);

    const leftGroundTile = this.getTileAt(x - 1, y + 1);
    const rightGroundTile = this.getTileAt(x + 1, y + 1);

    if (leftGroundTile === '#') {
      actions.push('multi_move[left]');
    }

    if (rightGroundTile === '#') {
      actions.push('multi_move[right]');
    }

    if (currentTile === '|') {
      actions.push('multi_move[up]');
    }

    if (groundTile === '|') {
      actions.push('multi_move[down]');
    }

    const leftTile = this.getTileAt(x - 1, y);
    const rightTile = this.getTileAt(x + 1, y);
    const upTile = this.getTileAt(x, y - 1);
    const downTile = this.getTileAt(x, y + 1);

    if (currentTile === 'C' || leftTile === 'C' || rightTile === 'C' || upTile === 'C' || downTile === 'C') {
      actions.push('use_pc');
    }

    if (currentTile === 'B' || leftTile === 'B' || rightTile === 'B' || upTile === 'B' || downTile === 'B') {
      actions.push('use_button');
    }

    return actions;
  }

  canMoveToPosition(to: Position): { canMove: boolean; reason?: string } {
    const from = this.getPosition();

    if (to.x < 0 || to.x >= this.currentLevel.size.width || to.y < 0 || to.y >= this.currentLevel.size.height) {
      return { canMove: false, reason: 'Out of bounds' };
    }

    const currentTile = this.getEffectiveTileAt(from.x, from.y);
    const targetTile = this.getEffectiveTileAt(to.x, to.y);
    const targetGroundTile = this.getEffectiveTileAt(to.x, to.y + 1);
    const currentGroundTile = this.getEffectiveTileAt(from.x, from.y + 1);

    // Can't move into solid tiles
    if (targetTile === '#' || targetTile === 'Z') {
      return { canMove: false, reason: 'Cannot move through wall/raised bridge' };
    }

    // Horizontal movement
    if (from.y === to.y) {
      // Need platform under target position for horizontal movement
      if (targetGroundTile !== '#' && targetGroundTile !== '|' && targetGroundTile !== 'T') {
        return { canMove: false, reason: 'No platform under target position' };
      }
      return { canMove: true };
    }

    // Vertical movement
    if (from.x === to.x) {
      if (to.y < from.y) {
        // Moving up - must be on ladder
        if (currentTile !== '|') {
          return { canMove: false, reason: 'Must be on ladder to move up' };
        }
        return { canMove: true };
      }

      if (to.y > from.y) {
        // Moving down - need ladder under current position
        if (currentGroundTile !== '|') {
          return { canMove: false, reason: 'No ladder under current position to move down' };
        }
        return { canMove: true };
      }
    }

    return { canMove: false, reason: 'Invalid movement direction' };
  }

  canUseComputer(): { canUse: boolean; reason?: string } {
    const { x, y } = this.getPosition();
    const currentTile = this.getTileAt(x, y);

    if (currentTile === 'C') {
      return { canUse: true };
    }

    const leftTile = this.getTileAt(x - 1, y);
    const rightTile = this.getTileAt(x + 1, y);
    const upTile = this.getTileAt(x, y - 1);
    const downTile = this.getTileAt(x, y + 1);

    if (leftTile === 'C' || rightTile === 'C' || upTile === 'C' || downTile === 'C') {
      return { canUse: true };
    }

    return { canUse: false, reason: 'No computer nearby' };
  }

  canUseButton(): { canUse: boolean; reason?: string } {
    const { x, y } = this.getPosition();
    const currentTile = this.getTileAt(x, y);

    if (currentTile === 'B') {
      return { canUse: true };
    }

    const leftTile = this.getTileAt(x - 1, y);
    const rightTile = this.getTileAt(x + 1, y);
    const upTile = this.getTileAt(x, y - 1);
    const downTile = this.getTileAt(x, y + 1);

    if (leftTile === 'B' || rightTile === 'B' || upTile === 'B' || downTile === 'B') {
      return { canUse: true };
    }

    return { canUse: false, reason: 'No button nearby' };
  }
}

export const gameState = new GameState(); 