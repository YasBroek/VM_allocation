from copy import deepcopy

def extend_and_sort(server_types):
    servers = []
    max_cpu = max(s.vCPU for s in server_types)
    max_ram = max(s.RAM for s in server_types)
    max_disk = max(s.disk for s in server_types)
    for s in server_types:
        for q in range(s.qty):
            new_s = deepcopy(s)
            new_s.ID = f"{s.ID}_{q+1}"
            servers.append(new_s)
    servers.sort(key=lambda s: (s.cost, (s.vCPU/max_cpu + s.RAM/max_ram + s.disk/max_disk)))

    return servers

def sort_vm(vms, server_types):
    max_cpu = max(s.vCPU for s in server_types)
    max_ram = max(s.RAM for s in server_types)
    max_disk = max(s.disk for s in server_types)

    vms_sorted = sorted(
        vms,
        key=lambda v: max(
            v.vCPU / max_cpu,
            v.RAM / max_ram,
            v.disk / max_disk
        ),
        reverse=True
    )

    return vms_sorted