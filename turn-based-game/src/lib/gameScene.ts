import { GAME_CONFIG, TILE_UV_MAPPING } from './gameConfig';
import { Position } from './gameTypes';

export interface LevelData {
  size: {
    width: number;
    height: number;
  };
  starting_position: {
    x: number;
    y: number;
  };
  starting_position_2?: {
    x: number;
    y: number;
  };
  legend: {
    [key: string]: string;
  };
  layout: string[];
}

export class GameScene {
  private scene: Phaser.Scene;
  private tileSize: number;
  private levelData: LevelData;
  private agentSprites: Phaser.GameObjects.Sprite[] = [];
  private agentPositions: Position[] = [];
  private serverAgentPositions: Position[] = [];
  private activeAgent: number = 0;
  private agentCount: number = 1;
  private isGameWon: boolean = false;
  private victoryContainer?: Phaser.GameObjects.Container;
  private eventSource?: EventSource;
  private onBackToMenu?: () => void;
  private switchAgentButton?: Phaser.GameObjects.Container;
  private bridgeTiles: { [key: string]: Phaser.GameObjects.Sprite } = {}; // Track bridge tiles for updates
  private agentIndicators: Phaser.GameObjects.Container[] = []; // Green dots above agents
  private lastBridgeState: boolean = false; // Track bridge state for effect triggering
  private offsetX: number = 0; // Level offset X for positioning
  private offsetY: number = 0; // Level offset Y for positioning

  constructor(scene: Phaser.Scene, levelData: LevelData, tileSize: number, onBackToMenu?: () => void) {
    this.scene = scene;
    this.tileSize = tileSize;
    this.levelData = levelData;
    this.onBackToMenu = onBackToMenu;

    // Initialize agents based on level data
    this.agentPositions = [levelData.starting_position];
    this.serverAgentPositions = [levelData.starting_position];

    if (levelData.starting_position_2) {
      this.agentPositions.push(levelData.starting_position_2);
      this.serverAgentPositions.push(levelData.starting_position_2);
      this.agentCount = 2;
    }

    // Notify server about the level change
    this.setLevelOnServer(levelData);
  }

  preload(): void {
    this.scene.load.image('tileset', '/main_tiles.jpg');
    this.scene.load.image('tileset2', '/main_tiles2.jpg');
    this.scene.load.image('agent', '/agent.png');

    // Set texture filtering for better quality
    this.scene.load.on('filecomplete-image-tileset', () => {
      const texture = this.scene.textures.get('tileset');
      texture.setFilter(Phaser.Textures.FilterMode.LINEAR);
    });

    this.scene.load.on('filecomplete-image-tileset2', () => {
      const texture = this.scene.textures.get('tileset2');
      texture.setFilter(Phaser.Textures.FilterMode.LINEAR);
    });

    this.scene.load.on('filecomplete-image-agent', () => {
      const texture = this.scene.textures.get('agent');
      texture.setFilter(Phaser.Textures.FilterMode.LINEAR);
    });
  }

  create(): void {
    const { size, layout } = this.levelData;
    const { width, height } = size;

    const gameContainer = this.scene.add.container(0, 0);

    const levelWidth = width * this.tileSize;
    const levelHeight = height * this.tileSize;

    const screenWidth = this.scene.cameras.main.width;
    const screenHeight = this.scene.cameras.main.height;
    const offsetX = (screenWidth - levelWidth) / 2;
    const offsetY = (screenHeight - levelHeight) / 2;

    // Store offsets for use in other methods
    this.offsetX = offsetX;
    this.offsetY = offsetY;

    this.renderLevel(layout, offsetX, offsetY, gameContainer);
    this.createAgent(offsetX, offsetY, gameContainer);
    this.createAgentIndicators(); // Add agent indicators for multi-agent levels
    this.setupCamera(levelWidth, levelHeight);
    this.setupControls();
    this.setupAgentPositionPolling(offsetX, offsetY);
  }

  private renderLevel(layout: string[], offsetX: number, offsetY: number, container: Phaser.GameObjects.Container): void {
    layout.forEach((row, rowIndex) => {
      row.split('').forEach((tile, colIndex) => {
        const uvCoords = TILE_UV_MAPPING[tile];
        if (uvCoords) {
          const sprite = this.createTile(
            offsetX + colIndex * this.tileSize,
            offsetY + rowIndex * this.tileSize,
            tile,
            uvCoords,
            container,
            colIndex,
            rowIndex
          );

          // Store bridge tiles separately for updates
          if (tile === 'Z') {
            const tileKey = `${colIndex}_${rowIndex}`;
            this.bridgeTiles[tileKey] = sprite;
          }
        }
      });
    });
  }

  private createTile(x: number, y: number, tileSymbol: string, uv: { tileset: string; uMin: number; uMax: number; vMin: number; vMax: number }, container: Phaser.GameObjects.Container, gridX?: number, gridY?: number): Phaser.GameObjects.Sprite {
    // Get texture source
    const texture = this.scene.textures.get(uv.tileset);
    const source = texture.source[0];

    // Calculate pixel coordinates directly from UV
    const frameX = uv.uMin * source.width;
    const frameY = uv.vMin * source.height;
    const frameWidth = (uv.uMax - uv.uMin) * source.width;
    const frameHeight = (uv.vMax - uv.vMin) * source.height;

    // Create frame name
    const frameName = `tile_${tileSymbol}_${x}_${y}`;

    // Add frame to texture (only if it doesn't exist)
    if (!texture.has(frameName)) {
      texture.add(frameName, 0, frameX, frameY, frameWidth, frameHeight);
    }

    // Create sprite with the frame
    const tile = this.scene.add.sprite(x + this.tileSize / 2, y + this.tileSize / 2, uv.tileset, frameName);

    // NOW set display size after frame is set
    tile.setDisplaySize(this.tileSize, this.tileSize);

    container.add(tile);
    return tile;
  }

  private createAgent(offsetX: number, offsetY: number, container: Phaser.GameObjects.Container): void {
    // Create sprites for all agents
    this.agentSprites = [];
    for (let i = 0; i < this.agentCount; i++) {
      const agentPos = this.agentPositions[i];
      const agentX = offsetX + agentPos.x * this.tileSize + this.tileSize / 2;
      const agentY = offsetY + agentPos.y * this.tileSize + this.tileSize / 2;

      const sprite = this.scene.add.sprite(agentX, agentY, 'agent');
      sprite.setDisplaySize(this.tileSize * 0.8, this.tileSize * 0.8);

      // Make inactive agents slightly transparent
      if (i !== this.activeAgent) {
        sprite.setAlpha(0.6);
      }

      // Improve agent sprite quality 
      sprite.texture.setFilter(Phaser.Textures.FilterMode.LINEAR);

      this.agentSprites.push(sprite);
      container.add(sprite);
    }
  }

  private setupAgentPositionPolling(offsetX: number, offsetY: number): void {
    // Close existing SSE connection if any
    if (this.eventSource) {
      console.log('Closing existing SSE connection');
      this.eventSource.close();
      this.eventSource = undefined;
    }

    // Server-Sent Events (SSE) connection for real-time position updates
    this.eventSource = new EventSource('/api/character/events');

    this.eventSource.onopen = () => {
      console.log('SSE connected');
    };

    this.eventSource.onmessage = (event) => {
      console.log('SSE raw message received:', event.data);
      try {
        const data = JSON.parse(event.data);
        console.log('SSE data received:', data);

        if (data.type === 'computer_interaction') {
          // Handle computer interaction event from server
          console.log('Computer interaction event received:', data);
          if (data.level_completed) {
            console.log('Level completed detected, showing computer effect...');
            this.showComputerUseEffect();
            // Small delay before showing victory screen to let effect play
            this.scene.time.delayedCall(1000, () => {
              console.log('Showing victory screen...');
              this.handleVictory();
            });
          }
        } else if (data.agents) {
          // Update all agent positions from server
          this.serverAgentPositions = data.agents;
          this.activeAgent = data.activeAgent || 0;
          this.updateAgentPosition(offsetX, offsetY);
        } else if (data.position) {
          // Backward compatibility - treat as active agent position
          this.serverAgentPositions[this.activeAgent] = data.position;
          this.updateAgentPosition(offsetX, offsetY);
        }

        // Always check bridge state (not just when agents data exists)
        if (data.bridgesActivated !== undefined) {
          console.log('Bridge state from SSE:', data.bridgesActivated);

          // Show effect only when bridges get activated (false -> true)
          if (!this.lastBridgeState && data.bridgesActivated) {
            this.showBridgeActivationEffect();
          }

          this.lastBridgeState = data.bridgesActivated;
          this.updateBridgeVisuals(data.bridgesActivated);
        }

        // Check for level completion only in computer_interaction events
        if (data.type === 'computer_interaction' && data.level_completed && !this.isGameWon) {
          console.log('Level completion detected in computer_interaction SSE event:', data);
          this.showComputerUseEffect();
          this.scene.time.delayedCall(1000, () => {
            console.log('Showing victory screen from SSE...');
            this.handleVictory();
          });
        }
      } catch (error) {
        console.error('Failed to parse SSE data:', error);
      }
    };

    this.eventSource.onerror = (error) => {
      console.error('SSE error:', error);
    };
  }

  private updateAgentPosition(offsetX: number, offsetY: number): void {
    console.log('Updating agent positions:', this.serverAgentPositions);

    for (let i = 0; i < this.serverAgentPositions.length; i++) {
      const newPosition = this.serverAgentPositions[i];
      const oldPosition = this.agentPositions[i];

      // Only update if position changed
      if (newPosition && oldPosition && (newPosition.x !== oldPosition.x || newPosition.y !== oldPosition.y)) {
        this.agentPositions[i] = newPosition;

        if (this.agentSprites[i]) {
          const newX = offsetX + newPosition.x * this.tileSize + this.tileSize / 2;
          const newY = offsetY + newPosition.y * this.tileSize + this.tileSize / 2;

          // Animate movement
          this.scene.tweens.add({
            targets: this.agentSprites[i],
            x: newX,
            y: newY,
            duration: 200,
            ease: 'Power2'
          });
        }
      }
    }

    // Update agent alpha based on active agent
    this.agentSprites.forEach((sprite, index) => {
      sprite.setAlpha(index === this.activeAgent ? 1.0 : 0.6);
    });

    // Update agent indicators
    this.updateAgentIndicators();
  }

  private setupCamera(levelWidth: number, levelHeight: number): void {
    const camera = this.scene.cameras.main;
    camera.setBounds(0, 0, levelWidth, levelHeight);
    camera.setZoom(GAME_CONFIG.zoom);
  }

  private setupControls(): void {

    this.scene.input.keyboard?.on('keydown-W', () => {
      this.makeMovementRequest('up');
    });

    this.scene.input.keyboard?.on('keydown-A', () => {
      this.makeMovementRequest('left');
    });

    this.scene.input.keyboard?.on('keydown-S', () => {
      this.makeMovementRequest('down');
    });

    this.scene.input.keyboard?.on('keydown-D', () => {
      this.makeMovementRequest('right');
    });

    // Action control - E key for actions (use computer)
    this.scene.input.keyboard?.on('keydown-E', () => {
      this.makeActionRequest();
    });

    // Agent switch control - X key (only if multiple agents)
    if (this.agentCount > 1) {
      this.scene.input.keyboard?.on('keydown-X', () => {
        this.switchAgent();
      });
    }


  }

  private async makeMovementRequest(direction: 'up' | 'down' | 'left' | 'right'): Promise<void> {
    if (this.isGameWon) return; // Prevent movement after victory

    try {
      const response = await fetch('/api/character/multi-move', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          direction: direction,
          steps: 1,
          agentIndex: this.activeAgent
        })
      });

      const result = await response.json();

      if (result.success) {
        console.log('Movement successful:', result);
      } else {
        console.log('Movement failed:', result.error);
      }
    } catch (error) {
      console.error('Movement request failed:', error);
    }
  }

  private async makeActionRequest(): Promise<void> {
    if (this.isGameWon) return; // Prevent actions after victory

    // Try button first, then computer
    try {
      // Check if near a button
      let response = await fetch('/api/character/use-button', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      let result = await response.json();

      if (result.success) {
        console.log('Button pressed:', result.data);
        return; // Button worked, don't try computer
      }

      // If button failed, try computer
      response = await fetch('/api/character/use-pc', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      result = await response.json();

      if (result.success) {
        console.log('Computer used:', result.data);
        // Computer interaction will be handled via server events
        // No need to handle victory here as it will come through SSE
      } else {
        console.log('No action available - not near button or computer');
      }
    } catch (error) {
      console.error('Action request failed:', error);
    }
  }

  private async switchAgent(): Promise<void> {
    if (this.agentCount <= 1) return;

    const newAgentIndex = (this.activeAgent + 1) % this.agentCount;

    try {
      const response = await fetch('/api/character/switch-agent', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          agentIndex: newAgentIndex
        })
      });

      const result = await response.json();

      if (result.success) {
        console.log('Agent switched:', result.data);
        // Update UI to show new active agent
        this.updateAgentSwitchButton();
        // Update agent indicators
        this.updateAgentIndicators();
      } else {
        console.error('Failed to switch agent:', result.error);
      }
    } catch (error) {
      console.error('Switch agent request failed:', error);
    }
  }

  private updateAgentSwitchButton(): void {
    if (this.switchAgentButton && this.agentCount > 1) {
      // Update agent indicator text
      const agentText = this.switchAgentButton.list[2] as Phaser.GameObjects.Text;
      agentText.setText(`Agent ${this.activeAgent + 1}`);
    }
  }

  private updateBridgeVisuals(bridgesActivated: boolean): void {
    if (bridgesActivated && Object.keys(this.bridgeTiles).length > 0) {
      // Update all Z bridge tiles to show T (lowered bridge) visual
      Object.entries(this.bridgeTiles).forEach(([tileKey, bridgeSprite]) => {
        // Get T tile UV coordinates for visual update
        const tUV = TILE_UV_MAPPING['T'];
        if (tUV && bridgeSprite && bridgeSprite.active) {
          // Get texture source for T tile
          const texture = this.scene.textures.get(tUV.tileset);
          const source = texture.source[0];

          // Calculate pixel coordinates for T frame
          const frameX = tUV.uMin * source.width;
          const frameY = tUV.vMin * source.height;
          const frameWidth = (tUV.uMax - tUV.uMin) * source.width;
          const frameHeight = (tUV.vMax - tUV.vMin) * source.height;

          // Create frame name for T tile
          const frameName = `tile_T_bridge_${tileKey}`;

          // Add frame to texture if it doesn't exist
          if (!texture.has(frameName)) {
            texture.add(frameName, 0, frameX, frameY, frameWidth, frameHeight);
          }

          // Simply change the texture/frame of existing sprite - no need to recreate!
          bridgeSprite.setTexture(tUV.tileset, frameName);
        }
      });
    }
  }

  private handleVictory(): void {
    this.isGameWon = true;
    this.showVictoryScreen();
  }

  private showVictoryScreen(): void {
    // Create victory overlay
    this.victoryContainer = this.scene.add.container(0, 0);

    // Gradient background overlay (MainMenu style)
    const overlay = this.scene.add.rectangle(
      this.scene.cameras.main.centerX,
      this.scene.cameras.main.centerY,
      this.scene.cameras.main.width,
      this.scene.cameras.main.height,
      0x1a202c, // Dark blue-gray like the main menu
      0.95
    );
    overlay.setScrollFactor(0);

    // Main panel (like MainMenu card style)
    const panelWidth = 450;
    const panelHeight = 400;
    const panel = this.scene.add.rectangle(
      this.scene.cameras.main.centerX,
      this.scene.cameras.main.centerY,
      panelWidth,
      panelHeight,
      0x374151, // gray-800 equivalent
      1
    );
    // Rounded corners effect with border
    panel.setStrokeStyle(2, 0x4b5563); // gray-700 border
    panel.setScrollFactor(0);

    // Title
    const titleText = this.scene.add.text(
      this.scene.cameras.main.centerX,
      this.scene.cameras.main.centerY - 140,
      'Level Completed!',
      {
        fontSize: '36px',
        color: '#ffffff',
        fontFamily: 'Arial Black'
      }
    );
    titleText.setOrigin(0.5);
    titleText.setScrollFactor(0);

    // Subtitle
    const subtitleText = this.scene.add.text(
      this.scene.cameras.main.centerX,
      this.scene.cameras.main.centerY - 95,
      'You successfully accessed the computer!',
      {
        fontSize: '14px',
        color: '#9ca3af', // gray-400
        fontFamily: 'Arial'
      }
    );
    subtitleText.setOrigin(0.5);
    subtitleText.setScrollFactor(0);

    // Success message
    const successText = this.scene.add.text(
      this.scene.cameras.main.centerX,
      this.scene.cameras.main.centerY - 40,
      '🎉 Well done! 🎉',
      {
        fontSize: '24px',
        color: '#10b981', // green-500
        fontFamily: 'Arial'
      }
    );
    successText.setOrigin(0.5);
    successText.setScrollFactor(0);

    // Button container for spacing
    const buttonY = this.scene.cameras.main.centerY + 40;
    const buttonSpacing = 70;

    // Back to Menu button (primary action - green gradient like MainMenu)
    const menuButton = this.scene.add.rectangle(
      this.scene.cameras.main.centerX,
      buttonY,
      300,
      50,
      0x10b981, // green-500
      1
    );
    menuButton.setScrollFactor(0);
    menuButton.setInteractive({ useHandCursor: true });

    const menuText = this.scene.add.text(
      this.scene.cameras.main.centerX,
      buttonY,
      'Back to Main Menu',
      {
        fontSize: '18px',
        color: '#ffffff',
        fontFamily: 'Arial Bold'
      }
    );
    menuText.setOrigin(0.5);
    menuText.setScrollFactor(0);

    // Try Again button (secondary action)
    const tryAgainButton = this.scene.add.rectangle(
      this.scene.cameras.main.centerX,
      buttonY + buttonSpacing,
      300,
      50,
      0x3b82f6, // blue-500
      1
    );
    tryAgainButton.setScrollFactor(0);
    tryAgainButton.setInteractive({ useHandCursor: true });

    const tryAgainText = this.scene.add.text(
      this.scene.cameras.main.centerX,
      buttonY + buttonSpacing,
      'Try Again',
      {
        fontSize: '18px',
        color: '#ffffff',
        fontFamily: 'Arial Bold'
      }
    );
    tryAgainText.setOrigin(0.5);
    tryAgainText.setScrollFactor(0);

    // Button hover effects (MainMenu style)
    menuButton.on('pointerover', () => {
      menuButton.setFillStyle(0x059669); // green-600
      this.scene.tweens.add({
        targets: menuButton,
        scaleX: 1.05,
        scaleY: 1.05,
        duration: 200,
        ease: 'Power2'
      });
    });

    menuButton.on('pointerout', () => {
      menuButton.setFillStyle(0x10b981); // green-500
      this.scene.tweens.add({
        targets: menuButton,
        scaleX: 1,
        scaleY: 1,
        duration: 200,
        ease: 'Power2'
      });
    });

    tryAgainButton.on('pointerover', () => {
      tryAgainButton.setFillStyle(0x2563eb); // blue-600
      this.scene.tweens.add({
        targets: tryAgainButton,
        scaleX: 1.05,
        scaleY: 1.05,
        duration: 200,
        ease: 'Power2'
      });
    });

    tryAgainButton.on('pointerout', () => {
      tryAgainButton.setFillStyle(0x3b82f6); // blue-500
      this.scene.tweens.add({
        targets: tryAgainButton,
        scaleX: 1,
        scaleY: 1,
        duration: 200,
        ease: 'Power2'
      });
    });

    // Button functionality
    menuButton.on('pointerdown', () => {
      this.goBackToMenu();
    });

    tryAgainButton.on('pointerdown', () => {
      this.restartLevel();
    });

    // Add all elements to container
    this.victoryContainer.add([
      overlay, panel, titleText, subtitleText, successText,
      menuButton, menuText, tryAgainButton, tryAgainText
    ]);

    // Victory animation (fade in with scale effect like MainMenu)
    this.victoryContainer.setAlpha(0);
    this.victoryContainer.setScale(0.8);
    this.scene.tweens.add({
      targets: this.victoryContainer,
      alpha: { from: 0, to: 1 },
      scaleX: { from: 0.8, to: 1 },
      scaleY: { from: 0.8, to: 1 },
      duration: 600,
      ease: 'Back.Out'
    });
  }

  private async restartLevel(): Promise<void> {
    // Hide victory screen
    if (this.victoryContainer) {
      this.victoryContainer.destroy();
      this.victoryContainer = undefined;
    }

    // Reset game state
    this.isGameWon = false;

    // Reset position via API
    try {
      const response = await fetch('/api/character/reset', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      });

      const result = await response.json();

      if (result.success) {
        console.log('Game reset successfully:', result.data);
      } else {
        console.error('Reset failed:', result.error);
        // Fallback: reload the page
        window.location.reload();
      }
    } catch (error) {
      console.error('Failed to reset position:', error);
      // Fallback: just reload the page
      window.location.reload();
    }
  }

  private async setLevelOnServer(levelData: LevelData): Promise<void> {
    try {
      const response = await fetch('/api/level/set', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          levelData: levelData
        })
      });

      const result = await response.json();

      if (result.success) {
        console.log('Level set on server:', result.data);
      } else {
        console.error('Failed to set level on server:', result.error);
      }
    } catch (error) {
      console.error('Error setting level on server:', error);
    }
  }

  private goBackToMenu(): void {
    // Call the callback if provided
    if (this.onBackToMenu) {
      this.onBackToMenu();
    } else {
      console.warn('No back to menu callback provided, reloading page as fallback');
      window.location.reload();
    }
  }

  // 🎮 GAMIFIED EFFECTS SYSTEM 🎮

  private showFloatingText(x: number, y: number, text: string, color: string = '#00ff00'): void {
    const floatingText = this.scene.add.text(x, y, text, {
      fontSize: '20px',
      color: color,
      fontStyle: 'bold',
      stroke: '#000000',
      strokeThickness: 3,
      shadow: { offsetX: 2, offsetY: 2, color: '#000000', blur: 5, fill: true }
    });

    floatingText.setOrigin(0.5);
    floatingText.setDepth(1000); // Always on top

    // Floating animation
    this.scene.tweens.add({
      targets: floatingText,
      y: y - 80,
      alpha: 0,
      scale: 1.5,
      duration: 2000,
      ease: 'Power2',
      onComplete: () => {
        floatingText.destroy();
      }
    });
  }

  private createAgentIndicators(): void {
    // Only for multi-agent levels
    if (this.agentCount <= 1) return;

    this.agentIndicators = [];

    for (let i = 0; i < this.agentCount; i++) {
      const container = this.scene.add.container(0, 0);

      // Green glowing dot
      const dot = this.scene.add.circle(0, 0, 8, 0x00ff00);
      dot.setStrokeStyle(2, 0x00aa00);

      // Pulsing glow effect
      const glow = this.scene.add.circle(0, 0, 12, 0x00ff00, 0.3);

      container.add([glow, dot]);
      container.setDepth(999);

      // Pulsing animation
      this.scene.tweens.add({
        targets: glow,
        scaleX: 1.5,
        scaleY: 1.5,
        alpha: 0.1,
        duration: 1000,
        yoyo: true,
        repeat: -1,
        ease: 'Sine.easeInOut'
      });

      this.agentIndicators.push(container);
    }

    this.updateAgentIndicators();
  }

  private updateAgentIndicators(): void {
    if (this.agentCount <= 1 || this.agentIndicators.length === 0) return;

    this.agentIndicators.forEach((indicator, index) => {
      const agentPosition = this.agentPositions[index];
      if (agentPosition) {
        // Use agent data position, not sprite position (which might be mid-animation)
        const worldX = this.offsetX + agentPosition.x * this.tileSize + this.tileSize / 2;
        const worldY = this.offsetY + agentPosition.y * this.tileSize + this.tileSize / 2;

        // Position above agent
        indicator.setPosition(worldX, worldY - 35);

        // Show only for active agent
        indicator.setVisible(index === this.activeAgent);
      }
    });
  }

  private showBridgeActivationEffect(): void {
    // Show floating text at player position using actual position data
    const agentPosition = this.agentPositions[this.activeAgent];
    if (agentPosition) {
      const worldX = this.offsetX + agentPosition.x * this.tileSize + this.tileSize / 2;
      const worldY = this.offsetY + agentPosition.y * this.tileSize + this.tileSize / 2;

      this.showFloatingText(
        worldX,
        worldY - 30,
        '🌉 BRIDGES ACTIVATED!',
        '#00ffff'
      );
    }

    // Show effects on all bridges
    Object.values(this.bridgeTiles).forEach((bridgeSprite, index) => {
      // Particle burst effect
      const particles = this.scene.add.particles(bridgeSprite.x, bridgeSprite.y, 'tileset1', {
        scale: { start: 0.3, end: 0 },
        speed: { min: 50, max: 150 },
        lifespan: 800,
        quantity: 8,
        tint: [0x00ffff, 0x0088ff, 0x00aaff]
      });

      // Clean up particles after animation
      this.scene.time.delayedCall(1000, () => {
        particles.destroy();
      });

      // Bridge flash effect
      this.scene.tweens.add({
        targets: bridgeSprite,
        tint: 0x00ffff,
        duration: 200,
        yoyo: true,
        repeat: 2,
        onComplete: () => {
          bridgeSprite.setTint(0xffffff); // Reset to normal
        }
      });
    });

    // Screen flash effect
    const flashOverlay = this.scene.add.rectangle(
      this.scene.cameras.main.centerX,
      this.scene.cameras.main.centerY,
      this.scene.cameras.main.width,
      this.scene.cameras.main.height,
      0x00ffff,
      0.3
    );
    flashOverlay.setScrollFactor(0);
    flashOverlay.setDepth(998);

    this.scene.tweens.add({
      targets: flashOverlay,
      alpha: 0,
      duration: 500,
      onComplete: () => {
        flashOverlay.destroy();
      }
    });
  }

  private showComputerUseEffect(): void {
    console.log('showComputerUseEffect called');
    const agentPosition = this.agentPositions[this.activeAgent];
    console.log('Agent position:', agentPosition, 'Active agent:', this.activeAgent);
    if (agentPosition) {
      const worldX = this.offsetX + agentPosition.x * this.tileSize + this.tileSize / 2;
      const worldY = this.offsetY + agentPosition.y * this.tileSize + this.tileSize / 2;

      // Victory text
      this.showFloatingText(
        worldX,
        worldY - 30,
        '🏆 LEVEL COMPLETE!',
        '#ffdd00'
      );

      // Golden sparkle effect
      const particles = this.scene.add.particles(worldX, worldY, 'tileset1', {
        scale: { start: 0.1, end: 0 },
        speed: { min: 100, max: 200 },
        lifespan: 3500,
        quantity: 15,
        tint: [0xffdd00, 0xffaa00, 0xff8800],
        emitZone: { type: 'edge', source: new Phaser.Geom.Circle(0, 0, 10), quantity: 15 }
      });

      // Clean up particles
      this.scene.time.delayedCall(3500, () => {
        particles.destroy();
      });
    }
  }

  // Cleanup method to close connections and free resources
  public cleanup(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = undefined;
    }

    if (this.victoryContainer) {
      this.victoryContainer.destroy();
      this.victoryContainer = undefined;
    }

    if (this.switchAgentButton) {
      this.switchAgentButton.destroy();
      this.switchAgentButton = undefined;
    }

    // Clean up agent indicators
    this.agentIndicators.forEach(indicator => {
      if (indicator) {
        indicator.destroy();
      }
    });
    this.agentIndicators = [];

    // Clear bridge tile references
    this.bridgeTiles = {};
  }
} 