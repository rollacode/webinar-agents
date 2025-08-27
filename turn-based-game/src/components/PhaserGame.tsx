'use client';

import { forwardRef, useEffect, useImperativeHandle, useRef } from 'react';
import { GAME_CONFIG } from '@/lib/gameConfig';
import { GameScene } from '@/lib/gameScene';

export interface IRefPhaserGame {
  game: Phaser.Game | undefined;
  scene: Phaser.Scene | undefined;
  restartGame: () => void;
}

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

interface IProps {
  currentActiveScene?: (scene_instance: Phaser.Scene) => void;
  selectedLevel: LevelData;
  onBackToMenu?: () => void;
}

export const PhaserGame = forwardRef<IRefPhaserGame, IProps>(function PhaserGame(
  { currentActiveScene, selectedLevel, onBackToMenu },
  ref
) {
  const game = useRef<Phaser.Game | undefined>(undefined);
  const phaserRef = useRef<HTMLDivElement>(null);

  useImperativeHandle(ref, () => ({
    game: game.current,
    scene: game.current?.scene.getScene('MainScene'),
    restartGame: () => {
      // Call cleanup before restart
      if (game.current) {
        const mainScene = game.current.scene.getScene('MainScene') as any;
        if (mainScene && mainScene.gameScene && typeof mainScene.gameScene.cleanup === 'function') {
          mainScene.gameScene.cleanup();
        }
      }
      
      // Trigger game restart by calling reset API
      fetch('/api/character/reset', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        }
      }).catch(error => {
        console.error('Failed to restart game:', error);
        // Fallback: reload page
        window.location.reload();
      });
    }
  }), []);

  useEffect(() => {
    let isMounted = true;

    async function initPhaser() {
      // Destroy existing game if it exists (for level changes)
      if (game.current) {
        console.log('Destroying existing game for level change');
        
        // Call cleanup on gameScene if it exists
        const mainScene = game.current.scene.getScene('MainScene') as any;
        if (mainScene && mainScene.gameScene && typeof mainScene.gameScene.cleanup === 'function') {
          mainScene.gameScene.cleanup();
        }
        
        game.current.destroy(true);
        game.current = undefined;
        
        // Small delay to ensure cleanup is complete
        await new Promise(resolve => setTimeout(resolve, 100));
      }

      if (!phaserRef.current) {
        console.log('Skipping init - ref not ready');
        return;
      }

      if (!isMounted) {
        console.log('Skipping init - component unmounted');
        return;
      }

      console.log('Initializing Phaser game with level:', selectedLevel.name);

      const Phaser = await import('phaser');

      // Level rendering scene
      class MainScene extends Phaser.Scene {
        public gameScene: GameScene;

        constructor() {
          super({ key: 'MainScene' });
          this.gameScene = new GameScene(this, selectedLevel.data, GAME_CONFIG.tileSize, onBackToMenu);
        }

        preload() {
          console.log('Preloading assets...');
          this.gameScene.preload();
        }

        create() {
          console.log('Creating level scene for:', selectedLevel.name);
          this.gameScene.create();

          console.log('Level scene created successfully');

          // Auto-cleanup when scene is destroyed
          this.events.once('destroy', () => {
            console.log('Scene destroying - calling cleanup');
            this.gameScene.cleanup();
          });

          // Notify React that scene is ready
          if (currentActiveScene) {
            currentActiveScene(this);
          }
        }
      }

      const config: Phaser.Types.Core.GameConfig = {
        type: Phaser.AUTO,
        width: GAME_CONFIG.width,
        height: GAME_CONFIG.height,
        backgroundColor: GAME_CONFIG.backgroundColor,
        parent: phaserRef.current,
        scene: [MainScene],
        scale: {
          mode: Phaser.Scale.FIT,
          autoCenter: Phaser.Scale.CENTER_BOTH
        },
        render: {
          antialias: true,
          antialiasGL: true,
          roundPixels: false, // Keep false for smoother scaling
          pixelArt: false // Set to true if using pixel art
        }
      };

      if (!isMounted) return;

      game.current = new Phaser.Game(config);
    }

    initPhaser();

    return () => {
      isMounted = false;
      if (game.current) {
        // Call cleanup before destroying
        const mainScene = game.current.scene.getScene('MainScene') as any;
        if (mainScene && mainScene.gameScene && typeof mainScene.gameScene.cleanup === 'function') {
          mainScene.gameScene.cleanup();
        }
        
        game.current.destroy(true);
        game.current = undefined;
      }
    };
  }, [currentActiveScene, selectedLevel]);

  return <div ref={phaserRef} style={{ width: '100%', height: '100%' }} />;
}); 