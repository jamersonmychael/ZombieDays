#!/usr/bin/python
# -*- coding: utf-8 -*-
import random
import sys

import pygame
from pygame import Surface, Rect
from pygame.font import Font

from code.Const import C_WHITE, WIN_HEIGHT, MENU_OPTION, EVENT_ENEMY, SPAWN_TIME, C_GREEN, C_CYAN, EVENT_TIMEOUT, \
    TIMEOUT_STEP, TIMEOUT_LEVEL, WIN_WIDTH, C_RED
from code.Enemy import Enemy
from code.Entity import Entity
from code.EntityFactory import EntityFactory
from code.EntityMediator import EntityMediator
from code.Player import Player


class Level:
    def __init__(self, window: Surface, name: str, game_mode: str, player_score: list[int]):
        self.timeout = TIMEOUT_LEVEL
        self.window = window
        self.name = name
        self.game_mode = game_mode
        self.entity_list: list[Entity] = []
        self.entity_list.extend(EntityFactory.get_entity(self.name + 'Bg'))
        player = EntityFactory.get_entity('Player1')
        player.score = player_score[0]
        self.entity_list.append(player)
        if game_mode in [MENU_OPTION[1], MENU_OPTION[2]]:
            player = EntityFactory.get_entity('Player2')
            player.score = player_score[1]
            self.entity_list.append(player)
        pygame.time.set_timer(EVENT_ENEMY, SPAWN_TIME)
        pygame.time.set_timer(EVENT_TIMEOUT, TIMEOUT_STEP)

        self.game_over = False

        # --- Carrega a imagem de Game Over (sem redimensionamento) ---
        try:
            self.game_over_image = pygame.image.load('./asset/GameOverBg.png').convert_alpha()
        except pygame.error as e:
            print(f"Erro ao carregar a imagem de Game Over: {e}")
            self.game_over_image = None

    def run(self, player_score: list[int]):
        pygame.mixer_music.load(f'./asset/{self.name}.mp3')
        pygame.mixer_music.set_volume(0.3)
        pygame.mixer_music.play(-1)
        clock = pygame.time.Clock()

        level_active = True

        while level_active:
            if not self.game_over:
                clock.tick(60)
                for ent in self.entity_list:
                    self.window.blit(source=ent.surf, dest=ent.rect)
                    ent.move()
                    if isinstance(ent, (Player, Enemy)):
                        shoot = ent.shoot()
                        if shoot is not None:
                            self.entity_list.append(shoot)
                    if ent.name == 'Player1':
                        self.level_text(14, f'Player1 - Health: {ent.health} | Score: {ent.score}', C_GREEN, (10, 25))
                    if ent.name == 'Player2':
                        self.level_text(14, f'Player2 - Health: {ent.health} | Score: {ent.score}', C_CYAN, (10, 45))

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == EVENT_ENEMY:
                        choice = random.choice(('Enemy1', 'Enemy2'))
                        self.entity_list.append(EntityFactory.get_entity(choice))
                    if event.type == EVENT_TIMEOUT:
                        self.timeout -= TIMEOUT_STEP
                        if self.timeout == 0:
                            for ent in self.entity_list:
                                if isinstance(ent, Player) and ent.name == 'Player1':
                                    player_score[0] = ent.score
                                if isinstance(ent, Player) and ent.name == 'Player2':
                                    player_score[1] = ent.score
                            pygame.mixer_music.stop()
                            return True

                found_player = False
                for ent in self.entity_list:
                    if isinstance(ent, Player):
                        found_player = True

                if not found_player:
                    self.game_over = True
                    pygame.mixer_music.stop()

                self.level_text(14, f'{self.name} - Timeout: {self.timeout / 1000:.1f}s', C_WHITE, (10, 5))
                self.level_text(14, f'fps: {clock.get_fps():.0f}', C_WHITE, (10, WIN_HEIGHT - 35))
                self.level_text(14, f'entidades: {len(self.entity_list)}', C_WHITE, (10, WIN_HEIGHT - 20))
                pygame.display.flip()

                EntityMediator.verify_collision(entity_list=self.entity_list)
                EntityMediator.verify_health(entity_list=self.entity_list)

            else:
                self.show_game_over_screen(player_score)
                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.__init__(self.window, self.name, self.game_mode, [0, 0])
                            level_active = False
                            return False
                        if event.key == pygame.K_ESCAPE:
                            level_active = False
                            return None

    def level_text(self, text_size: int, text: str, text_color: tuple, text_pos: tuple):
        text_font: Font = pygame.font.SysFont(name="Brunson Rough", size=text_size)
        text_surf: Surface = text_font.render(text, True, text_color).convert_alpha()
        text_rect: Rect = text_surf.get_rect(left=text_pos[0], top=text_pos[1])
        self.window.blit(source=text_surf, dest=text_rect)

    def show_game_over_screen(self, final_scores: list[int]):
        self.window.fill((0, 0, 0))

        # --- Desenha a imagem de Game Over (sem redimensionamento, assumindo tamanho certo) ---
        if self.game_over_image:
            # Centraliza a imagem. Ajuste o Y para posicionamento vertical.
            image_rect = self.game_over_image.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2))
            self.window.blit(source=self.game_over_image, dest=image_rect)
            # Se a imagem não carregou, ainda mostra o texto "GAME OVER"
            game_over_font: Font = pygame.font.SysFont(name="Brunson Rough", size=50)
            game_over_surf: Surface = game_over_font.render("GAME OVER", True, C_RED).convert_alpha()
            game_over_rect: Rect = game_over_surf.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 - 80))
            self.window.blit(source=game_over_surf, dest=game_over_rect)

        # --- Ajuste do posicionamento da Pontuação Final ---
        score_font: Font = pygame.font.SysFont(name="Brunson Rough", size=24)
        # Offset inicial do centro vertical para a pontuação
        y_offset_score = 30

        if self.game_mode == MENU_OPTION[0]: # Single Player
            score_text = f"Sua Pontuação Final: {final_scores[0]}"
            score_surf: Surface = score_font.render(score_text, True, C_WHITE).convert_alpha()
            score_rect: Rect = score_surf.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + y_offset_score))
            self.window.blit(source=score_surf, dest=score_rect)
        elif self.game_mode in [MENU_OPTION[1], MENU_OPTION[2]]: # Co-op ou VS
            score_text_p1 = f"Player 1 Pontuação: {final_scores[0]}"
            score_surf_p1: Surface = score_font.render(score_text_p1, True, C_GREEN).convert_alpha()
            score_rect_p1: Rect = score_surf_p1.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + y_offset_score))
            self.window.blit(source=score_surf_p1, dest=score_rect_p1)

            y_offset_score += 25 # Aumenta o offset para a próxima linha de texto
            score_text_p2 = f"Player 2 Pontuação: {final_scores[1]}"
            score_surf_p2: Surface = score_font.render(score_text_p2, True, C_CYAN).convert_alpha()
            score_rect_p2: Rect = score_surf_p2.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + y_offset_score))
            self.window.blit(source=score_surf_p2, dest=score_rect_p2)

        # --- Ajuste do posicionamento das Opções (Reiniciar / Voltar ao Menu) ---
        instructions_font: Font = pygame.font.SysFont(name="Brunson Rough", size=18)
        # Offset inicial do centro vertical para as instruções
        y_offset_instructions = 80

        restart_text = "Pressione 'R' para Reiniciar Nível"
        restart_surf: Surface = instructions_font.render(restart_text, True, C_WHITE).convert_alpha()
        restart_rect: Rect = restart_surf.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + y_offset_instructions))
        self.window.blit(source=restart_surf, dest=restart_rect)

        y_offset_instructions += 25 # Aumenta o offset para a próxima instrução
        menu_text = "Pressione 'ESC' para Voltar ao Menu"
        menu_surf: Surface = instructions_font.render(menu_text, True, C_WHITE).convert_alpha()
        menu_rect: Rect = menu_surf.get_rect(center=(WIN_WIDTH // 2, WIN_HEIGHT // 2 + y_offset_instructions))
        self.window.blit(source=menu_surf, dest=menu_rect)