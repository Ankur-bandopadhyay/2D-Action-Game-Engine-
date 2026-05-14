import pygame
import os
import random
import csv
import button
pygame.init()

SCREEN_WIDTH=500#800 kore dibi
SCREEN_HEIGHT=int(SCREEN_WIDTH*0.8)#uses 80 percent of the size

#define game variables
GRAVITY=0.75
SCROLL_THRESH=200#DISTANCE TO THE NEAR END OF THE SCREEN THEN SCREEN WILL MOVE
screen_scroll=0
bg_scroll=0
ROWS=16
TILE_SIZE=SCREEN_HEIGHT // ROWS #EVENLY SPLIT WHOLE SCREEN
COLS=150
TILE_TYPES=21
MAX_LEVELS=3
level = 1#this will increase as player finishes it
start_game=False


#define player action variables
moving_left=False
moving_right=False
shoot=False
grenade=False
grenade_thrown=False

#define colors in bg so that while moving the player it doesnt leave a trail behind
BG=(144,201,120)#rgb codes
RED=(255,0,0)
WHITE=(255,255,255)
GREEN=(0,255,0)
BLACK=(0,0,0)

#define font
font=pygame.font.SysFont('Futura',30)
def draw_text(text,font,text_col,x,y):
    img= font.render(text,True,text_col)
    screen.blit(img,(x,y))


screen=pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))#CREATES A PYGAME WINDOW
pygame.display.set_caption('Shooter')

#load images
#button images
start_img=pygame.image.load('img/start_btn.png').convert_alpha()
exit_img=pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img=pygame.image.load('img/restart_btn.png').convert_alpha()

#backgound
pine1_img=pygame.image.load('img/Background/pine1.png').convert_alpha()
pine2_img=pygame.image.load('img/Background/pine2.png').convert_alpha()
mountain_img=pygame.image.load('img/Background/mountain.png').convert_alpha()
sky_img=pygame.image.load('img/Background/sky_cloud.png').convert_alpha()


#store tiles in a list
img_list=[]#this list will correspond to each image of the tiles
for x in range(TILE_TYPES):
    img=pygame.image.load(f'img/Tile/{x}.png')#21diff tiles
    img=pygame.transform.scale(img,(TILE_SIZE,TILE_SIZE))
    img_list.append(img)


#bullet
bullet_img=pygame.image.load('img/icons/bullet.png').convert_alpha()
#grenade
grenade_img=pygame.image.load('img/icons/grenade.png').convert_alpha()
#pickup boxes
health_box_img=pygame.image.load('img/icons/health_box.png').convert_alpha()
grenade_box_img=pygame.image.load('img/icons/grenade_box.png').convert_alpha()
ammo_box_img=pygame.image.load('img/icons/ammo_box.png').convert_alpha()

BOX_SIZE = (20, 20)

health_box_img = pygame.transform.scale(health_box_img, BOX_SIZE)
grenade_box_img = pygame.transform.scale(grenade_box_img, BOX_SIZE)
ammo_box_img = pygame.transform.scale(ammo_box_img, BOX_SIZE)

item_boxes={
    'Health' : health_box_img ,
    'Ammo': ammo_box_img,
    'Grenade':grenade_box_img
    
}
#set framerate to control the speed
clock = pygame.time.Clock()
FPS=60

def draw_bg():
    screen.fill(BG)
    width=sky_img.get_width()
    for x in range(5):#we will run a loop for keeping on adding bg images so that it never runs out
        screen.blit(sky_img,((x*width) - bg_scroll * 0.5,0))
        screen.blit(mountain_img,((x*width)-bg_scroll *0.6,SCREEN_HEIGHT-mountain_img.get_height()-110))#whatever be the sky width in 1st  iteration will add 0(0xwidth) 2nd iter 1*width so every iteratin the width will get increased
        screen.blit(pine1_img,((x*width)-bg_scroll*0.7,SCREEN_HEIGHT-pine1_img.get_height()+10))#*0.6,0.5 is kacher images will move faster compared to farther images
        screen.blit(pine2_img,((x*width)-bg_scroll*0.8,SCREEN_HEIGHT-pine1_img.get_height()+60))


#function to reset the level
def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()

    #create a new world(empty tile list)
    data=[]
    for row in range(ROWS):
        r=[-1]*COLS#empty tile will be represented by -1
        data.append(r)

    return data    



class Soldier(pygame.sprite.Sprite):
    def __init__(self,char_type,x,y,scale,speed,ammo,grenades):#x and y are the coordinates
        pygame.sprite.Sprite.__init__(self)
        self.alive=True#to know when its ded or alive:)
        self.char_type=char_type
        self.speed=speed#to give it some speed
        self.ammo=ammo#to ensure player doesnt shoot infinietly
        self.start_ammo=ammo
        self.shoot_cooldown=0#to limit how quickly i can fire
        self.grenades=grenades
        self.health=100
        self.max_health=self.health
        self.direction=1#direc and flip cus for when player moves left it should flip
        self.vel_y=0#vertical velocity
        self.jump=False
        self.in_air=True
        self.flip=False
        #to draw the player
        self.animation_list=[]
        self.frame_index=0
        self.action=0#0 refers to idle and if i want to run it changes to 1
        self.update_time=pygame.time.get_ticks()#will give me the time when the animation starts acts as a baseline


        #create ai specific variables
        self.move_counter=0
        self.vision=pygame.Rect(0,0,150,20)#variable for enemies to sense the player 150 refers to how much they can see
        self.idling=False
        self.idling_counter=0


        #load all images for players
        animation_types=['Idle','Run','Jump','Death']

        for animation in animation_types:
            temp_list=[]
            #reset temp list of images
            #count no of files in folder
            num_of_frames=len(os.listdir(f'img/{self.char_type}/{animation}'))#take the length of the folders
            for i in range(num_of_frames):
                img=pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()#loads the image into the x and y
                #to scale the image
                img=pygame.transform.scale(img,(int(img.get_width() * scale),int(img.get_height()*scale)))
                temp_list.append(img)#will appen each of the animation
            self.animation_list.append(temp_list)

    



        self.animation_list.append(temp_list) 
        self.image=self.animation_list[self.action][self.frame_index] #if 0 then will fetch idles's temp list vice versa for 1(run)   
        self.rect=self.image.get_rect()#draws a rectangle type boundary around img
        self.rect.center= (x,y)#draws rect around the coordinates
#attaching self makes it a instance variable
        self.width=self.image.get_width()
        self.height=self.image.get_height()




    def update(self):
        self.update_animation()
        self.check_alive()
        #update cooldown
        if self.shoot_cooldown>0:#if the player has shot already
            self.shoot_cooldown-=1



    def move(self,moving_left,moving_right):#will accept the parameters moving left and right
        #reset movement variables incase of collision
        screen_scroll=0
        dx=0
        dy=0

        #assign movement variables if moving left or right
        if moving_left:
            dx = -self.speed
            self.flip=True
            self.direction=-1
        if moving_right:
            dx=self.speed
            self.flip=False
            self.direction=1

        #jump
        if self.jump==True and self.in_air==False:#will stop double jump air e thakle wont jump again
            self.vel_y= -11#y coordinates start at top of screen if youre jumping its gonna go -ve
            #atthis point it has completed the jump
            self.jump=False
            self.in_air=True

        #apply gravity
        self.vel_y+=GRAVITY#u hv to put a limit to a ground
        if self.vel_y>10:#if it has more speed than 10 while going up it will come down
            self.vel_y
        dy+=self.vel_y#actual change of y coordinate

        #check for collison 
        for tile in world.obstacle_list:#check for collision first to restrict players movement
            #check collison in x direc
            if tile[1].colliderect(self.rect.x+dx,self.rect.y,self.width,self.height):#dx will be the new distance player has travelled
                dx=0
                #if the ai has hit the wall it will change sides
                if self.char_type=='enemy':
                    self.direction*=-1
                    self.move_counter=0
            #check for collision in y direc
            if tile[1].colliderect(self.rect.x,self.rect.y+dy,self.width,self.height):#dy will be the new distance player has travelled
                #below the ground,i.e jumping
                if self.vel_y<0:#hit a head
                    self.vel_y=0#prevents double jump if it jumps velocity is 0
                    dy=tile[1].bottom-self.rect.top#how far is the player is yet to move
                #check if above the ground,falling 
                elif self.vel_y>=0:
                    self.vel_y=0
                    self.in_air=False
                    dy=tile[1].top-self.rect.bottom  


        #check with collision with water
        if pygame.sprite.spritecollide(self,water_group,False):
            self.health=0


        #check for collision with exit
        level_complete=False
        if pygame.sprite.spritecollide(self,exit_group,False):
            level_complete=True
        

        #check if player has fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT:
           self.health=0 

      
      
      
         #check if going off the edges of the screen
        if self.char_type == 'player':
            if self.rect.left+dx<0 or self.rect.right+dx>SCREEN_WIDTH  :
                dx=0#stop his movement        


        #update rectangle position
        self.rect.x += dx
        self.rect.y += dy

        #update scroll basedon player's scroll
        if self.char_type=='player':
            if (self.rect.right > SCREEN_WIDTH-SCROLL_THRESH and bg_scroll<(world.level_length*TILE_SIZE)-SCREEN_WIDTH) \
                or (self.rect.left<SCROLL_THRESH and bg_scroll>abs(dx)):#check if he'snear the screen(player)
                self.rect.x-= dx
                screen_scroll = -dx #if he's moving right screen moves left vice versa

        return screen_scroll,level_complete


    def shoot(self):
        if self.shoot_cooldown == 0 and self.ammo>0:#ihv atleast one bullet to shoot with
            self.shoot_cooldown =20#lower the no faster the reload
            bullet=Bullet(self.rect.centerx + (0.75 *self.rect.size[0]*self.direction),self.rect.centery,self.direction)#the bullets will shoot from the center of the player's coordinates ,player.rect.size[0] starts up the bullet from the center +players width,*player.direction so when it changes its direction bullets coordinate become negative
            bullet_group.add(bullet)
            #reduce ammo     
            self.ammo-=1

    def ai(self):
        if self.alive and player.alive:
            if self.idling==False and random.randint(1,200)==1:#run this check when they r not idle
                self.update_action(0)#0 for idle
                self.idling=True#condition if matched then they will become idle
                self.idling_counter=50
            #check if ai is near player
            if self.vision.colliderect(player.rect):
                #stop running and face player
                self.update_action(0)
                #shoot
                self.shoot()


            else:#if it doesnt detect the player
                if self.idling==False:#non idle state
                    if self.direction==1:
                        ai_moving_right=True
                    else:
                        ai_moving_right=False    

                    ai_moving_left=not ai_moving_right#to not let the ai move in both directions
                    self.move(ai_moving_left,ai_moving_right)
                    self.update_action(1)#1 run
                    self.move_counter+=1
                    #update ai vision as the enemy moves
                    self.vision.center=(self.rect.centerx+ 75*self.direction,self.rect.centery)#it will see half the vision(150) starting from itself and (-ve)/(+ve) will the distance be so that it points ahead them
                    #pygame.draw.rect(screen,RED,self.vision) to draw the vision


                    if self.move_counter > TILE_SIZE:
                        self.direction *=-1#to randomly change the direction
                        self.move_counter*=-1
                else:
                    self.idling_counter-=1#if it has stopped timer will start
                    if self.idling_counter<=0:
                        self.idling=False

        #scroll
        self.rect.x+=screen_scroll#will move the rect of the enemies



    def update_animation(self):
        #update animation
        ANIMATION_COOLDOWN = 100#acts as a cooldown timer(very fast it keeps on updating)
        #update image depending on current frame
        self.image=self.animation_list[self.action][self.frame_index]
        #check if enough time has passed since the last update
        if pygame.time.get_ticks()-self.update_time > ANIMATION_COOLDOWN:
            self.update_time=pygame.time.get_ticks()#resets the timer
            self.frame_index+=1
        #if the animation has ran out reset to the start
        if self.frame_index >=len(self.animation_list[self.action]):#check the no of frames within the action list
            #to stop the death animation from keep on happening
            if self.action==3:
                self.frame_index=len(self.animation_list[self.action])-1#returns the last animation
            else:    
                 self.frame_index=0




    def update_action(self,new_action):
        #check if the new action is different than previous one
        if new_action != self.action:
            self.action=new_action#if its running change to idle vice versa
            #update the animation
            self.frame_index=0
            self.update_time=pygame.time.get_ticks()#get a snapshot of frame index and time so that the character can be cooled down

    def check_alive(self):
        if self.health<=0:
            self.health=0
            self.speed=0#the enemy or player dont remain floating but stop where there are
            self.alive=False
            self.update_action(3)

    def draw(self):
        #to draw the image use the blit method
         screen.blit(pygame.transform.flip(self.image,self.flip,False),self.rect)#parameters what image i want and location
class World():
    def __init__(self):
        self.obstacle_list=[]   #check for only the dirtboxes  
    def process_data(self,data):
         self.level_length=len(data[0])#list of list incase of here how may columns do we have for the1strow
        #iterate through the list and based on what number it is take action
         for y,row in enumerate(data):
             for x,tile in enumerate(row):
                 if tile >= 0:#-1s are ignored
                     img=img_list[tile]#tile will correspond to the no
                     img_rect=img.get_rect()#each img will be assigned a rec
                     img_rect.x= x*TILE_SIZE#enumerator comes in play to fetch index no(x)
                     img_rect.y= y*TILE_SIZE
                     tile_data=(img,img_rect)
                     if tile>=0 and tile<=8:#these are obstacles
                        self.obstacle_list.append(tile_data)
                     elif tile>=9 and tile<=10:
                         water=Water(img,x*TILE_SIZE,y*TILE_SIZE)
                         water_group.add(water)
                     elif tile>11 and tile<=14:
                         decoration=Decoration(img,x*TILE_SIZE,y*TILE_SIZE)
                         decoration_group.add(decoration)
                     elif tile ==15:#create a player
                        player = Soldier('player',x*TILE_SIZE,y*TILE_SIZE,0.8,5,20,5)
                        health_bar=HealthBar(10,10,player.health,player.health)
                     elif tile==16:#create enemies
                         enemy = Soldier('enemy',x*TILE_SIZE,y*TILE_SIZE,0.8,2,20,0)
                         enemy_group.add(enemy)
                     elif tile ==17:#create ammo box
                         item_box=Itembox('Ammo',x*TILE_SIZE,y*TILE_SIZE)
                         item_box_group.add(item_box)
                     elif tile ==18:#create grenade box
                         item_box=Itembox('Grenade',x*TILE_SIZE,y*TILE_SIZE)
                         item_box_group.add(item_box)
                     elif tile ==19:#create health box
                         item_box=Itembox('Health',x*TILE_SIZE,y*TILE_SIZE)
                         item_box_group.add(item_box)        
                     elif tile==20:
                         exit=Exit(img,x*TILE_SIZE,y*TILE_SIZE)
                         exit_group.add(exit)

         return  player,health_bar    
                         
    def draw(self):
      for tile in self.obstacle_list:
          tile[1][0]+=screen_scroll
          screen.blit(tile[0],tile[1])#0 for the img and 1 for the rectangle
          


class Decoration(pygame.sprite.Sprite):
    def __init__(self,img,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=img
        self.rect=self.image.get_rect()
        self.rect.midtop=(x+TILE_SIZE // 2,y+(TILE_SIZE-self.image.get_height()))

    def update(self):
        self.rect.x+=screen_scroll

class Water(pygame.sprite.Sprite):
    def __init__(self,img,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=img
        self.rect=self.image.get_rect()
        self.rect.midtop=(x+TILE_SIZE // 2,y+(TILE_SIZE-self.image.get_height()))

    def update(self):
        self.rect.x+=screen_scroll   

class Exit(pygame.sprite.Sprite):
    def __init__(self,img,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image=img
        self.rect=self.image.get_rect()
        self.rect.midtop=(x+TILE_SIZE // 2,y+(TILE_SIZE-self.image.get_height()))
    
    def update(self):
        self.rect.x+=screen_scroll




class Itembox(pygame.sprite.Sprite):
    def __init__(self,item_type,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type=item_type
        self.image = item_boxes[self.item_type]
        self.rect=self.image.get_rect()
        self.rect.midtop=(x + TILE_SIZE // 2,y+(TILE_SIZE-self.image.get_height()))#so that it just sits at the top


    def update(self):
        #scroll
        self.rect.x+=screen_scroll
        #check if player has picked up any boxes
        if pygame.sprite.collide_rect(self,player):#itembox's rect should collide wit player's to get money
            #check what kindofbox
            if self.item_type=='Health':
                player.health+=25
                if player.health>player.max_health:
                    player.health=player.max_health
            elif self.item_type=='Ammo':
                player.ammo+=15
            elif self.item_type=='Grenade':
                player.grenades+=3

            #delete the itemboxes once it picks up
            self.kill()      

class HealthBar():
    def __init__(self,x,y,health,max_health):
        self.x=x
        self.y=y
        self.health=health
        self.max_health=max_health

    def draw(self,health):
        #update with new health
        self.health=health
        #calculate health ratio
        ratio=self.health/self.max_health
        pygame.draw.rect(screen,BLACK,(self.x -2,self.y-2,154,24))
        pygame.draw.rect(screen,RED,(self.x,self.y,150,20)) 
        pygame.draw.rect(screen,GREEN,(self.x,self.y,150*ratio,20))   #ratio is health/max health

    



class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed=10#bullet speed
        self.image=bullet_img
        self.rect=self.image.get_rect()
        self.rect.center=(x,y)#rectangle gets drawn around the bullet img
        self.direction=direction

    def update(self):
        #move bullet
        self.rect.x+=(self.direction*self.speed)+screen_scroll
        #check if bullet has gone out of screen so that it saves memory
        if self.rect.right < 0 or self.rect.left> SCREEN_WIDTH -30:
            self.kill()

        #   check collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
               self.kill()

        #check collision with characters
        if  pygame.sprite.spritecollide(player,bullet_group,False):#if the player is hit wit any of the bullets
            #only if player is alive then it dies
            if player.alive:
                player.health-=5
                self.kill()
        for enemy in enemy_group:        
            if  pygame.sprite.spritecollide(enemy,bullet_group,False):#if the player is hit wit any of the bullets
                #only if enemy is alive then it dies
                if enemy.alive:
                    enemy.health-=30#reduces health of enemy by 25
                    self.kill()#bullet gets deleted  and if enemy is alive bullet just passes through it    


class Grenade(pygame.sprite.Sprite):
    def __init__(self,x,y,direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer=100#fuse timer it will sit there then explode
        self.vel_y = -11#gonna shoot up at 11 pixels up
        self.speed=7#horizontal speed
        self.image=grenade_img
        self.rect=self.image.get_rect()
        self.rect.center=(x,y)#rectangle gets drawn around the grenade img
        self.direction=direction
        self.width=self.image.get_width()
        self.height=self.image.get_height()


    def update(self):#grenade's own projectile(vertical and horizontal speed)
        self.vel_y+=GRAVITY
        dx=self.direction*self.speed
        dy=self.vel_y


        #check for collision with level
        for tile in world.obstacle_list:
            #check collision with walls
            if tile[1].colliderect(self.rect.x+dx,self.rect.y,self.width,self.height):
                self.direction*=-1#uppon reaching/hitting the wall the grenade will flip(bounce sort) if it goes right it chabges to left
                dx=self.direction*self.speed#updating it
            #check for collision in y direc
            if tile[1].colliderect(self.rect.x,self.rect.y+dy,self.width,self.height):#dy will be the new distance player has travelled
                self.speed=0#if it hits ceiling it just falls to the ground
                #check if ground is below i.e thrown up
                if self.vel_y<0:#moving upwards
                    self.vel_y=0
                    dy=tile[1].bottom-self.rect.top
                #check if above the ground,falling 
                elif self.vel_y>=0:
                    self.vel_y=0
                    dy=tile[1].top-self.rect.bottom#how far the ned can move    
        
        
        #update grenade pos
        self.rect.x+=dx + screen_scroll
        self.rect.y +=dy  

        #countdown timer
        self.timer-=1 
        if self.timer<=0:
            self.kill()
            explosion=Explosion(self.rect.x,self.rect.y,0.5)#explosion takes place in place of the grenade
            explosion_group.add(explosion)
            #do damage to anyone that is nearby
            if abs(self.rect.centerx - player.rect.centerx)  < TILE_SIZE*2 and \
               abs(self.rect.centery - player.rect.centery)  < TILE_SIZE*2 :   #blast radius will be 2 tiles across  
                player.health-=50
            for enemy in enemy_group:    
                if abs(self.rect.centerx - enemy.rect.centerx)  < TILE_SIZE*2 and \
                    abs(self.rect.centery - enemy.rect.centery)  < TILE_SIZE*2 :   #blast radius will be 2 tiles across here it will affect the whole group of enemies
                    enemy.health-=50
                    print(enemy.health)

class Explosion(pygame.sprite.Sprite):
    def __init__(self,x,y,scale):
        pygame.sprite.Sprite.__init__(self)
        #for explosions we create a list and add the animations which run after the another
        self.images=[]
        for num in range(1,6):
            img=pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
            img=pygame.transform.scale(img,(int(img.get_width()*scale),int(img.get_height()*scale)))
            self.images.append(img)
        self.frame_index=0                              
        self.image=self.images[self.frame_index]    
        self.rect=self.image.get_rect()
        self.rect.center=(x,y)#rectangle gets drawn around the grenade img
        self.counter=0 


    def update(self):
        #scroll
        self.rect.x+=screen_scroll

        EXPLOSION_SPEED  = 4#how quickly i want to animate
        #update explosion
        self.counter+=1
        if self.counter>= EXPLOSION_SPEED:
            self.counter=0
            self.frame_index+=1#jumps onto the next frame
            #if the animation is complete then del the explosion
            if self.frame_index>=len(self.images):
                self.kill()
            else:    
                self.image=self.images[self.frame_index]
              

#create buttons
start_button= button.Button(SCREEN_WIDTH // 2-130,SCREEN_HEIGHT // 2 - 150,start_img,1)
exit_button= button.Button(SCREEN_WIDTH // 2-110,SCREEN_HEIGHT // 2 + 50,exit_img,1)
restart_button= button.Button(SCREEN_WIDTH // 2-66,SCREEN_HEIGHT // 2 - 50,restart_img,1)


 
#create sprite groups
enemy_group=pygame.sprite.Group()
bullet_group=pygame.sprite.Group()#allow me to group all the bullets not individually
grenade_group=pygame.sprite.Group()
explosion_group=pygame.sprite.Group()
item_box_group=pygame.sprite.Group()
decoration_group=pygame.sprite.Group()
water_group=pygame.sprite.Group()
exit_group=pygame.sprite.Group()








#create empty tile list
world_data=[]
for row in range(ROWS):
    r=[-1]*COLS#empty tile will be represented by -1
    world_data.append(r)
#load in level data and create world
with open(f'level{level}_data.csv',newline='') as csvfile:
    reader=csv.reader(csvfile,delimiter=',')
    for x,row in enumerate(reader):
         for y,tile in enumerate(row):
             world_data[x][y]=int(tile)

world= World()
player,health_bar=world.process_data(world_data)          



#to keep the window open
run=True
while run:

    clock.tick(FPS)

    
    
    if start_game== False: 
        #draw menu
        screen.fill(BG)
        #add buttons
        if start_button.draw(screen):#if player clicks the button since it retuns a action
            start_game=True #flicks between 2 variable start_game and run
        if exit_button.draw(screen):
            run=False

        
    else:
        draw_bg()#adding this will keep on refreshing the background
        #draw world map
        world.draw()
        #show health bar
        health_bar.draw(player.health)
        #show ammo
        draw_text('AMMO:',font,WHITE,10,35)
        for x in range(player.ammo):
            screen.blit(bullet_img,(90+(x*10),40))
        
        #show grenades
        draw_text('GRENADES:',font,WHITE,10,60)
        for x in range(player.grenades):
            screen.blit(grenade_img,(135+(x*15),60))
        
        
        player.update()
        player.draw()
        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        #update and draw groups
        bullet_group.update()
        grenade_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()
        explosion_group.update()#will deal with a set of explosions
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)
        item_box_group.draw(screen)
        

        #update player actions
        #if the player is alive then only will i want it to move
        if player.alive:
            #shoot bullets
            if shoot:#processing the bullets
                 player.shoot()#this ensures that both player and enemy can shoot
            #throw grenades
            elif grenade and grenade_thrown==False and player.grenades>0:#if its having more than 1 grenade it can throw
                grenade=Grenade(player.rect.centerx + (0.5 * player.rect.size[0]*player.direction),\
                            player.rect.top ,player.direction)
                grenade_group.add(grenade)
                #reduce grenades
                player.grenades-=1
                grenade_thrown=True
                
            if player.in_air:
                player.update_action(2)#2 means jump
            elif moving_left or moving_right:
                player.update_action(1)#1 means run
            else:
                player.update_action(0)#0 means idle   
            screen_scroll,level_complete= player.move(moving_left,moving_right)#will always be qual to the player speed
            bg_scroll-=screen_scroll
            #check if player has completed the level
            if level_complete:
                level+=1
                bg_scroll=0
                world_data=reset_level()
                if level<=MAX_LEVELS:#only if other levels are there
                    with open(f'level{level}_data.csv',newline='') as csvfile:
                        reader=csv.reader(csvfile,delimiter=',')
                        for x,row in enumerate(reader):
                            for y,tile in enumerate(row):
                                world_data[x][y]=int(tile)

                    world= World()
                    player,health_bar=world.process_data(world_data)
    


        else:
            #will handle any situation where player is not alive
            screen_scroll=0#to stop any kind of scrolling
            if restart_button.draw(screen):
                bg_scoll=0
                world_data= reset_level()
                #load in level data and create world
                with open(f'level{level}_data.csv',newline='') as csvfile:
                    reader=csv.reader(csvfile,delimiter=',')
                    for x,row in enumerate(reader):
                        for y,tile in enumerate(row):
                            world_data[x][y]=int(tile)

                world= World()
                player,health_bar=world.process_data(world_data)


    #pygame has a cross feature on top of it which we need to get
    for event in pygame.event.get():
        #quit game
        if event.type==pygame.QUIT:
            run = False
        #keyboard presses
        if event.type==pygame.KEYDOWN:
            #if user presses a
            if event.key == pygame.K_a:
                moving_left=True
            if event.key == pygame.K_d:
                moving_right=True
            if event.key == pygame.K_SPACE:
                shoot=True
            if event.key == pygame.K_q:
                grenade=True        
            if event.key == pygame.K_w and player.alive:
                player.jump=True    
            #if esc pressed then window quits    
            if event.key == pygame.K_ESCAPE:
                run=False    


        #keyboard button released
        if event.type==pygame.KEYUP:
            #if user presses a
            if event.key == pygame.K_a:
                moving_left=False
            if event.key == pygame.K_d:
                moving_right=False  
            if event.key == pygame.K_SPACE:
                shoot=False
            if event.key == pygame.K_q:
                grenade=False
                grenade_thrown=False#ensures when q button is released player can again throw one            
    pygame.display.update()        

pygame.quit()            