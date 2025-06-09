#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

import pygame

from code.Const import WIN_WIDTH, WIN_HEIGHT, MENU_OPTION
from code.Level import Level
from code.Menu import Menu
from code.Score import Score


class Game:
    def __init__(self):
        pygame.init()
        self.window = pygame.display.set_mode(size=(WIN_WIDTH, WIN_HEIGHT))

    def run(self):
        while True:
            score = Score(self.window)
            menu = Menu(self.window)
            menu_return = menu.run()

            if menu_return in [MENU_OPTION[0], MENU_OPTION[1], MENU_OPTION[2]]:
                # Reinicia a pontuação no início de um novo jogo
                player_score = [0, 0]

                # Loop para tentar o Nível 1
                while True:
                    level1 = Level(self.window, 'Level1', menu_return, player_score)
                    level_return_1 = level1.run(player_score)

                    if level_return_1 is True: # Nível 1 concluído com sucesso
                        # Tentar Nível 2
                        level2 = Level(self.window, 'Level2', menu_return, player_score)
                        level_return_2 = level2.run(player_score)

                        if level_return_2 is True: # Nível 2 concluído com sucesso
                            score.save(menu_return, player_score)
                            break # Sai do loop de tentativas de nível (passou ambos os níveis)
                        elif level_return_2 is False: # Game Over no Nível 2
                            # Permanece no loop para dar a opção de reiniciar (apertar 'R') ou voltar ao menu ('ESC')
                            # Se o usuário apertar 'R', level2.__init__ será chamado dentro de level2.run()
                            # Se o usuário apertar 'ESC', level_return_2 será 'None', e o próximo 'elif' lidará com isso
                            pass
                        elif level_return_2 is None: # Voltar ao menu do Nível 2
                            break # Sai do loop de tentativas de nível, volta para o menu principal
                    elif level_return_1 is False: # Game Over no Nível 1
                        # Permanece no loop para dar a opção de reiniciar (apertar 'R') ou voltar ao menu ('ESC')
                        pass
                    elif level_return_1 is None: # Voltar ao menu do Nível 1
                        break # Sai do loop de tentativas de nível, volta para o menu principal

            elif menu_return == MENU_OPTION[3]:
                score.show()
            elif menu_return == MENU_OPTION[4]:
                pygame.quit()  # Close Window
                quit()  # end pygame
            else:
                pygame.quit()
                sys.exit()