#!/usr/bin/env python3
# PoisonedReverse.py - Distance Vector with Poisoned Reverse

INF = float('inf')

class Router:
    """Single Router in a Network"""
    def __init__(self, name):
        self.name = name    # router name
        self.neighbors = {} # {neighbor: cost}
        self.dis_vec = {}   # {dest: cost}              shortest to each dest
        self.next_hop = {}  # {dest: next_hop}          nexthop to each dest
        self.vec_table = {} # {dest: {next_hop: cost}}  every route to each dest

    def init_net(self, routers):
        """
        Initialize distance vector and table.
        e.g. router X: 
            neighbors = {y:3, z:9}
            dis_vec = {x:0, y:3, z:9}
            next_hop = {x:x, y:y, z:z}
            vec_table = {
                X:{Y:INF, Z:INF}, 
                Y:{Y:3, Z:INF}, 
                Z:{Y:INF, Z:9}
            }
        """
        # Initialize neighbors and next hops
        for node in routers:
            # node itself
            if node == self.name:
                self.dis_vec[node] = 0
                self.next_hop[node] = self.name
            # neighbor nodes
            elif node in self.neighbors:
                self.dis_vec[node] = self.neighbors[node]
                self.next_hop[node] = self.name
            # non-neighbor nodes
            else:
                self.dis_vec[node] = INF
                self.next_hop[node] = None

        # Initialize table of all routes
        for node in routers:
            self.vec_table[node] = {}
            for n in self.neighbors:
                if n == node:   # cost to direct neighbor
                    self.vec_table[node][n] = self.neighbors[n]
                else:           # cost to other nodes
                    self.vec_table[node][n] = INF

    def poisoned_reverse(self, target_neighbor=None):
        """
        Generate Distance Vector with Poisoned Reverse
        return poisoned dis_vec {dest: cost}
        """
        dv = {}
        for dest in self.dis_vec:
            if (target_neighbor is not None and 
                self.next_hop[dest] == target_neighbor and
                dest != target_neighbor):
                dv[dest] = INF  # Poisoned Reverse
            else:
                dv[dest] = self.dis_vec[dest]
        return dv

    def update_net(self, neighbor, neighbor_dv):
        """
        Update routing table based on neighbors' distance vector.
        At each node, D_x(y) = minimum over all v{ c(x,v)+D_v(y) }.
        Return True if find a minimum cost.
        """
        updated = False  # to determine convergence when method is called
        for dest in self.dis_vec:
            if dest == self.name:
                continue

            new_cost = self.neighbors[neighbor] + neighbor_dv[dest]
            
            if new_cost < self.vec_table[dest][neighbor]:
                # update cost via current neighbor
                self.vec_table[dest][neighbor] = new_cost
                updated = True
            
            min_cost = min(self.vec_table[dest].values())
            if min_cost < self.dis_vec[dest]:
                # update the minimum cost
                self.dis_vec[dest] = min_cost
                # handle multiple minimum cost with alphabetical order
                self.next_hop[dest] = min((hop for hop, c in self.vec_table[dest].items() if c == min_cost), key=lambda x: x)
                updated = True
        return updated

    def output_distance_table(self, routers):
        """
        Generate distance table.
        e.g. Distance Table of router X at t=0:
                Y    Z    
            Y    3    INF  
            Z    INF  9    
        """
        dis_table = []
        header = ''
        srouters = sorted(routers)
        # output header
        for via in srouters:
            if via == self.name:
                continue
            header += '  ' + via
        dis_table.append(header)

        # output content
        for dest in srouters:
            if dest == self.name:
                continue
            row = [dest]
            for i in srouters:
                if i == self.name:
                    continue
                cost = self.vec_table[dest].get(i, INF)
                row.append(str(cost) if cost != INF else "INF")
            dis_table.append(" ".join(row))
        return dis_table

    def output_routing_table(self):
        """
        Generate routing table.
        e.g. Routing Table of router X:
            Y,Y,3
            Z,Y,7
        """
        routing_table = []
        for dest in sorted(self.dis_vec):
            if self.dis_vec[dest] == INF:
                routing_table.append(f'{dest}, INF, INF')
            else:
                routing_table.append(f'{dest}, {self.next_hop[dest], self.dis_vec[dest]}')
        return routing_table
    

def distance_vector(routers, phase):
    """Simulate Distance Vector with Poisoned Reverse and Print Routing Tables"""
    print(f'\n—————————————————————| {phase} Phase |—————————————————————')
    # Initialize routers
    for router in routers.values():
        router.init_net(routers)
    # Run distance vector and print tables
    t = 0
    while True:
        # print distance table of each router
        for i in sorted(routers):
            print(f'Distance Table of router {i} at t={t}:')
            for j in routers[i].output_distance_table(routers):
                print(j)
            print()
    
        # Distance Vector with Poisoned Reverse
        convergence = True
        dis_vec_update = {}
        for i in routers:
            dis_vec_update[i] = {}
            for neighbor in routers[i].neighbors:
                dis_vec_update[i][neighbor] = routers[i].poisoned_reverse(neighbor)
        for router in routers.values():
            for neighbor in router.neighbors:
                updated = router.update_net(neighbor, dis_vec_update[neighbor])
                if updated:
                    convergence = False
        if convergence:
            break
        t += 1

    # print routing table of each router
    for i in sorted(routers):
        print(f'Routing Table of router {i}: ')
        print(f'next (via, cost)')
        for j in routers[i].output_routing_table():
            print(j)
        print()


def main():
    print('———————————————| Distance Vector Simulator |———————————————')
    print('1. Enter each node of the network (ends with START)')
    print('2. Enter pair of nodes and cost (ends with UPDATE)')
    print('3. Enter pair of nodes and cost update (ends with END)')
    print('————————————————————| Start Input Here |———————————————————')

    # Read the inputs line by line
    routers = {}
    separator = None
    read_start = []
    read_update = []
    while True:
        try:
            inputs = input().strip()
        except EOFError: # handle unexpected ending
            break
        if not inputs:   # detect empty line
            continue

        if inputs in ['START', 'UPDATE', 'END']:
            separator = inputs
            if inputs == 'END':
                break
            continue

        # read routers
        if separator == None:
            routers[inputs] = Router(inputs)
        # read START topology
        elif separator == 'START':
            read_start.append(inputs)
        # read UPDATE topology
        elif separator == 'UPDATE':
            read_update.append(inputs)

    # Run distance vector after START
    for topo_start in read_start:
        src, dest, cost = topo_start.split()
        cost = int(cost)
        routers[src].neighbors[dest] = cost
        routers[dest].neighbors[src] = cost
    distance_vector(routers, 'START')

    # Run distance vector after UPDATE
    for topo_update in read_update:
        src, dest, cost = topo_update.split()
        cost = int(cost)
        if cost == -1:
            del routers[src].neighbors[dest]
            del routers[dest].neighbors[src]
        else:
            routers[src].neighbors[dest] = cost
            routers[dest].neighbors[src] = cost
    distance_vector(routers, 'UPDATE')

    print(f'———————————————| Distance Vector Simulator |———————————————')
    print(f'——————————————————————————| END |——————————————————————————\n')


if __name__ == "__main__":
    main()
