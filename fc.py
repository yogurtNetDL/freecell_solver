import random,bisect,copy
seed = 1

def color(cardn): return int(cardn / 26)
def suit(cardn): return int(cardn / 13)
def number(cardn): 
    if cardn >= 0: return cardn % 13
    else: return -1
def thecard(suit, number): 
    if number <= 12: return suit * 13 + number
    else: return 52
def number_poker(cardn):
    x = cardn % 13 + 1
    if x == 1:
        return 'A'
    elif x == 11:
        return 'J'
    elif x == 12:
        return 'Q'
    elif x == 13:
        return 'K'
    else:
        return str(x)

def generate_case(seed):
    random.seed(seed)
    cards = list(range(52))
    random.shuffle(cards)
    case = []
    for i in range(4):
        case.append([-1]+cards[i*7:7*(i+1)])
    for i in range(4):
        case.append([-1]+cards[28+i*6:28+6*(i+1)])
    return case

def print_case(case):
    suits = u'♣♠♦♥'
    for row in case:
        for card in row:
            if card == -1: print ('Row\t')
            else: print(suits[suit(card)]+number_poker(card)+'\t',end='')
        print()

def print_house(house):
    suits = u'♣♠♦♥'
    print_case(house['case'])
    print('Cell\t',end='')
    for card in house['cell']:
        if card < 0: print('Open\t',end='')
        else: print(suits[suit(card)]+number_poker(card)+'\t',end='')
    print
    print('Found\t',end='')
    for card in house['fd']:
        if card < 0: print('Open\t',end='')
        else: print(suits[suit(card)]+number_poker(card)+'\t',end='')
    print

def make_move(house_temp, actions):
    house = copy.deepcopy(house_temp)
    for action in actions:
        target, destination = action
        if 0 <= target and target <= 7:
            card = house['case'][target].pop()
        elif 8 <= target:
            card = house['cell'][target-8]
            house['cell'][target-8] = -1
        if type(destination) != str and 0<=destination and destination<=7:
            house['case'][destination].append(card)
        elif destination == 'c':
            freecell = house['cell'].index(-1)
            house['cell'][freecell] = card
        elif destination == 'f':
            house['fd'][suit(card)] = card
        else:
            return 0
    return house

def available_moves(house):
    row_end = [row[-1] for row in house['case']]
    fds = house['fd']
    cells = house['cell']
    
    cell_avail = max([card == -1 for card in house['cell']])
    try: row_avail = row_end.index(-1)
    except: row_avail = -1
    
    son_list = []
    for card in row_end:
        num_card = number(card)
        if card >= 0 and num_card > 1:
            if color(card) == 0: 
                sons = [thecard(2,num_card-1),
                        thecard(3,num_card-1)]
            else: 
                sons = [thecard(0,num_card-1),
                        thecard(1,num_card-1)]
        else:
            sons = [-1,-1]
        son_list.append(sons[0])
        son_list.append(sons[1])
                
    for i_row,card in enumerate(row_end+cells):
        if card >= 0:
            if number(card) == number(fds[suit(card)]) + 1:
                yield (i_row,'f')
            if cell_avail and i_row <8:
                yield (i_row,'c')
            if row_avail>=0:
                yield (i_row,row_avail)
            for son,i_son in zip(son_list,range(16)):
                if card == son:
                    yield (i_row,int(i_son/2))

def heustic(house):
    # foundation
    heustic_fd = 12*4-sum([number(card) for card in house['fd']])
    small_cards = [thecard(thesuit,number(card)+1) for thesuit,card in enumerate(house['fd'])]
    
    heustic_small_cards = 0
    min_small_card = min([number(card) for card in small_cards])
    for small_card in small_cards:
        length = sum([sum([len(row) - i - 1 for i,x in enumerate(row) if x == small_card]) for row in house['case']])
        if number(small_card) == min_small_card:
            heustic_small_cards += length
        else:
            heustic_small_cards += length * 0.5  
    
    heustic_bad_pairs = 0
    for row in house['case']:
        if len(row) > 2:
            for i in range(1,len(row)-1):
#                paired = color(row[i]) <> color(row[i+1]) and \
#                         number(row[i]) == number(row[i+1]) + 1
                paired = number(row[i]) > number(row[i+1]) 
                if not paired:
                    heustic_bad_pairs += len(row) - i - 1
    
    heustic_cells = sum([0]+[1 for cell in house['cell'] if cell >= 0])
    
    heustic = - 10 * heustic_fd + \
              - 1 * heustic_small_cards + \
              - 0 * heustic_bad_pairs + \
              - 0 * heustic_cells
    return heustic 

def tc(inputstr):
    if inputstr[0] == '2':
        return thecard(2,int(inputstr[1:])-1)
    elif inputstr[0] == '1':
        return thecard(3,int(inputstr[1:])-1)
    elif inputstr[0] == '4':
        return thecard(0,int(inputstr[1:])-1)
    elif inputstr[0] == '3':
        return thecard(1,int(inputstr[1:])-1)
    
def tohash(house):
    string = ''
    for row in house['case']:
        for card in row:
            if card != -1:
                string += chr(card+1)
        string += '|'
    for card in sorted(house['cell']):
        if card != -1:
            string += chr(card+1)
    return string

def freecell_solver(new_case):
    house_initial = {'case':new_case,
                     'cell':[-1, -1, -1, -1],
                     'fd':[-1, -1, -1, -1]}
    #print_house(house_initial)
    frontier = [house_initial]
    frontier_heustic = [heustic(house_initial)]
    frontier_moves = [[]]
    explored = set([])
    found = False
    
    iteration = 0
    while not found:
        house_cur = frontier.pop()
        frontier_heustic.pop()
        moves = frontier_moves.pop()
        explored.add(tohash(house_cur))
        ams = available_moves(house_cur)
        for am in ams:
            house_sun = make_move(house_cur,[am])
            if tohash(house_sun) not in explored:
                house_sun_heustic = heustic(house_sun)
                rank = bisect.bisect_left(frontier_heustic,house_sun_heustic)
                frontier.insert(rank,house_sun)
                frontier_heustic.insert(rank,house_sun_heustic)
                frontier_moves.insert(rank,moves+[am])
                if sum([number(card) for card in house_sun['fd']]) == 48:
                    found = True
                    break
                if len(frontier) > 60000:
                    frontier.pop(0)
                    frontier_heustic.pop(0)
        iteration += 1
        if iteration % 2000 == 0: 
            print("Iteration",iteration,", score",-frontier_heustic[-1])
            #print_house(house_cur)
        if iteration >= 30000:
            break
    return found,iteration,moves+[am]

case = [[-1, tc('27'), tc('34'), tc('19'), tc('111'), tc('412'), tc('211'), tc('24')],
        [-1, tc('35'), tc('46'), tc('21'), tc('410'), tc('411'), tc('36'), tc('37')],
        [-1, tc('45'), tc('110'), tc('38'), tc('22'), tc('310'), tc('32'), tc('39')],
        [-1, tc('213'), tc('33'), tc('29'), tc('311'), tc('41'), tc('413'), tc('210')],
        [-1, tc('28'), tc('47'), tc('26'), tc('313'), tc('25'), tc('13')],
        [-1, tc('18'), tc('44'), tc('212'), tc('42'), tc('112'), tc('31')],
        [-1, tc('14'), tc('113'), tc('48'), tc('16'), tc('23'), tc('12')],
        [-1, tc('312'), tc('49'), tc('11'), tc('43'), tc('17'), tc('15')]]

freecell_solver(case)

#
#
##freecell_solver(generate_case(1))
#
#sols = []
#for seed in range(1000):
#    case = generate_case(seed)
#    print("Case",seed)
#    found, iteration, moves = freecell_solver(case)
#    if found:
#        print("Found the solution after",iteration,"iterations, solution length",len(moves),".")
#    else:
#        print("Solution not found after",iteration,"iterations.")
#    sols.append([found,iteration,len(moves)])
##    
##
##def print_house_tofile(f,house):
##    suits = u'[{}]'.encode('utf-8')
##    case = house['case']
##    for row in case:
##        for card in row:
##            if card == -1: print >>f, 'Row\t',
##            else: print >>f, suits[suit(card)]+number_poker(card)+'\t',
##        print >>f, '\n',
##    print >>f, 'Cell\t',
##    for card in house['cell']:
##        if card < 0: print >>f,'Open\t',
##        else: print >>f,suits[suit(card)]+number_poker(card)+'\t',
##    print >>f, '\n',
##    print >>f, 'Found\t',
##    for card in house['fd']:
##        if card < 0: print >>f, 'Open\t',
##        else: print >>f, suits[suit(card)]+number_poker(card)+'\t',
##    print >>f, '\n',
#
##f=open('output.txt','w')
##house = house_initial
##print_house_tofile(f,house)
##for act in moves + [am]:
##    print >>f,"Move",act[0],"to",act[1]
##    house = make_move(house,[act])
##    print_house_tofile(f,house)
##f.close()
##
##def plot_house(house,hcard,fn,bcolor):
##    import matplotlib.pyplot as plt
##    plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
##    plt.rcParams['axes.unicode_minus']=False
##    import matplotlib.patches as patches
##    plt.rcParams['figure.figsize'] = (20.0, 10.0)
##    fig = plt.figure()
##    ax = fig.add_axes([0,0,1,1])
##    suits = [u'梅花',u'黑桃',u'方块',u'红桃']
##    case = house['case']
##    row_space = 0.1
##    card_space = 0.07
##    for i,row in enumerate(case):
##        for j,card in enumerate(row[1:]):
##            if card == hcard:
##                p = patches.Rectangle(
##                    (0.04+row_space * i, 0.78-card_space * j,), 0.07, card_space,
##                    fill=True, color = bcolor, alpha = 0.2, transform=ax.transAxes, clip_on=False
##                    )
##            else:
##                p = patches.Rectangle(
##                    (0.04+row_space * i, 0.78-card_space * j,), 0.07, card_space,
##                    fill=False, transform=ax.transAxes, clip_on=False
##                    )
##            ax.add_patch(p)
##            ax.text(0.05+row_space * i, 0.8-card_space * j, suits[suit(card)]+"-"+number_poker(card),
##                     color='red' if color(card) == 1 else 'black',fontsize=20,)
##    
##    row_space = 0.08
##    for i,card in enumerate(house['cell']):
##        if card == hcard:
##            p = patches.Rectangle(
##                (0.04+row_space * i, 0.88,), 0.07, card_space,
##                fill=True, color = bcolor, alpha = 0.2, transform=ax.transAxes, clip_on=False
##                )
##        else:
##            p = patches.Rectangle(
##                (0.04+row_space * i, 0.88,), 0.07, card_space,
##                fill=False, transform=ax.transAxes, clip_on=False
##                )
##        ax.add_patch(p)
##        if card <> -1:
##            ax.text(0.05+row_space * i, 0.9, suits[suit(card)]+"-"+number_poker(card),
##                     color='red' if color(card) == 1 else 'black',fontsize=20,)
##            
##    row_space = 0.08
##    for i,card in enumerate(house['fd']):
##        if card == hcard:
##            p = patches.Rectangle(
##                (0.5+row_space * i, 0.88,), 0.07, card_space,
##                fill=True, color = bcolor, alpha = 0.2, transform=ax.transAxes, clip_on=False
##                )
##        else:
##            p = patches.Rectangle(
##                (0.5+row_space * i, 0.88,), 0.07, card_space,
##                fill=False, transform=ax.transAxes, clip_on=False
##                )
##        ax.add_patch(p)
##        if card <> -1:
##            ax.text(0.51+row_space * i, 0.9, suits[suit(card)]+"-"+number_poker(card),
##                     color='red' if color(card) == 1 else 'black',fontsize=20,)
##            
##    ax.text(0.40, 0.9, 'FreeCell',
##                     color='red' if color(card) == 1 else 'black',fontsize=20,)
##    #ax.set_axis_off()
##    plt.savefig('imgs/'+str(fn)+'.png')
##    plt.clf()
##               
#
##
##house = house_initial
##for i,act in enumerate(moves + [am]):
##    if i%2 == 0: tcolor = 'blue'
##    else: tcolor = 'green'
##    print i
##    if act[0] <=7:
##        hcard = house['case'][act[0]][-1]
##    else:
##        hcard = house['cell'][act[0]-8]
##    plot_house(house,hcard,2*i,tcolor)
##    house = make_move(house,[act])
##    plot_house(house,hcard,2*i+1,tcolor)
