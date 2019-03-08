"""
Discrete Event Simulation for Inventory Management

Scenario:
---------
  We consider an inventory of a retail shop. The quantity of the inventory
  is periodically checked so that if the quantity falls below reorder point
  (ROP), an order is placed. After placing the order, the delivery
  arrives at the retail shop after a certain delay.

  A customer arrives at the retail shop and purchase one or multiple
  products. If the product is out-of-stock, the customer leaves the
  retail shop dissatisfied.
"""

import simpy
import random
import itertools
import matplotlib.pyplot as plt
plt.style.use('fivethirtyeight')

#RANDOM_SEED = 12
#random.seed(RANDOM_SEED)
MAX_PURCHASE = 10            # A customer can buy maximum of 10 products at a time
PRODUCT_PURCHASING_TIME = 0  # A customer takes about 2 unit time to buy a product
INVENTORY_SIZE = 20          # liters
ROP = 10                     # Reorder point for ordering the product
EOQ = 10                     # Economic order quantity
LEAD_TIME = 8                # The time it takes for a supplier to deliver the products once an order is placed
PERIODIC_CHECKING_TIME = 2   # Periodic checking time of the inventory
T_INTER = [0, 30]            # Create a customer every [min, max] unit time
SIM_TIME = 500               # Simulation time in seconds


def customer(env, inventory_stock, name = ''):
    """A customer arrives at the retail shop and purchase one or multiple
    products. If the product is out-of-stock, the customer leaves the
    retail shop dissatisfied."""
    #start = env.now
    #yield env.timeout(random.randint(1, 30))
    no_product_purchase = random.randint(1, MAX_PURCHASE)
    customer_demand.append(no_product_purchase)
    print('{} arriving at retail shop at {:.1f}'.format(name, env.now))
    customer_arrival_time.append(env.now)
    yield env.timeout(PRODUCT_PURCHASING_TIME)
    if inventory_stock.level >= no_product_purchase:
        print('{} purchased {} products in {:.1f}'.format(name,
                                                        no_product_purchase,
                                                        env.now))
        customer_purchase.append(no_product_purchase)
        yield inventory_stock.get(no_product_purchase)
        print('Inventory Level = {}'.format(inventory_stock.level))
    elif inventory_stock.level > 0:
        print('{} purchased {} products in {:.1f}'.format(name,
                                                        inventory_stock.level,
                                                        env.now))
        customer_purchase.append(inventory_stock.level)
        yield inventory_stock.get(inventory_stock.level)
        print('{} leaves partly dissatisfied'.format(name))
        print('Inventory Level = 0')
    else:
        print('{} purchased nothing and leaves dissatisfied'.format(name))
        customer_purchase.append(0)
        print('Inventory Level = 0')


def inventory_control(env, inventory_stock):
    """Periodically check the quantity of the inventory and place the order
    if the quantity falls below reorder point."""
    while True:
        if inventory_stock.level <= ROP:
            print('Place order at {:.1f}'.format(env.now))
            order_placement_time.append(env.now)
            yield env.process(place_order(env, inventory_stock))
        #print('Periodic checking at {}, Inventory level = {}'.format(env.now, inventory_stock.level))
        priodic_checking_time.append(env.now)
        yield env.timeout(PERIODIC_CHECKING_TIME)  # Periodic checking of inventory


def place_order(env, inventory_stock):
    """Arrives at the retail shop after a certain delay."""
    yield env.timeout(LEAD_TIME)
    #amount = inventory_stock.capacity - inventory_stock.level
    amount = EOQ
    print('Inventory refilled by {1} products at {0} '.format(env.now, amount))
    print('Inventory Level = {}'.format(inventory_stock.capacity))
    order_arrival_time.append(env.now)
    order_amount.append(amount)
    yield inventory_stock.put(amount)


def customer_generator(env, inventory_stock):
    """Generate new customers that arrive at the retail shop."""
    for i in itertools.count():
        yield env.timeout(random.randint(*T_INTER))
        env.process(customer(env, inventory_stock, 'Customer_'+str(i+1)))

def data_collection(env, clock, inventory_level, inventory_stock):
    while True:
        clock.append(env.now)
        inventory_level.append(inventory_stock.level)
        yield env.timeout(0.1)

def plot_chart(env, clock, inventory_level, customer_arrival_time,
               priodic_checking_time, order_placement_time,\
               order_arrival_time, order_amount, customer_purchase,\
               customer_demand):
    
    
    fig1 = plt.figure(figsize = (20,8))
    while True:
        plt.clf()
        plot1 = plt.plot(clock, inventory_level,'b-', linewidth = 4,\
                         label = 'Inventory level')
        plot2 = plt.plot(clock, [ROP]*len(clock), 'k--', linewidth = 2,\
                         label = 'Reorder point (ROP)')

        plot3 = plt.plot(clock, [0]*len(clock), 'r--', linewidth = 2)
        plot4 = plt.plot(customer_arrival_time, [0]*len(customer_arrival_time),\
                         'rD', marker = '^', markersize = 14, \
                         linewidth = 0.5, label = 'Customer arrival')
        plot5 = plt.plot(clock, [-4]*len(clock), 'g--', linewidth = 2.0)
        plot6 = plt.plot(order_placement_time, [-4]*len(order_placement_time),\
                         'kD', marker = '^', markersize = 14, \
                         label = 'Order placement')
        plot7 = plt.plot(order_arrival_time, [-4]*len(order_arrival_time),\
                         'gD', marker = '^', markersize = 14, \
                         label = 'Order arrived')

        customer_purchase1 = ['-'+str(x) for x in customer_purchase]
        for x, y, z in zip(customer_arrival_time, [0]*len(customer_arrival_time),\
                           customer_purchase1):
            plt.annotate(z, xy=(x, y), xytext=(8, 15),\
                textcoords='offset points', ha='right', va='bottom', fontsize = 14,\
                bbox=dict(boxstyle='round,pad=0.3', fc='red', alpha=0.2))
            
        order_amount1 = ['+'+str(x) for x in order_amount]
        for x, y, z, w, t in zip(order_arrival_time, [-4]*len(order_arrival_time),\
                                 order_amount1, order_placement_time,\
                                 ['Placed\norder']*len(order_amount1)):
            plt.annotate(z, xy=(x, y), xytext=(10, 15),\
                textcoords='offset points', ha='right', va='bottom', fontsize = 12,\
                bbox=dict(boxstyle='round,pad=0.3', fc='green', alpha=0.2))
            plt.annotate(t, xy=(w, y), xytext=(20, 15),\
                textcoords='offset points', ha='right', va='bottom', fontsize = 12,\
                bbox=dict(boxstyle='round,pad=0.3', fc='yellow', alpha=0.2))

        plt.ylim(-6, 22)
        if clock[-1] <= 50:
            plt.xlim(0, 50)
        else:
            plt.xlim(clock[len(clock) - 500], clock[-1])
        plt.xlabel('Time')
        plt.ylabel('Inventory stock')
        leg = plt.legend(loc = 'upper left', fontsize=12)
        leg.get_frame().set_facecolor('w')
        #fig1.savefig('output.png',  dpi = 300)
        total_demand = sum(customer_demand)
        satisfied_demand = sum(customer_purchase)
        plt.title('Inventory Dynamics ('+str(satisfied_demand)+'/'+str(total_demand)+')\n'+\
                  'Unsatisfied Demand = '+str(total_demand - satisfied_demand))
        plt.show(block=False)
        plt.pause(0.0001) 
        yield env.timeout(0.5)
    

# Setup and start the simulation
print('Inventory Simulation')
print('--'*25)

# Variable for data collection
clock, inventory_level = [], []
customer_arrival_time, priodic_checking_time = [], []
order_placement_time, order_arrival_time, order_amount = [], [], []
customer_purchase, customer_demand = [], []

# Create environment and start processes
env = simpy.Environment()
inventory_stock = simpy.Container(env, INVENTORY_SIZE, init = INVENTORY_SIZE)
env.process(inventory_control(env, inventory_stock))
env.process(customer_generator(env, inventory_stock))
env.process(data_collection(env, clock, inventory_level, inventory_stock))
env.process(plot_chart(env, clock, inventory_level, customer_arrival_time,\
             priodic_checking_time, order_placement_time,\
             order_arrival_time, order_amount, customer_purchase, customer_demand))

# Execute!
env.run(until = SIM_TIME)








