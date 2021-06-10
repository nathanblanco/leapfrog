# This is code for the Leapfrog task introduced in Knox, Otto, Stone, & Love (2012).
# It requires python 2, numpy, pygame, and pypsyexp (which is in the 'lib' folder) to run.
# code written by Ross Otto, Brad Knox, and Nate Blanco

import os, sys, signal
import math
from string import *
from random import random, randint, shuffle, normalvariate, uniform, choice
import pygame
import datetime
from pygame.locals import *
import tempfile
from time import sleep
from lib.pypsyexp import *
import eztext
execfile('params.py')
execfile('text.py')
execfile('inst_text.py')


laptop = False



#------------------------------------------------------------
# MouseButton Classes (statelights, next, resp)
#------------------------------------------------------------
class StateButton(MouseButton):
    def __init__(self, x, y, w, h, myimage):
        # This is how you call the superclass init
        MouseButton.__init__(self, x, y, w, h)
        self.image = myimage
    def draw(self, surface):
        self.image_rect = self.image.get_rect()
        self.image_rect.center = self.rect.center
        surface.blit(self.image,self.image_rect)
    def do(self):
        print "Implemented in subclasses"

class NextButton(MouseButton):
    def __init__(self, x, y, w, h, myimage, snd, app):
        # This is how you call the superclass init
        MouseButton.__init__(self, x, y, w, h)
        self.image = myimage
        self.snd = snd
    def draw(self, surface):
        self.image_rect = self.image.get_rect()
        self.image_rect.center = self.rect.center
        surface.blit(self.image,self.image_rect)
    def do(self):
        self.snd.play()

class RespButton(MouseButton):
    def __init__(self, x, y, w, h, id, myimage, myimagepressed, snd, app):
        # This is how you call the superclass init
        MouseButton.__init__(self, x, y, w, h)
        self.myid = id
        self.image = myimage
        self.imagep = myimagepressed
        self.snd = snd
    def draw(self, surface):
        self.image_rect = self.image.get_rect()
        self.image_rect.center = self.rect.center
        surface.blit(self.image,self.image_rect)
    def do(self, surface):
        self.image_rect = self.imagep.get_rect()
        self.image_rect.center = self.rect.center
        surface.blit(self.imagep,self.image_rect)
        pygame.display.flip()
        self.snd.play()
        pygame.time.wait(100)
        self.image_rect = self.image.get_rect()
        self.image_rect.center = self.rect.center
        surface.blit(self.image,self.image_rect)
        pygame.display.flip()
        return self.myid

#------------------------------------------------------------
# MelMat Class
#------------------------------------------------------------
class DDMExperiment(Experiment):
    def __init__(self, laptop, screenres, experimentname):
        
        
        self.experimentname = experimentname
 
        [self.cond, self.ncond, self.subj] = self.get_cond_and_subj_number('patterncode.txt')
        
                
        Experiment.__init__(self, laptop, screenres, experimentname)
        self.load_all_resources('images', 'sounds')
        
        self.subj = self.record_subj_num()

        print "I am subject %s in condition: %s" % (self.subj, str(self.cond))
        
        self.num_missed_trials = 0
        
        self.p_flip = 0.075
        self.earnings = 0.0


        
        self.filename = "data/%s.txt" % self.subj
        self.datafile = open(self.filename, 'w')

        [self.a_resp ,self.b_resp] = ['l', 'r']
        
        
    #------------------------------------------------------------
    # show_thanks
    #------------------------------------------------------------
    def show_thanks(self):        
        background = self.show_centered_image('thanks.gif',white)

        subj_text = "SUBJECT NUMBER: %s" % self.subj
        self.place_text_image(background, subj_text, 32, 0, 250, black, white)
        
        # MAYBE DO SOMETHING HERE
        #self.earnings = 2.00 # was $1.
        #entry_text = "YOU HAVE WON: $ %.2f" % int(self.earnings)
        #entry_text = "YOU HAVE WON: $ %.2f" % int(self.earnings)
           
        #self.place_text_image(background, entry_text, 32, 0, -80, black, white)
        self.update_display(background)
        
        self.escapable_sleep(10000)
        self.on_exit()

        while 1:
            [res, rescode, rt] = self.get_response()
        raise SystemExit
    
    #------------------------------------------------------------
    # get_click_response
    #------------------------------------------------------------
    def get_click_response(self):
        exit = False;
        while not exit:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.on_exit()
                elif event.type == KEYDOWN:
                    if pygame.key.get_pressed()[K_LSHIFT] and pygame.key.get_pressed()[K_BACKQUOTE]:
                        self.on_exit()
                    elif( pygame.key.get_pressed()[K_z]):
                        for but in self.buttons:
                            if(but.myid=='l'):
                                but.do(self.screen)
                                return 'l'
                    elif( pygame.key.get_pressed()[K_SLASH]):
                        for but in self.buttons:
                            if(but.myid=='r'):
                                but.do(self.screen)
                                return 'r'

        return rescode
    
    #------------------------------------------------------------
    # get_click_response_and_rt
    #------------------------------------------------------------
    def get_click_response_and_rt(self):
        time_stamp = pygame.time.get_ticks()
        res = self.get_click_response()
             
        if (res == 'l'):
            rescode = '1'
        elif (res == 'r'):
            rescode = '0'
        
        rt = pygame.time.get_ticks() - time_stamp
        return [res, rescode, rt]
 
    #--------------------------------------------------------------
    # draw_buttons
    #--------------------------------------------------------------
    def draw_buttons(self, mysurf):
        self.buttons = []

        x_pos = 160
        self.buttons = self.buttons + [RespButton( x_pos, 262, 107,108, 'l', self.resources['button-l.gif'],
                                                   self.resources['button-l.gif'], self.resources["buttonpress.wav"], self)]
        self.buttons = self.buttons + [RespButton( x_pos+(180*3), 262, 107,108, 'r', self.resources['button-r.gif'],
                                                   self.resources['button-r.gif'], self.resources["buttonpress.wav"], self)]
        for i in self.buttons:
            i.draw(mysurf)
    
    #---------------------------------------------------------------
    # draw_chosen_button
    #---------------------------------------------------------------
    def draw_chosen_button(self, background, chosen_button):
        if(chosen_button == 'l'):
            pygame.draw.rect(background, (0,255,255), (158,260,110,110), 3)
        elif(chosen_button == 'r'):
            pygame.draw.rect(background, (0,255,255), (698,260,110,110), 3)
    
    #-----------------------------------------------------------------
    # get_payoff_value
    #------------------------------------------------------------------
    def get_payoff_value(self, res): 
        is_switch = 0
        if(random() < self.p_flip):
                is_switch = 1
                if(self.last_changed == 'b'): 
                    print '***changing A'
                    self.last_changed  = 'a'
                    self.a_reward += 20.0
                else:
                    print '***changing B'
                    self.last_changed = 'b'
                    self.b_reward += 20.0

        if(res == self.a_resp): payoff = self.a_reward
        else: payoff = self.b_reward
        return payoff
    
    #---------------------------------------------------------------------
    # draw_trial_reward
    #---------------------------------------------------------------------
    def draw_trial_reward(self, mysurf, payoff ):
        self.place_text_image(mysurf, ' %.0f'%(payoff), 90, -45, 10, white , black)
        self.update_display(mysurf)
    
    #------------------------------------------------------------
    # do_trial
    #------------------------------------------------------------
    def do_trial(self, background, trialnum, is_practice=False):
        print '\n\ntrial ' + str(trialnum)

        background = self.show_centered_image('new_interface.gif',black)
        self.place_text_image(background, "CHOOSE", 44, -20, 200, white, black)
        self.draw_buttons(background)
        self.update_display(background)

        pygame.mixer.init()
        time_stamp = pygame.time.get_ticks()
        resp = None
        rt = None
        wait_time = None
        current_stage = None
        current_interval = 1
        while(True):
            current_time_elapsed = pygame.time.get_ticks() - time_stamp
            
            if(current_stage == 'outcome'):
                if( current_time_elapsed >= (RESPONSE_TIME_ALLOWED + OUTCOME_TIME)):
                    break
                else:
                    continue            

            if(wait_time != None):
                if(current_time_elapsed >= wait_time):
                    wait_time = None
                    current_stage = 'outcome'
                    if(rt == None):
                        rt = -1
                        self.num_missed_trials += 1

                    if (resp == self.a_resp):
                        hit = 1
                    else:
                        hit = 0

                    if(resp == None):
                        hit = -1
                        resp =-1
                        payoff = -1

                    if(resp != -1):
                        self.place_text_image(background, "             ", 44, -20, 200, white, black)
                        self.draw_trial_reward(background, payoff)
                        self.update_display(background)
                    else:
                        self.place_text_image(background, "X", 200, -10, 0, (255,0,0), black)
                        self.place_text_image(background, 'TOO SLOW, TRY AGAIN', 44, -20, 200, white, black)
                        self.update_display(background)
                else:
                    continue

            if((current_time_elapsed >= RESPONSE_TIME_ALLOWED) and (wait_time == None)):
                stage = 'wait'
                wait_time = RESPONSE_TIME_ALLOWED - current_time_elapsed

            if(current_time_elapsed >= (current_interval*250)):
                pygame.mixer.init()
                current_interval += 1



            if(resp == None):
                for event in pygame.event.get():
                    if(event.type == QUIT):
                        self.on_exit()
                    elif(event.type == KEYDOWN):
                        if pygame.key.get_pressed()[K_LSHIFT] and pygame.key.get_pressed()[K_BACKQUOTE]:
                            self.on_exit()
                        elif (pygame.key.get_pressed()[K_z]):
                            resp = 'l'
                            rt = pygame.time.get_ticks() - time_stamp
                            pygame.draw.rect(background, black, (0, 550, 1000,800), 0)
                            self.draw_chosen_button(background, resp)
                            self.place_text_image(background, "   WAIT   ", 44, -20, 200, white, black)
                            self.update_display(background)
                            if(not is_practice): payoff = self.get_payoff_value(resp)
                            else: payoff = uniform(.1, .4)
                            print 'payoff:' + str(payoff)

                        elif( pygame.key.get_pressed()[K_SLASH]):
                            resp = 'r'
                            rt = pygame.time.get_ticks() - time_stamp
                            self.draw_chosen_button(background,resp)
                            self.place_text_image(background, "   WAIT   ", 44, -20, 200, white, black)
                            self.update_display(background)
                            if(not is_practice): payoff = self.get_payoff_value(resp)
                            else: payoff = uniform(.1, .4)
                            print 'payoff:' + str(payoff)
                        
        

        pygame.event.clear()
        
        if(not is_practice): self.output_trial([self.subj, self.cond, self.p_flip, 2, trialnum, self.a_reward, self.b_reward, resp, payoff, rt, self.num_missed_trials])

        if(resp !=  -1): return True
        else: return False


    #-------------------------------------------------------------
    # do_same_diff_trial  (practice)
    #-------------------------------------------------------------
    def do_same_diff_trial(self, background, trialnum, trial_type='sampling'):
        background = self.show_centered_image('new_interface.gif',black)
        self.place_text_image(background, 'TRIAL:', 24, -20, -30, white, black)  
        self.place_text_image(background, str(trialnum), 44, -20, 0, blue, black)  

        if(random() < self.p_flip):
            if(self.last_changed == 'b'): 
                self.last_changed  = 'a'
                a_status = 'CHANGED'
                b_status = 'SAME'
                a_color=red
                b_color = white
            else:
                self.last_changed = 'b'
                b_status  = 'CHANGED'
                a_status = 'SAME'
                b_color = red
                a_color = white
        else:
            [a_status,b_status] = ['SAME','SAME']
            [a_color, b_color] = [white, white]

        self.draw_buttons(background)
        self.place_text_image(background, a_status, 44, -290, 10, a_color, black)  
        self.place_text_image(background, b_status, 44, 240, 10, b_color, black)  

        self.update_display(background)

        pygame.time.wait(500)

        pygame.event.clear()
 
        
        if a_status=='SAME':
        	tempA=0
        else:
        	tempA=1
        if b_status=='SAME':
        	tempB=0
        else:
        	tempB=1
        self.output_trial([self.subj, self.cond, self.p_flip, 0, trialnum, tempA, tempB, -9, -9, -9, -9])

    #---------------------------------------------------------
    # report_num_flips
    #---------------------------------------------------------
    def report_num_flips(self, block):
        background = self.show_centered_image('instructions-background.gif',black)

        last_txtbox_value = None
        txtbx = eztext.Input(maxlength=45, color=(0,255,0), prompt='Type here: ')

        while 1:
            events = pygame.event.get()
            background = self.show_centered_image('instructions-background.gif',black)
            txtbx.update(events, background)

            if((len(txtbx.value) > 0) and (txtbx.value[-1] == 'R')): break

            if(txtbx.value != last_txtbox_value):
                self.place_text_image(background, 'In the next hundred trials, how many CHANGES do you expect to see?', 32, -60, -200, white, black)
                self.place_text_image(background, 'Type your answer below. Press RETURN when you are done.', 32, -100, -150, white, black)
                self.update_display(background)
                txtbx.draw(background)
                self.update_display(background)
                last_txtbox_value = txtbx.value

        self.output_trial([self.subj, self.cond, self.p_flip, 1, block, -9, -9, txtbx.value[0:-1], -9, -9, -9])
        

    #------------------------------------------------------------
    # show_instructions
    #------------------------------------------------------------
    def show_instructions(self, inst_num, butfn, butfn2):        
        background = self.show_centered_image('instructions-background.gif',black)

        inst_text = eval(inst_num)
        text(inst_text, (45,60), self.screen, background)

        pygame.display.flip()            
        self.escapable_sleep(1000)

        self.button = NextButton(570, 700, 265, 50, self.resources[butfn],self.resources["buttonpress.wav"], self)
        self.button.draw(self.screen)
        if butfn2 != None:
            self.button2 = NextButton(140, 700, 265, 50, self.resources[butfn2],self.resources["buttonpress.wav"], self)
            self.button2.draw(self.screen)
        pygame.display.flip()


        retval = NEXT
        exit = False;
        while not exit:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.on_exit()
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.on_exit()
                elif event.type == MOUSEBUTTONDOWN:
                    (x,y) = pygame.mouse.get_pos()
                    if (self.button.containsPoint(x, y)):
                        self.button.do()
                        exit = True
                        retval = NEXT
                    if butfn2 != None:
                        if (self.button2.containsPoint(x, y)):
                            self.button2.do()
                            exit = True
                            retval = BACK
        return retval

    #------------------------------------------------------------
    # record_subj_num
    #------------------------------------------------------------
    def record_subj_num(self):
        background = self.show_centered_image('instructions-background.gif',black)

        last_txtbox_value = None
        txtbx = eztext.Input(maxlength=45, color=(0,255,0), prompt='Walk-in ID: ')


        while 1:
            # events for txtbx
            events = pygame.event.get()
            # update txtbx
            txtbx.update(events, background)
            # blit txtbx on the sceen

            if((len(txtbx.value) > 0) and (txtbx.value[-1] == 'R')): break

            if(txtbx.value != last_txtbox_value):
                #self.place_text_image(background, 'In the next hundred trials, how many CHANGES do you expect to see?', 32, -60, -200, white, black)
                self.update_display(background)
                txtbx.draw(background)
                self.update_display(background)
                last_txtbox_value = txtbx.value


        return last_txtbox_value

            
    #------------------------------------------------------------------------------------------
    # helper function 
    #------------------------------------------------------------------------------------------
    def do_regular_exp_helper(self):
    
        background = self.show_centered_image('instructions-background.gif',black)
    
    
        self.earnings = 0.0
        self.num_missed_trials = 0


        self.earnings = 0.0
        self.a_reward = 10.
        self.b_reward = 20.
        self.last_changed = 'b'

    
    
        for i in range(1,ntrials+1):            
            trial_ok = False
            while(not trial_ok):
                trial_ok = self.do_trial(background, i )

            if(self.num_missed_trials > 3):
                pygame.mouse.set_visible(True)
                self.show_instructions('missed_trials', 'next.gif', None)
                pygame.mouse.set_visible(False)
                self.num_missed_trials = 0


            if ((i%50)==0): 
                    pygame.mouse.set_visible(True)
                    if (i!=ntrials):
                        self.show_instructions('break_single', 'next.gif', None)
                    pygame.mouse.set_visible(False)

       
                
                
    #------------------------------------------------------------
    # do_regular_exp
    #------------------------------------------------------------
    def do_regular_exp(self):
          
          
        
        background = self.show_centered_image('instructions-background.gif',black)
        pygame.mouse.set_visible(1)          
        stage = 1
  
        while(stage!=4):
            if stage == 1:
                if (self.show_instructions('pre_task_inst_1',  'next.gif', 'back.gif')==BACK):
                    stage = 1
                else:
                    stage = 2
            elif stage == 2:
                if self.show_instructions('pre_task_inst_2',  'next.gif', 'back.gif')==BACK:
                    stage = 1
                else:
                    stage = 3
            elif stage == 3:
                if self.show_instructions('pre_task_inst_3',  'next.gif', 'back.gif')==BACK:
                    stage = 2
                else:
                    stage = 4

        pygame.mouse.set_visible(0)          

        self.last_changed = 'b'

        for block in range(n_practice_blocks):
            self.report_num_flips(block)
            for trial in range(100):
                self.do_same_diff_trial(background,trial)
        self.report_num_flips(block)

        pygame.mouse.set_visible(1)          
        stage = 1
        while(stage!=3):
            if stage == 1:
               if (self.show_instructions('task_inst_gains',  'next.gif', 'back.gif')==BACK):
                    stage = 1
               else:
                    stage = 2
            elif stage == 2:
                if self.show_instructions('task_inst_2',  'next.gif', 'back.gif')==BACK:
                    stage = 1
                else:
                    stage = 3

        background = self.show_centered_image('new_interface.gif',black)
        self.place_text_image(background, "CHOOSE", 44, -20, 200, white, black)
        self.draw_buttons(background)

        pygame.mouse.set_visible(False)
        pygame.time.wait(1000)
        
        self.do_regular_exp_helper()
        
                
        self.show_thanks()

#-----------------------
# main                   
#------------------------
def main():
    global laptop, experimentname;
    experiment = DDMExperiment(laptop, screenres, experimentname)
    experiment.do_regular_exp()

#------------------------------------------------------------
# let's start
#------------------------------------------------------------
if __name__ == '__main__':
    main()
