pre_task_inst_1 = ['Welcome to our experiment.',
                   'In this experiment, we are interested in how people deal with making choices in changing environments.',
                   'In this experiment you will be making a series of decisions in order to earn points.',
                   '',
                   '',
                   '']
pre_task_inst_2 = ['Each time you press one of the two buttons, you will be told how many points your choice resulted in.',
                   '',
                   'RED and GREEN will both keep getting more valuable over the course of the experiment. RED and GREEN will take turns being the better option. The only way to know which option is currently better is by sampling the options.',
                   '',
                   'While you cannot always know which option is currently the highest paying, your job is to get the highest score that you can.']

pre_task_inst_3 = [ 'Before you start actually making choices, we want you to learn a little bit about how the two options change.',
                    '',
                    'In this part of the experiment, you will watch the options changing over time.'
                    '',
                    'Each trial, the options will either both stay the SAME or one will CHANGE.'
                    '',
                    'Before seeing each block of 100 trials, you will be asked how many changes you predict you will observe. Each block of 100 trials has the same RATE of change, so you should rely on your previous experience to make predictions.', 
                    '',
                    'As both the GREEN and RED options will change, We want to know how many changes in TOTAL you expect to see.']

#------------------------------------------------------------
# Page 3
#------------------------------------------------------------

task_inst_losses = ['Good. Now we want you to make actual choices based on what you have learned. Each time you press one of the two buttons, you will be told how many points your choice resulted in.',
               
               'In this version, for either option you will LOSE points. Your goal is to minimize the number of points that you lose.',
               'Right now:',
               '    The GREEN OPTION will earn -300 points',
               '    The RED OPTION will earn -290 points',
               'At the start of this experiment, the BETTER choice right now is RED. However, RED won\'t always be better than GREEN. Sometimes RED will be better, and sometimes GREEN will be better.',
               
               
               'RED and GREEN will both keep getting more valuable over the course of the experiment. RED and GREEN will take turns being the better option. The only way to know which option is currently better is by sampling the options. RED and GREEN will change at the same rate that you just observed.',
               'While you cannot always know which option is currently the best, your job is to get the highest score that you can can by minimizing your losses.']
               
task_inst_gains = ['Good. Now we want you to make actual choices based on what you have learned. Each time you press one of the two buttons, you will be told how many points your choice resulted in.',
               
               'In this version, for either option you will GAIN points. Your goal is to maximize the number of points that you gain.',
               'Right now:',
               '    The GREEN OPTION will earn 10 points',
               '    The RED OPTION will earn 20 points',
               'At the start of this experiment, the BETTER choice right now is RED. However, RED won\'t always be better than GREEN. Sometimes RED will be better, and sometimes GREEN will be better.',
               
               
               'RED and GREEN will both keep getting more valuable over the course of the experiment. RED and GREEN will take turns being the better option. The only way to know which option is currently better is by sampling the options. RED and GREEN will change at the same rate that you just observed.',
               'While you cannot always know which option is currently the best, your job is to get the highest score that you can can by maximizing your gains.']


task_inst_2 = ['',
               'When the screen says CHOOSE, you will make your choice with the keyboard.'
               '',
               'To select the GREEN option, press \'Z\'',
               'To select the RED option, press \'/\'',
               '',
               'You may find it easy to keep your two fingers on the Z and \'/\' keys. After you choose you will see how many points you just received.',
               '',
               'Today, you will make ' + str(ntrials) + ' choices.']



inst_single =['You may start when you are ready.']


missed_trials = ['You need to be responding more quickly when you see "CHOOSE" on the screen',
                             '',
                             'Please pay closer attention and try to respond more quickly.']


break_single = ['Please take a break.',
                '','','',
                'You may continue when you are ready']


