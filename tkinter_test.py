# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 14:12:47 2019

@author: Ilmavic
"""

from tkinter import *
import random
import time
from math import sin, cos, pi, atan

N_FIELD = 1000 
FLIGHT_OBJ = []
ALL_ATTACKING_ROCKETS = []

root = Tk()
label = Label(font='sans 20')
label.pack()
root.title('Flight Apparats')
c = Canvas(root, width=N_FIELD, height=N_FIELD, bg="white")
c.pack()

 
#print(c.coords(ball))
# print('x1-x0=', round(c.coords(self.ball)[2]-c.coords(self.ball)[0], 1), 'y1-y0=', round(c.coords(self.ball)[3]-c.coords(self.ball)[1], 2))

 
def get_random_color():
    de=("%02x" % random.randint(0,255))
    re=("%02x" % random.randint(0,255))
    we=("%02x" % random.randint(0,255))
    ge="#"
    return ge+de+re+we

def get_rockets_list(options):
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
    

#def gg(dt):
##    print(gg)
#    rockets_list = []
#    for option in dt:
#        count_rocket = option[0]
#        for r in range(count_rocket):
#            print(option[1:])
#    return dt
#
#tt = gg([[2, 5, 8, 4000, 20],[2, 7, 6, 2000, 10],[1, 3]])
   
class ModelObject():
    def __init__(self, size, speed, canvas=c):
        self.size = size
        self.speed = speed
        self.canvas = canvas
        self.angle = random.uniform(0, round(2*pi, 2))
        x, y = random.randint(0, N_FIELD-self.size), random.randint(0, N_FIELD-self.size)
        self.coords = [int(x), int(y), int(x+self.size), int(y+self.size)]

class FlightObject(ModelObject):
    def __init__(self, size, speed, health_points, rockets=0, firerate=2, canvas=c):
        super().__init__(size, speed, canvas)
        self.firerate = firerate
        self.health_points = health_points
        self.ball = self.canvas.create_oval(self.coords, fill=get_random_color())
        self.rockets_list = get_rockets_list(rockets)
        
    def motion(self):
        x_delta = round(self.speed * cos(self.angle), 2)
        y_delta = round(-1 * self.speed * sin(self.angle), 2)
        coord_ball = c.coords(self.ball)
        # если достигает левой стенки
        if coord_ball[0]+x_delta < 0:
            c.coords(self.ball, abs(coord_ball[0]), coord_ball[1],
                     round(abs(coord_ball[0])+self.size, 2), round(coord_ball[1]+self.size, 2))
            if self.angle > pi:
                self.angle = round(3 * pi - self.angle, 2)
            else:
                self.angle = round(pi - self.angle, 2)
        # если достигает верхней стенки
        elif  coord_ball[1]+y_delta < 0:
            c.coords(self.ball, coord_ball[0], abs(coord_ball[1]),
                     round(coord_ball[0]+self.size, 2), round(coord_ball[1]+self.size, 2))
    
            self.angle = round(2 * pi - self.angle, 2)
        # если достигает правой стенки    
        elif coord_ball[0]+x_delta > N_FIELD-self.size:
            c.coords(self.ball, round(2*N_FIELD-coord_ball[0]-x_delta-2*self.size, 2), coord_ball[1],
                     round(2*N_FIELD-coord_ball[0]-x_delta-self.size, 2), coord_ball[1]+self.size)
            if self.angle > pi:
                self.angle = round(3 * pi - self.angle, 2)
            else:
                self.angle = round(pi - self.angle, 2)
        elif coord_ball[1]+y_delta > N_FIELD-self.size:
            c.coords(self.ball, coord_ball[0], round(2*N_FIELD-coord_ball[1]-y_delta-2*self.size, 2),
                     coord_ball[0]+self.size,  round(2*N_FIELD-coord_ball[1]-y_delta-self.size, 2))
            self.angle = round(2 * pi - self.angle, 2)
        else:
            c.coords(self.ball, coord_ball[0]+x_delta, coord_ball[1]+y_delta,
                     coord_ball[0]+self.size+x_delta, coord_ball[1]+self.size+y_delta)
       # Округлим координаты для двух знаков
        self.coords = list(map(lambda x: round(x, 2), c.coords(self.ball)))
        c.coords(self.ball, self.coords)
    
    def get_max_dist_rockets(self):
        if self.rockets_list:
            rocket_distance = [rocket.distance_attack for rocket in self.rockets_list]
            max_distance_rockets = [rocket for rocket in self.rockets_list if rocket.distance_attack == max(rocket_distance)]
            if len(max_distance_rockets) > self.firerate:
                max_distance_rockets = max_distance_rockets[:self.firerate]
            return max_distance_rockets
        else:
            return None
    
    def danger_zone(self):
        if self.get_max_dist_rockets():
            max_distance_rocket = self.get_max_dist_rockets()[0]
            x0_coord = self.coords[0]+0.5*self.size-max_distance_rocket.distance_attack if self.coords[0]+0.5*self.size-max_distance_rocket.distance_attack > 0 else 0
            y0_coord = self.coords[1]+0.5*self.size-max_distance_rocket.distance_attack if self.coords[1]+0.5*self.size-max_distance_rocket.distance_attack > 0 else 0
            x1_coord = self.coords[0]+0.5*self.size+max_distance_rocket.distance_attack if self.coords[0]+0.5*self.size+max_distance_rocket.distance_attack < N_FIELD else N_FIELD
            y1_coord = self.coords[1]+0.5*self.size+max_distance_rocket.distance_attack if self.coords[1]+0.5*self.size+max_distance_rocket.distance_attack < N_FIELD else N_FIELD
            return [x0_coord, y0_coord, x1_coord, y1_coord]
        else:
            return None
        
        
    def get_enemies(self, objects_list):
        if self.danger_zone():
            if self in objects_list:
                other_objects = [obj for obj in objects_list if self != obj]
                attacking_rockets = self.get_max_dist_rockets()
                for rocket in attacking_rockets:
                    rocket.coords = self.coords
                enemies_list = []
                for other_object in other_objects:
                    condition_X = other_object.coords[0]+round(self.size/2, 2) >= self.danger_zone()[0] and other_object.coords[0]+round(self.size/2, 2) <= self.danger_zone()[2]
                    condition_Y = other_object.coords[1]+round(self.size/2, 2) >= self.danger_zone()[1] and other_object.coords[1]+round(self.size/2, 2) <= self.danger_zone()[3]
                    if condition_X and condition_Y:
                        enemies_list.append(other_object)
                if enemies_list:
                    if len(enemies_list) > self.firerate:
                        enemies_list = enemies_list[:self.firerate]
                    for i_rocket in range(len(attacking_rockets)):
                        attacking_rockets[i_rocket].coords = self.coords
                        attacking_rockets[i_rocket].enemy = enemies_list[i_rocket]
                global ALL_ATTACKING_ROCKETS        
                ALL_ATTACKING_ROCKETS += attacking_rockets
                return enemies_list
            else: 
                print("WARNING: Object %s don't exist on battlefield!" % self)
        else:
            return None
    
        
class Rocket(ModelObject):
    def __init__(self, speed, distance_attack=100, lifetime=5000, damage=30, size=10, canvas=c):
        super().__init__(size, speed, canvas)
        self.angle = 0
        self.distance_attack = distance_attack
        self.lifetime = lifetime
        self.parent = 0
        self.damage = damage
        self.enemy = 0
        self.rocket = 0
        self.coords = None
#        self.rocket = self.canvas.create_rectangle(self.coords, fill=get_random_color())
        
    def motion(self):
        if not self.rocket:
            self.rocket = self.canvas.create_rectangle(self.coords, fill=get_random_color())
        # найти угол по координатам
        delta_X = self.enemy.coords[0]-self.coords[0]+round(self.size/2, 2)
        delta_Y = self.enemy.coords[1]-self.coords[1]+round(self.size/2, 2)
        # первый квадрант
        if delta_X > 0 and delta_Y <= 0:
            self.angle = (-1)*atan(delta_Y/delta_X)
        # второй квадрант
        elif delta_X < 0 and delta_Y <= 0:
            self.angle = pi-atan(delta_Y/delta_X)
        #  третий квадрант        
        elif delta_X < 0 and delta_Y > 0:
            self.angle = pi-atan(delta_Y/delta_X)
        # четвертый квадрант
        elif delta_X > 0 and delta_Y > 0:
            self.angle = 2*pi-atan(delta_Y/delta_X)
        elif delta_X == 0:
            self.angle = 0.5*pi if delta_Y < 0 else 1.5*pi
        x_delta = round(self.speed * cos(self.angle), 2)
        y_delta = round(-1 * self.speed * sin(self.angle), 2)
        self.coords = [self.coords[0]+x_delta, self.coords[1]+y_delta, self.coords[2]+x_delta, self.coords[3]+y_delta]
        self.coords = list(map(lambda x: round(x, 2), self.coords))
        c.coords(self.rocket, self.coords)
        
for i in range(5):
#  конструктор  size, speed, health_points, rockets=0, firerate=2, canvas=c
    sp = random.randint(1, 20)
    tt =  FlightObject(20, sp, 30, [[3, random.randint(1, 20), random.randint(1, 20), random.randint(100, 200)], [2, random.randint(1, 20), random.randint(1, 20), random.randint(150, 220)]])
    FLIGHT_OBJ.append(tt)  
while 1:
    for f in FLIGHT_OBJ:
        f.motion()
        if f.get_enemies(FLIGHT_OBJ):
            print('Yeaa=', f)
#        print('rockets_max=', f.get_max_dist_rocket())
#        print('enemies_max=', f.get_enemies(FLIGHT_OBJ)) 
    if ALL_ATTACKING_ROCKETS:
        for r in ALL_ATTACKING_ROCKETS:
            r.motion()
    c.update()  
    time.sleep(0.1)
    

root.mainloop()
#time.sleep(3) 
#c.delete(tt)       


#tt = FlightObject(10, 30, 30, rockets=[[2, 5, 8, 4000, 20, 11],[2, 7, 6, 2000, 10, 15],[1, 3]])
#tt = Rocket(*[3, 2, 5, 8, 4000, 20][1:])


