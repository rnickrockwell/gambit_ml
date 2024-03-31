import pygame
import random
import math
import time
import random
import math
import time

def pygame_loop(queue):
    # Initialize Pygame
    pygame.init()

    # Screen dimensions
    # Screen dimensions are now set by the display mode
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    screen_width, screen_height = screen.get_size()  # Update dimensions based on actual size


    # Colours
    black = (0, 0, 0)
    white = (255, 255, 255)

    # Paddle settings
    paddle_width, paddle_height = 10, screen_height/3
    player_speed = 0
    opponent_speed = 7


    # Paddle positions
    opponent_x,opponent_y = 500, screen_height / 2 - paddle_height / 2
    player_x,player_y = screen_width - 20, screen_height / 2 - paddle_height / 2
    player_paddle = pygame.Rect(player_x, player_y, paddle_width, paddle_height)
    opponent_paddle = pygame.Rect(opponent_x, opponent_y, paddle_width, paddle_height)

    # Ball settings
    ball_width, ball_height = 15, 15
    n = 1
    ball_speed_x, ball_speed_y = n * random.choice((1, -1)), n * random.choice((1, -1))
    ball_rect = pygame.Rect((player_x + opponent_x)/ 2, screen_height / 2 - ball_height / 2, ball_width, ball_height)

    # Circle settings
    circle_radius = 140  # Adjust size as needed
    circle_x = circle_radius + 10
    circle_pos_1 = (circle_x, screen_height - 150)
    circle_pos_2 = (circle_x, screen_height /2)
    circle_pos_3 = (circle_x, 0+150)
    #box_padding = 10  # Space around circles for the box

    # Flash frequencies
    flash_frequency_1 = 9.0
    flash_frequency_2 = 12.0
    flash_frequency_3 = 15.0

    # flash_frequency_1 = 7.0
    # flash_frequency_2 = 9.0
    # flash_frequency_3 = 11.0

    # Font settings
    font = pygame.font.SysFont(None, 24)

    # Clock for controlling frame rate
    clock = pygame.time.Clock()

    # Record the start time of the game
    start_time = time.time()


    # Game loop
    running = True
    while running:
        # Calculate elapsed time
        current_time = time.time() - start_time
        
        # Handle Pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_DOWN:
                    player_speed = 7
                elif event.key == pygame.K_UP:
                    player_speed = -7
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_DOWN, pygame.K_UP):
                    player_speed = 0

        if not queue.empty():
            prediction = queue.get()
            if prediction == 'DONE':
                running = False
                break
            else:
                p = int(prediction)
                match p:
                    case 9: opponent_y = screen_height - paddle_height /2
                    case 12: opponent_y = screen_height /2 - paddle_height /2    
                    case 15: opponent_y = 0    
        

        # Game logic
        player_paddle.y += player_speed
        opponent_paddle.y = opponent_y
        if player_paddle.top <= 0: player_paddle.top = 0
        if player_paddle.bottom >= screen_height: player_paddle.bottom = screen_height
        if opponent_paddle.top <= 0: opponent_paddle.top = 0
        if opponent_paddle.bottom >= screen_height: opponent_paddle.bottom = screen_height
        
        ball_rect.x += ball_speed_x
        ball_rect.y += ball_speed_y
        if ball_rect.top <= 0 or ball_rect.bottom >= screen_height: ball_speed_y *= -1
        if ball_rect.left <= opponent_x - paddle_width or ball_rect.right >= screen_width:
            ball_rect.center = (screen_width / 2, screen_height / 2)
            ball_speed_x *= random.choice((1, -1))
            ball_speed_y *= random.choice((1, -1))
        if ball_rect.colliderect(player_paddle) or ball_rect.colliderect(opponent_paddle): ball_speed_x *= -1

        # Draw screen
        screen.fill(black)

        # Paddles
        pygame.draw.rect(screen, white, player_paddle)
        pygame.draw.rect(screen, white, opponent_paddle)

        # Ball
        pygame.draw.ellipse(screen, white, ball_rect)

        # Lines
        pygame.draw.aaline(screen, white, ((opponent_x + player_x) / 2 - 10, 0), ((opponent_x + player_x) / 2 - 10, screen_height))
        pygame.draw.aaline(screen, white, ((circle_x + opponent_x) / 2, 0), ((circle_x + opponent_x) / 2, screen_height))
    

        # Flickering effect for circles
        if math.sin(2 * math.pi * flash_frequency_1 * current_time) > 0:
            pygame.draw.circle(screen, white, circle_pos_1, circle_radius)
        if math.sin(2 * math.pi * flash_frequency_2 * current_time) > 0:
            pygame.draw.circle(screen, white, circle_pos_2, circle_radius)
        if math.sin(2 * math.pi * flash_frequency_3 * current_time) > 0:
            pygame.draw.circle(screen, white, circle_pos_3, circle_radius)



        
        # # Boxing in the flickering circles
        # pygame.draw.rect(screen, white, pygame.Rect(circle_pos_1[0] - circle_radius - box_padding, 
        #                                             circle_pos_1[1] - circle_radius - box_padding, 
        #                                             2 * (circle_radius + box_padding), 
        #                                             2 * (circle_radius + box_padding)), 2)
        # pygame.draw.rect(screen, white, pygame.Rect(circle_pos_2[0] - circle_radius - box_padding, 
        #                                             circle_pos_2[1] - circle_radius - box_padding, 
        #                                             2 * (circle_radius + box_padding), 
        #                                             2 * (circle_radius + box_padding)), 2)
        # pygame.draw.rect(screen, white, pygame.Rect(circle_pos_3[0] - circle_radius - box_padding, 
        #                                             circle_pos_3[1] - circle_radius - box_padding, 
        #                                             2 * (circle_radius + box_padding), 
        #                                             2 * (circle_radius + box_padding)), 2)

        # Display frequencies
        # freq_text_1 = font.render(f'{flash_frequency_1} Hz', True, white)
        # freq_text_2 = font.render(f'{flash_frequency_2} Hz', True, white)
        # freq_text_3 = font.render(f'{flash_frequency_3} Hz', True, white)
        # screen.blit(freq_text_1, (circle_pos_1[0] - freq_text_1.get_width() / 2, circle_pos_1[1] + circle_radius + 10))
        # screen.blit(freq_text_2, (circle_pos_2[0] - freq_text_2.get_width() / 2, circle_pos_2[1] + circle_radius + 10))
        # screen.blit(freq_text_3, (circle_pos_3[0] - freq_text_3.get_width() / 2, circle_pos_3[1] + circle_radius + 10))

        pygame.display.flip()
        clock.tick(144)

    pygame.quit()
