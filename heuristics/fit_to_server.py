from copy import deepcopy
from utils import *

def fit_to_server(vms, server_types):
    
    vms_sorted = sort_vm(vms, server_types)

    servers = extend_and_sort(server_types)

    attributions = []
    used_servers = []
    max_iter = len(vms_sorted) + 1
    iter = 0

    while (len(vms_sorted)>=1 and iter < max_iter):
        if not servers:
            print("No feasible solution with FTS")
            return None
        s = servers[0]
        attributions.append((vms_sorted[0].ID,s.ID))
        s.vCPU -= vms_sorted[0].vCPU
        s.RAM -= vms_sorted[0].RAM
        s.disk -= vms_sorted[0].disk
        vms_sorted.pop(0)
        vms_att = []

        for i, vm in enumerate(vms_sorted):
            if (vm.vCPU <= s.vCPU and vm.RAM <= s.RAM and vm.disk <= s.disk):
                attributions.append((vm.ID, s.ID))
                s.vCPU -= vm.vCPU
                s.RAM -= vm.RAM
                s.disk -= vm.disk
                vms_att.append(i)

        for i in sorted(vms_att, reverse=True):
            vms_sorted.pop(i)
        
        used_servers.append(s)
        servers.pop(0)
        iter += 1

    return attributions, len(used_servers)
    


