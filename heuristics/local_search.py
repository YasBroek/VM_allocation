from heuristics.first_fit_decreasing import first_fit_decreasing
from utils import *

def local_search(vms, server_types):
    result = first_fit_decreasing(vms, server_types)
    if result is None:
        return None
    allocations, _ = result
    if allocations is None:
        return None

    servers = extend_and_sort(server_types)
    server_map = {s.ID: s for s in servers}
    vm_map = {vm.ID: vm for vm in vms}

    assignment = {vm_id: srv_id for vm_id, srv_id in allocations}
    loads = {s.ID: [] for s in servers}
    for vm_id, srv_id in assignment.items():
        loads[srv_id].append(vm_id)

    def used_resources(srv_id, exclude=None):
        vms_on = [v for v in loads[srv_id] if v != exclude]
        return (
            sum(vm_map[v].vCPU for v in vms_on),
            sum(vm_map[v].RAM  for v in vms_on),
            sum(vm_map[v].disk for v in vms_on),
        )

    def can_fit(vm_id, srv_id):
        s = server_map[srv_id]
        u_cpu, u_ram, u_disk = used_resources(srv_id)
        vm = vm_map[vm_id]
        return (
            u_cpu  + vm.vCPU <= s.vCPU and
            u_ram  + vm.RAM  <= s.RAM  and
            u_disk + vm.disk <= s.disk
        )

    improved = True
    while improved:
        improved = False
        active = [sid for sid, vlist in loads.items() if vlist]
        # sort by number of VMs ascending — try to empty least loaded first
        active.sort(key=lambda sid: len(loads[sid]))

        for target in active:
            vms_to_move = list(loads[target])
            moved = []

            for vm_id in vms_to_move:
                for other in active:
                    if other == target:
                        continue
                    if can_fit(vm_id, other):
                        loads[other].append(vm_id)
                        loads[target].remove(vm_id)
                        assignment[vm_id] = other
                        moved.append(vm_id)
                        break

            if not loads[target]:  # server emptied
                improved = True
                break
            else:
                # undo moves for this target
                for vm_id in moved:
                    src = assignment[vm_id]
                    loads[src].remove(vm_id)
                    loads[target].append(vm_id)
                    assignment[vm_id] = target

    active = [sid for sid, vlist in loads.items() if vlist]
    final_allocations = [(vm_id, srv_id) for vm_id, srv_id in assignment.items()]
    return final_allocations, len(active)