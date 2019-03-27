# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 14:12:47 2019
Python version 3.6

@author: Ilmavic
"""
# import required modules for apps
from tkinter import *
import random
import time
from math import sin, cos, pi, atan

# global constatnts
N_FIELD = 1000
COUNT_FLIGHT_OBJECTS = 12
FLIGHT_OBJ = []
ALL_ATTACKING_ROCKETS = []
DEAD_FLIGHT_OBJECTS = []
DEAD_ROCKETS = []
DELAY = 0.2

# creation of canvas battlefield
root = Tk()
label = Label(font='sans 20')
label.pack()
root.title('Flight Apparats')
c = Canvas(root, width=N_FIELD, height=N_FIELD, bg="white")
c.pack()

 
# accessory functions for apps
def get_random_color():
    # function that generate random RGB color
    de=("%02x" % random.randint(0,255))
    re=("%02x" % random.randint(0,255))
    we=("%02x" % random.randint(0,255))
    ge="#"
    return ge+de+re+we
   
def get_rockets_list(options):
    # function that receive rocket list 
    # ----- options is list, when first value is count rocket this type,
    # ----- other arguments characteristics of this type of rockets 
    if options == 0:
        return []
    else:
        rockets_list = []
        for option in options:
            count_rocket = option[0]
            for rocket in range(count_rocket):
                obj_rocket = Rocket(*option[1:])
                rockets_list.append(obj_rocket)
        return rockets_list
    
def get_center_coords(object):
    # function for receive of coordinates center of object
    return round(object.coords[0], 2)+round(object.size/2, 2), round(object.coords[1], 2)+round(object.size/2, 2)
  
def hit_enemy(rocket):
    # boolean function that says whether the rocket hit the target 
    rc = rocket.coords
    ec = rocket.enemy.coords
    rs = rocket.size
    # when the top left corner touches the enemy
    condition_left_up = rc[0] > ec[0] and rc[0] < ec[2] and rc[1] > ec[1] and rc[1] < ec[3]
    # top right corner
    condition_right_up = rc[0]+rs > ec[0] and rc[0]+rs < ec[2] and rc[1] > ec[1] and rc[1] < ec[3]
    # lower left corner
    condition_left_down = rc[0] > ec[0] and rc[0] < ec[2] and rc[1]+rs > ec[1] and rc[1]+rs < ec[3]
    # bottom right corner
    condition_right_down = rc[2] > ec[0] and rc[2] < ec[2] and rc[3] > ec[1] and rc[3] < ec[3]
    if condition_left_up or condition_right_up or condition_left_down or condition_right_down:
        return True
    else:
        return False


class ModelObject():
    # class model object. create object with common characteristics
    # ----- size - size of objects
    # ----- speed - speed of object
    # ----- canvas - the canvas on which the object is painted
    # ----- angle - random angle from 0 to 2 * pi radian which sets the direction
    # ----- coords -random coordinates for this object
    def __init__(self, size, speed, canvas=c):
        self.size = size
        self.speed = speed
        self.canvas = canvas
        self.angle = random.uniform(0, round(2*pi, 2))
        x, y = random.randint(0, N_FIELD-self.size), random.randint(0, N_FIELD-self.size)
        self.coords = [int(x), int(y), int(x+self.size), int(y+self.size)]
        

class FlightObject(ModelObject):
    # class for flight objects
    # ----- firerate - number of rockets fired at one time
    # ----- ball - creation object on the canvas
    # ----- rockets_list - list of rocket
    def __init__(self, size, speed, health_points, rockets=0, firerate=2, canvas=c):
        super().__init__(size, speed, canvas)
        self.firerate = firerate
        self.health_points = health_points
        self.ball = self.canvas.create_oval(self.coords, fill=get_random_color())
        self.rockets_list = get_rockets_list(rockets)
     

    def motion(self):
        # realizes the movement of the object, while when it reaches the field boundary 
        # it is reflected with the angle of reflection equal to the angle of incidence
        x_delta = round(self.speed * cos(self.angle), 2)
        y_delta = round(-1 * self.speed * sin(self.angle), 2)
        coord_ball = c.coords(self.ball)
        # if it reaches the left wall
        if coord_ball[0]+x_delta < 0:
            c.coords(self.ball, abs(coord_ball[0]), coord_ball[1],
                     round(abs(coord_ball[0])+self.size, 2), round(coord_ball[1]+self.size, 2))
            if self.angle > pi:
                self.angle = round(3 * pi - self.angle, 2)
            else:
                self.angle = round(pi - self.angle, 2)
        # if it reaches the top wall
        elif  coord_ball[1]+y_delta < 0:
            c.coords(self.ball, coord_ball[0], abs(coord_ball[1]),
                     round(coord_ball[0]+self.size, 2), round(coord_ball[1]+self.size, 2))
    
            self.angle = round(2 * pi - self.angle, 2)
        # if it reaches the right wall   
        elif coord_ball[0]+x_delta > N_FIELD-self.size:
            c.coords(self.ball, round(2*N_FIELD-coord_ball[0]-x_delta-2*self.size, 2), coord_ball[1],
                     round(2*N_FIELD-coord_ball[0]-x_delta-self.size, 2), coord_ball[1]+self.size)
            if self.angle > pi:
                self.angle = round(3 * pi - self.angle, 2)
            else:
                self.angle = round(pi - self.angle, 2)
        # if it reaches the bottom wall        
        elif coord_ball[1]+y_delta > N_FIELD-self.size:
            c.coords(self.ball, coord_ball[0], round(2*N_FIELD-coord_ball[1]-y_delta-2*self.size, 2),
                     coord_ball[0]+self.size,  round(2*N_FIELD-coord_ball[1]-y_delta-self.size, 2))
            self.angle = round(2 * pi - self.angle, 2)
        # just make a movement in a given direction
        else:
            c.coords(self.ball, coord_ball[0]+x_delta, coord_ball[1]+y_delta,
                     coord_ball[0]+self.size+x_delta, coord_ball[1]+self.size+y_delta)
       # round the coordinates for two characters
        self.coords = list(map(lambda x: round(x, 2), c.coords(self.ball)))
        c.coords(self.ball, self.coords)
    

    def get_max_dist_rockets(self):
        # This method gives a list of rockets for which the range of use is maximum. 
        # while the number of rockets does not exceed the rate of fire
        if self.rockets_list:
            rocket_distance = [rocket.distance_attack for rocket in self.rockets_list]
            max_distance_rockets = [rocket for rocket in self.rockets_list if rocket.distance_attack == max(rocket_distance)]
            if len(max_distance_rockets) > self.firerate:
                max_distance_rockets = max_distance_rockets[:self.firerate]
            return max_distance_rockets
        else:
            return None
    
    def danger_zone(self):
        # gets the coordinates of the affected area. 
        # Being in which another object leads to the launch of rockets
        if self.get_max_dist_rockets():
            max_distance_attack = self.get_max_dist_rockets()[0].distance_attack
            x0_coord = self.coords[0]+0.5*self.size-max_distance_attack if self.coords[0]+0.5*self.size-max_distance_attack > 0 else 0
            y0_coord = self.coords[1]+0.5*self.size-max_distance_attack if self.coords[1]+0.5*self.size-max_distance_attack > 0 else 0
            x1_coord = self.coords[0]+0.5*self.size+max_distance_attack if self.coords[0]+0.5*self.size+max_distance_attack < N_FIELD else N_FIELD
            y1_coord = self.coords[1]+0.5*self.size+max_distance_attack if self.coords[1]+0.5*self.size+max_distance_attack < N_FIELD else N_FIELD
            return [x0_coord, y0_coord, x1_coord, y1_coord]
        else:
            return None
        
    def enemies(self, objects_list):
        # gives a list of objects in the affected area
        if self.danger_zone():
            if self in objects_list:
                other_objects = [obj for obj in objects_list if self != obj]
                enemies_list = []
                for other_object in other_objects:
                    condition_X = other_object.coords[0]+round(self.size/2, 2) >= self.danger_zone()[0] and other_object.coords[0]+round(self.size/2, 2) <= self.danger_zone()[2]
                    condition_Y = other_object.coords[1]+round(self.size/2, 2) >= self.danger_zone()[1] and other_object.coords[1]+round(self.size/2, 2) <= self.danger_zone()[3]
                    if condition_X and condition_Y:
                        enemies_list.append(other_object)
                return enemies_list

                
    
    def rockets_for_enemies(self, objects_list):
        # gives a list of rockets that will attack objects in the affected area
        enemies = self.enemies(objects_list)
        if enemies:
            attacking_rockets = self.get_max_dist_rockets()
            attacking_rockets = attacking_rockets[:min(len(attacking_rockets), len(enemies))]
            if len(enemies) > self.firerate:
                enemies = enemies[:self.firerate]
            for i_rocket in range(len(attacking_rockets)):
                coords = [get_center_coords(self)[0]-round(attacking_rockets[i_rocket].size/2, 2),
                          get_center_coords(self)[1]-round(attacking_rockets[i_rocket].size/2, 2),
                          get_center_coords(self)[0]+round(attacking_rockets[i_rocket].size/2, 2),
                          get_center_coords(self)[1]+round(attacking_rockets[i_rocket].size/2, 2)]
                attacking_rockets[i_rocket].coords = coords
                attacking_rockets[i_rocket].enemy = enemies[i_rocket]
            return attacking_rockets    
        else:
            return None
        
    def is_alive(self):
        # checks if the object is alive
        if self.health_points > 0:
            return True
        else:
            return False
    
        
class Rocket(ModelObject):
    # class rocket
    def __init__(self, speed, distance_attack=100, lifetime=50, damage=40, size=10, canvas=c):
        super().__init__(size, speed, canvas)
        self.angle = 0
        self.distance_attack = distance_attack
        self.lifetime = lifetime
        self.parent = 0
        self.damage = damage
        self.enemy = 0
        self.rocket = 0
        self.coords = None
        self.current_time = 0
        self.color = get_random_color()
    
        
    def motion(self):
        # motion rockets
        self.current_time += 1
        if not self.rocket:
            self.rocket = self.canvas.create_rectangle(self.coords, fill=self.color)
        last_coords = [self.coords[0]+round(self.size/2, 2), self.coords[1]+round(self.size/2, 2)]
        # find angle by coordinates
        delta_X = self.enemy.coords[0]-self.coords[0]+round(self.size/2, 2)
        delta_Y = self.enemy.coords[1]-self.coords[1]+round(self.size/2, 2)
        # first quadrant
        if delta_X > 0 and delta_Y <= 0:
            self.angle = (-1)*atan(delta_Y/delta_X)
        # second quadrant
        elif delta_X < 0 and delta_Y <= 0:
            self.angle = pi-atan(delta_Y/delta_X)
        #  third quadrant        
        elif delta_X < 0 and delta_Y > 0:
            self.angle = pi-atan(delta_Y/delta_X)
        # fourth quadrant
        elif delta_X > 0 and delta_Y > 0:
            self.angle = 2*pi-atan(delta_Y/delta_X)
        elif delta_X == 0:
            self.angle = 0.5*pi if delta_Y < 0 else 1.5*pi
        x_delta = round(self.speed * cos(self.angle), 2)
        y_delta = round(-1 * self.speed * sin(self.angle), 2)
        self.coords = [self.coords[0]+x_delta, self.coords[1]+y_delta, self.coords[2]+x_delta, self.coords[3]+y_delta]
        self.coords = list(map(lambda x: round(x, 2), self.coords))
        c.coords(self.rocket, self.coords)
        # creation trajectory of rocket
        current_coords = [self.coords[0]+round(self.size/2, 2), self.coords[1]+round(self.size/2, 2)] 
        trajectory_coords = last_coords + current_coords
        c.create_line(trajectory_coords,dash=(10,2), fill=self.color)
        
    def die_enemy(self):
        # check if the rocket is working
        # the rocket acts if the lifetime has expired or it hit the target
        if self.current_time >= self.lifetime:
            self.rocket = None
            return True
        elif hit_enemy(self):
            self.enemy.health_points -= self.damage
            self.rocket = None
            return True
        else:
            return False

# creation FLIGHT OBJECTS     
for i in range(COUNT_FLIGHT_OBJECTS):
#  constructor of flight object: size, speed, health_points, rockets=0, firerate=2, canvas=c
# constructor of rocket: speed, distance_attack=100, lifetime=50, damage=40, size=10, canvas=c
# add flight objects in general list og flight objects    
    speed_fl_obj = random.randint(1, 20)
    speed_rocket1 = random.randint(speed_fl_obj, 30)
    speed_rocket2 = random.randint(speed_fl_obj, 30)
    speed_rocket3 = random.randint(speed_fl_obj, 25)
    distance_attack1 = random.randint(20, 50)
    distance_attack2 = random.randint(30, 60)
    distance_attack3 = random.randint(50, 80)
    lifetime1 = random.randint(100, 200)
    lifetime2 = random.randint(150, 220)
    lifetime3 = random.randint(50, 300)
    damage1 =  30
    damage2 =  20
    damage3 =  15
    rockets = [[3, speed_rocket1, distance_attack1, lifetime1, damage1], 
                 [2, speed_rocket2, distance_attack2, lifetime2, damage2],
                 [3, speed_rocket3, distance_attack3, lifetime3, damage3]]
    flight_object =  FlightObject(20, speed_fl_obj, 100, rockets)
    FLIGHT_OBJ.append(flight_object)
    
flag = True 

# Simulation airbattle 
while flag: 
    for fl_obj in FLIGHT_OBJ:
        # if the flight object is dead, 
        # then add to the list of dead flight objects
        if not fl_obj.is_alive():
            fl_obj.ball = None
            DEAD_FLIGHT_OBJECTS.append(fl_obj)
        else:
            # otherwise we move the object and check if there are any enemies in the affected area, 
            # if we have, then we get a list of rockets to attack the enemy 
            # and add to the general list of attacking missiles
            fl_obj.motion()
            if fl_obj.enemies(FLIGHT_OBJ):
                attacking_rockets = fl_obj.rockets_for_enemies(FLIGHT_OBJ)
                ALL_ATTACKING_ROCKETS += attacking_rockets
                fl_obj.rockets_list = [rocket for rocket in fl_obj.rockets_list if rocket not in attacking_rockets]
    # redefine the list of flying objects except dead            
    FLIGHT_OBJ = [flight_object for flight_object in FLIGHT_OBJ if flight_object not in DEAD_FLIGHT_OBJECTS]
    # make a move from the list of attacking rocket, 
    # excluding from the list of rockets that are destroyed
    if ALL_ATTACKING_ROCKETS:
        for rocket in ALL_ATTACKING_ROCKETS:
            if not rocket.die_enemy():
                rocket.motion()
            else:
                DEAD_ROCKETS.append(rocket)
        ALL_ATTACKING_ROCKETS = [rocket for rocket in ALL_ATTACKING_ROCKETS if rocket not in DEAD_ROCKETS]
    c.update()  
    time.sleep(DELAY)
    firepower = []
    # calculate coomon count of rockets on battlefield all objects
    for fl_obj in FLIGHT_OBJ:
        firepower += fl_obj.rockets_list
    # if one flying object or ammunition remains zero, 
    # we complete the simulation    
    if len(FLIGHT_OBJ) == 1 or len(firepower) == 0:
        flag = False
    
c.create_text(N_FIELD/2, 20, text="Battle is finished!!!", justify=CENTER, font="Verdana 21")
root.mainloop()



