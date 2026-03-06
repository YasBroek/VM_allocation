from first_fit_decreasing import first_fit_decreasing
from utils import *

def local_search(vms, server_types):
    allocations, _ = first_fit_decreasing(vms, server_types)
    if allocations is None:
        return None

    servers = extend_and_sort(server_types)
    server_map = {s.ID: s for s in servers}
    vm_map = {vm.ID: vm for vm in vms}

    assignment = {vm_id: srv_id for vm_id, srv_id in allocations}
    loads = {s.ID: [] for s in servers}
    for vm_id, srv_id in assignment.items():
        loads[srv_id].append(vm_id)

    def can_fit(vm_id, srv_id, exclude_vm_id=None):
        s = server_map[srv_id]
        used_cpu  = sum(vm_map[v].vCPU for v in loads[srv_id] if v != exclude_vm_id)
        used_ram  = sum(vm_map[v].RAM  for v in loads[srv_id] if v != exclude_vm_id)
        used_disk = sum(vm_map[v].disk for v in loads[srv_id] if v != exclude_vm_id)
        vm = vm_map[vm_id]
        return (
            used_cpu  + vm.vCPU <= s.vCPU and
            used_ram  + vm.RAM  <= s.RAM  and
            used_disk + vm.disk <= s.disk
        )

    def move_vm(vm_id, to_srv_id):
        from_srv_id = assignment[vm_id]
        loads[from_srv_id].remove(vm_id)
        loads[to_srv_id].append(vm_id)
        assignment[vm_id] = to_srv_id

    improved = True
    while improved:
        improved = False

        active_servers = [sid for sid, vlist in loads.items() if vlist]
        active_servers.sort(key=lambda sid: len(loads[sid]))

        for target_srv_id in active_servers:
            vms_on_target = list(loads[target_srv_id])

            relocation = {}  
            success = True

            for vm_id in vms_on_target:
                placed = False
                for other_srv_id in active_servers:
                    if other_srv_id == target_srv_id:
                        continue
                    if other_srv_id in relocation.values():
                        pass
                    if can_fit(vm_id, other_srv_id):
                        relocation[vm_id] = other_srv_id
                        move_vm(vm_id, other_srv_id)
                        placed = True
                        break
                if not placed:
                    success = False
                    break

            if success and not loads[target_srv_id]:
                improved = True
                break
            else:
                for vm_id, dst in relocation.items():
                    move_vm(vm_id, target_srv_id)

        if not improved:
            active_servers = [sid for sid, vlist in loads.items() if vlist]
            for i, srv1 in enumerate(active_servers):
                for srv2 in active_servers[i+1:]:
                    for vm1 in list(loads[srv1]):
                        for vm2 in list(loads[srv2]):
                            if (can_fit(vm1, srv2, exclude_vm_id=vm2) and
                                can_fit(vm2, srv1, exclude_vm_id=vm1)):
                                move_vm(vm1, srv2)
                                move_vm(vm2, srv1)
                                improved = True

    active_servers = [sid for sid, vlist in loads.items() if vlist]
    final_allocations = [(vm_id, srv_id) for vm_id, srv_id in assignment.items()]
    return final_allocations, len(active_servers)