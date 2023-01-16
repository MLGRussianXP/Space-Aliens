import pygame
from random import uniform, randint
from time import time
import os
import sys

# подгружаем отдельно функции для работы со шрифтом
pygame.font.init()
font1 = pygame.font.Font(None, 80)
font2 = pygame.font.Font(None, 35)
win = font1.render('YOU WIN!', True, (255, 255, 255))
results = 'Вы набрали {0} очков, убив {1} боссов. У вас осталось {2} жизней'
lose = font1.render('YOU LOSE!', True, (180, 0, 0))
pause_text = font1.render('Пауза', True, (255, 255, 255))
lose_boss = font1.render('ХА-ХА! Пропустил босса!', True, (180, 0, 0))
restart = font2.render('R - перезапуск', True, (255, 255, 255))  # сообщение о рестарте
start = font2.render('Нажми цифру чтобы начать', True, (255, 255, 255))  # сообщение о старте
start_diff = font2.render('1 - Легко, 2 - Норм, 3 - Капец', True, (255, 0, 255))  # выбор сложности
font2 = pygame.font.Font(None, 30)

# фоновая музыка
pygame.mixer.init()
pygame.mixer.music.load('data/space.ogg')
pygame.mixer.music.set_volume(0.2) # громкость музыки 40%
fire_sound = pygame.mixer.Sound('data/fire.ogg')
reload_sound = pygame.mixer.Sound('data/reload.ogg')
select_sound = pygame.mixer.Sound('data/select_diff.ogg')
boss_sound = pygame.mixer.Sound('data/boss.ogg')
game_over_sound = pygame.mixer.Sound('data/game_over.ogg')
destroy_sound = pygame.mixer.Sound('data/destroy.ogg')

# нам нужны такие картинки:
img_back = "galaxy.jpg"  # фон игры
img_bullet = "bullet.png"  # пуля
img_hero = "rocket.png"  # герой
img_enemy = "ufo.png"  # враг
img_ast = "asteroid.png"  # астероид
img_boss = "boss.png"  # босс

''' Да-да, всё равно нулю так как после выбора сложности подставим туда значения '''
score = 0  # сбито кораблей
goal = 0  # столько кораблей нужно сбить для победы
lost = 0  # пропущено кораблей
max_lost = 0  # проиграли, если пропустили столько
life = 0  # текущие жизни
max_life = 0 # нужно для рестарта, тут храним максимальное количество жизней
max_enemies = 0  # максимальное количество врагов
boss_counter = 0 # счетчик убитых боссов
reload_time = 0 # время перезарядки
boss_coming_at = 0 # храним через сколько набранных очков придёт босс
boss_coming = 0 # через сколько придет следующий босс
num_fire = 0  # переменная для подсчёта выстрела


# функция загрузки изображения из папки data
def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)

    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()

    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# класс-родитель для других спрайтов
class GameSprite(pygame.sprite.Sprite):
 # конструктор класса
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        # Вызываем конструктор класса (Sprite):
        pygame.sprite.Sprite.__init__(self)
        # каждый спрайт должен хранить свойство image - изображение
        self.image = pygame.transform.scale(load_image(player_image), (size_x, size_y))
        self.image_name = player_image
        self.speed = player_speed
        # каждый спрайт должен хранить свойство rect - прямоугольник, в который он вписан
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
    # метод, отрисовывающий героя на окне
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

# класс главного игрока
class Player(GameSprite):
    # метод для управления спрайтом стрелками клавиатуры
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed
    # метод "выстрел" (используем место игрока, чтобы создать там пулю)
    def fire(self):
        bullets.add(Bullet(img_bullet, self.rect.centerx, self.rect.top, 15, 20, -15))

# класс спрайта-врага
class Enemy(GameSprite):
    # движение врага
    def update(self):
        self.rect.y += self.speed
        global lost
        # исчезает, если дойдет до края экрана
        if self.rect.y > win_height:
            self.rect.x = randint(80, win_width - 80)
            self.rect.y = 0
            if self.image_name == img_ast:
                return
            lost += 1

class Boss(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, lives_count):
        GameSprite.__init__(self, player_image, player_x, player_y, size_x, size_y, 1)
        self.lives = lives_count # у босса новое поле для количества жизней
    def update(self):
        global finish
        self.rect.y += self.speed
        if self.rect.y > win_height:
            pygame.mixer.music.stop() # останавливаем музыку
            finish = True
            make_frame() # отрисовываем фон и счетчики размещая их по центру
            window.blit(lose_boss, (win_width / 2 - lose_boss.get_width() / 2, 200))
            window.blit(restart, (win_width / 2 - restart.get_width() / 2, 300))

# класс спрайта-пули
class Bullet(GameSprite):
    # движение врага
    def update(self):
        self.rect.y += self.speed
        # исчезает, если дойдет до края экрана
        if self.rect.y < 0:
            self.kill()

def make_ememies():
    """ Функция uniform из модуля рандом даёт нам возможность получать рандомное число,
    но не целое, а с плавающей запятой(float). Таким образом, скорость в меньшем диапазоне
    будет наиболее разнообразней чем с целыми числами.
    """
    for _ in range(max_enemies):
        monsters.add(
            Enemy(img_enemy, randint(80, win_width - 80), -40, 80, 50, uniform(1.5, 3.0)))
    for _ in range(3):
        asteroids.add(
            Enemy(img_ast, randint(30, win_width - 30), -40, 80, 50, uniform(1.0, 2.0)))

''' 
    Зачем выносить в отдельную функцию отрисовку фона и счетчиков?
    - Потому что эта часть будет повторяться три раза в ходе программы.
    1. В ходе игры. 2. При проигрыше. 3. При выигрыше.  

    Зачем делать это при выигрыше и проигрыше?
    - Для того чтобы счетчики корректно отображались и не врали.  
'''
def make_frame():
    window.blit(background, (0, 0))
    window.blit(font2.render("Счет: " + str(score) + "/" + str(goal), True, (255, 255, 255)),
                (10, 20))
    window.blit(
        font2.render("Пропущено: " + str(lost) + "/" + str(max_lost), True, (255, 255, 255)),
        (10, 50))
    window.blit(font2.render("Боссов: " + str(boss_counter), True, (255, 255, 255)), (10, 80))


if __name__ == '__main__':
    # Создаем окошко
    # window = display.set_mode((0, 0), FULLSCREEN) # можно установить полноэкранный режим
    window = pygame.display.set_mode((800, 500))  # и тогда эту строку нужно закомментировать
    pygame.display.set_caption("Супермега шутер!")
    win_width = pygame.display.Info().current_w  # получаем ширину окна
    win_height = pygame.display.Info().current_h  # получаем высоту окна
    background = pygame.transform.scale(load_image(img_back), (win_width, win_height))
    ''' Можно так же адаптировать размеры спрайтов,
    чтобы была зависимость размера спрайта от размера экрана '''
    # создаем спрайты
    ship = Player(img_hero, 5, win_height - 60, 80, 55, 10)
    boss = Boss(img_boss, randint(80, win_width - 80), -40, 80, 100, 10)

    monsters = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    bullets = pygame.sprite.Group()

    finish = False # переменная "игра закончилась": как только там True,
    # в основном цикле перестают работать спрайты
    run = True  # флаг сбрасывается кнопкой закрытия окна
    rel_time = False  # флаг отвечающий за перезарядку
    first_start = True # переменная чтобы игра не начиналась после запуска
    pause = False # переменная которая отвечает за паузу
    boss_time = False # переменная которая определяет, появится босс или нет

    ''' 
        Чтобы отобразить надпись ровно по центру нужно знать ширину и высоту окна,
        а так же ширину и высоту спрайта, в данном случае текстового. Формула ниже
    '''
    window.blit(
        start, (win_width / 2 - start.get_width() / 2 , win_height / 2 - start.get_height() / 2)
    )
    window.blit(
        start_diff, (
            win_width / 2 - start_diff.get_width() / 2 ,
            win_height / 2 - start_diff.get_height() / 2 + 40
        )
    )
    pygame.display.update()

    # Основной цикл игры:
    while run:
        for e in pygame.event.get():
            # событие нажатия на кнопку Закрыть
            if e.type == pygame.QUIT:
                run = False

            elif e.type == pygame.KEYDOWN:
                # событие нажатия на escape - пауза (вкл/выкл)
                if e.key == pygame.K_ESCAPE:
                    if pause and not first_start:
                        pause = False
                        pygame.mixer.music.play()
                    elif not pause and not first_start:
                        pause = True
                        pygame.mixer.music.pause()
                        window.blit(
                            pause_text,
                            (
                                win_width / 2 - pause_text.get_width() / 2 ,
                                win_height / 2 - pause_text.get_height() / 2
                            )
                        )
                        pygame.display.update()

                # выход из игры по нажатию Q
                elif e.key == pygame.K_q:
                    run = False

                # событие нажатия на пробел - спрайт стреляет
                elif e.key == pygame.K_SPACE and not finish and not pause:
                    # проверяем сколько выстрелов сделано и не происходит ли перезарядка
                    if num_fire < 5 and rel_time == False:
                        num_fire = num_fire + 1
                        fire_sound.play()
                        ship.fire()
                    if num_fire >= 5 and rel_time == False:  # если игрок сделал 5 выстрелов
                        reload_sound.play()
                        last_time = time()  # засекаем время, когда это произошло
                        rel_time = True  # ставив флаг перезарядки

                # легкий уровень сложности
                elif e.key == pygame.K_1 and first_start:
                    goal = 50
                    reload_time = 1
                    max_lost = 10
                    life = max_life = 5
                    max_enemies = 5
                    boss_coming_at = boss_coming = 20 # обе переменные будут со значением 20
                    select_sound.play()
                    pygame.mixer.music.play() # воспроизводим музыку только при начале игры
                    first_start = False
                    make_ememies()

                # средний уровень сложности
                elif e.key == pygame.K_2 and first_start:
                    goal = 125
                    reload_time = 2
                    max_lost = 7
                    life = max_life = 4
                    max_enemies = 7
                    boss_coming_at = boss_coming = 15 # обе переменные будут со значением 15
                    select_sound.play()
                    pygame.mixer.music.play() # воспроизводим музыку только при начале игры
                    first_start = False
                    make_ememies()

                # сложный уровень сложности
                elif e.key == pygame.K_3 and first_start:
                    goal = 300
                    reload_time = 3
                    max_lost = 5
                    life = max_life = 3
                    max_enemies = 10
                    boss_coming_at = boss_coming = 10 # обе переменные будут со значением 10
                    select_sound.play()
                    pygame.mixer.music.play() # воспроизводим музыку только при начале игры
                    first_start = False
                    make_ememies()

                # рестарт - клавиша R, сработает только если игра закончена
                elif e.key == pygame.K_r and finish:
                    # обнуляемся
                    for monster in monsters:
                        monster.kill() # убираем всех врагов
                    for asteroid in asteroids:
                        asteroid.kill() # убиваем все астероиды
                    for bullet in bullets:
                        ''' удаляем все пули которые на сцене, если этого
                            не сделать они продолжат лететь после рестарта '''
                        bullet.kill()
                    if boss_time:
                        boss.kill()
                        boss_time = False
                    finish = False
                    first_start = True
                    rel_time = False  # флаг отвечающий за перезарядку
                    pause = False # переменная которая отвечает за паузу
                    # обнуляем счетчики
                    score = 0
                    num_fire = 0
                    lost = 0
                    # отрисовываем стартовый экран
                    window.fill("black")
                    window.blit(
                        start, (
                            win_width / 2 - start.get_width() / 2 ,
                            win_height / 2 - start.get_height() / 2
                        )
                    )
                    window.blit(
                        start_diff, (
                            win_width / 2 - start_diff.get_width() / 2 ,
                            win_height / 2 - start_diff.get_height() / 2 + 40
                        )
                    )
                    pygame.mixer.music.play() # воспроизводим музыку только при начале игры
                    pygame.display.update()

        if not first_start:
            if not pause:
                # сама игра: действия спрайтов, проверка правил игры, перерисовка
                if not finish:
                    # отрисовываем фон и счетчики
                    make_frame()

                    # производим движения спрайтов
                    ship.update()
                    monsters.update()
                    asteroids.update()
                    bullets.update()

                    # обновляем их в новом местоположении при каждой итерации цикла
                    ship.reset()
                    monsters.draw(window)
                    asteroids.draw(window)
                    bullets.draw(window)

                    # проверяем, если сейчас босс должен быть на сцене
                    if boss_time:
                        # собираем касания с пулями
                        cols = pygame.sprite.spritecollide(boss, bullets, True)
                        for col in cols:
                            boss.lives -= 1 # отнимаем боссу жизни
                        window.blit(
                            font2.render("BOSS: " + str(boss.lives), True, (255, 0, 0)), (10, 140)
                        ) # обновляем счетчик
                        boss.update()
                        boss.reset()
                        if boss.lives <= 0: # если у босса кончились жизни
                            boss_time = False
                            score += 5
                            boss_coming = score + boss_coming_at # следующий босс появится через
                            # "текущие очки" + "через сколько должен появится босс"
                            boss_counter += 1 # счетчик поверженных боссов +1
                            boss.kill() # совсем убиваем его со сцены

                    # если не время босса и "когда должен прийти босс" - "текущие очки"
                    # меньше или равно нулю, то пришло время выпускать босса
                    if not boss_time and boss_coming - score <= 0:
                        boss_time = True
                        # параметра скорости нет, скорость у боссов - 1
                        boss = Boss(img_boss, randint(80, win_width - 80), -40, 80, 100, 5)
                        boss_sound.play() # звук появления босса

                    # проверка столкновения пули и монстров (и монстр, и пуля при касании исчезают)
                    collides = pygame.sprite.groupcollide(monsters, bullets, True, True)
                    for c in collides:
                        # этот цикл повторится столько раз, сколько монстров подбито
                        score += 1
                        destroy_sound.play()
                        monsters.add(
                            Enemy(
                                img_enemy,
                                randint(80, win_width - 80), -40, 80, 50, uniform(1.5, 3.0)
                            )
                        )
                    # если спрайт коснулся врага уменьшает жизнь
                    if pygame.sprite.spritecollide(ship, monsters, False):
                        pygame.sprite.spritecollide(ship, monsters, True)
                        monsters.add(
                            Enemy(
                                img_enemy,
                                randint(80, win_width - 80), -40, 80, 50, uniform(1.5, 3.0)
                            )
                        )
                        life -= 1

                    if pygame.sprite.spritecollide(ship, asteroids, False):
                        pygame.sprite.spritecollide(ship, asteroids, True)
                        asteroids.add(
                            Enemy(
                                img_ast,
                                randint(30, win_width - 30), -40, 80, 50, uniform(1.0, 2.0)
                            )
                        )
                        life -= 1

                    # проигрыш
                    if life == 0 or lost >= max_lost or ship.rect.colliderect(boss):
                        #                               касание босса - это тоже проигрыш
                        # проиграли, ставим фон и больше не управляем спрайтами
                        pygame.mixer.music.stop() # останавливаем музыку
                        finish = True
                        make_frame() # отрисовываем фон и счетчики размещая их по центру
                        window.fill('black')
                        window.blit(lose, (win_width / 2 - lose.get_width() / 2, 200))
                        window.blit(restart, (win_width / 2 - restart.get_width() / 2, 300))
                        results_rendered = font2.render(
                            results.format(score, boss_counter, life), True, (255, 204, 0)
                        )
                        window.blit(
                            results_rendered,
                            (win_width / 2 - results_rendered.get_width() / 2, 350)
                        )
                        game_over_sound.play()

                    # проверка выигрыша: сколько очков набрали?
                    if score >= goal:
                        pygame.mixer.music.stop() # останавливаем музыку
                        finish = True
                        make_frame() # отрисовываем фон и счетчики
                        window.fill('black')
                        window.blit(win, (win_width / 2 - win.get_width() / 2, 200))
                        window.blit(restart, (win_width / 2 - restart.get_width() / 2, 300))
                        results_rendered = font2.render(
                            results.format(score, boss_counter, life), True, (255, 204, 0)
                        )
                        window.blit(
                            results_rendered,
                            (win_width / 2 - results_rendered.get_width() / 2, 350)
                        )

                    # перезарядка
                    if not finish:
                        if rel_time:
                            now_time = time()  # считываем время
                            if now_time - last_time < reload_time:
                                # пока не прошло reload_time выводим информацию о перезарядке
                                window.blit(
                                    font2.render("Патроны: заряжаем", True, (255, 0, 0)), (10, 110)
                                )
                            else:
                                num_fire = 0   # обнуляем счетчик пуль
                                rel_time = False  # сбрасываем флаг перезарядки
                        else:
                            window.blit(
                                font2.render("Патроны: " + str(5 - num_fire), True, (255, 255, 255)),
                                (10, 110)
                            )

                    # задаем разный цвет в зависимости от кол-ва жизней
                    if 3 <= life <= 5:
                        life_color = (0, 150, 0)
                    elif life == 2:
                        life_color = (150, 150, 0)
                    else:
                        life_color = (150, 0, 0)

                    text_life = font1.render(str(life), True, life_color)
                    window.blit(text_life, (750, 10))

                    pygame.display.update()
                pygame.time.delay(50)
