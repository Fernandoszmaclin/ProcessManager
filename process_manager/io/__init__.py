from collections import deque

from process_manager.models import ProcessState


class IODeviceConfig:
    def __init__(self, device_id, simultaneous_uses, operation_time):
        self.device_id = device_id
        self.simultaneous_uses = simultaneous_uses
        self.operation_time = operation_time

    def __eq__(self, other):
        return isinstance(other, IODeviceConfig) and vars(self) == vars(other)


class IOManager:
    def __init__(self, devices):
        self.devices = {device.device_id: device for device in devices} # device id
        self.active = {device.device_id: [] for device in devices} # active IO on each device
        self.waiting = {device.device_id: deque() for device in devices} # processes waiting IO 


    def request(self, process, device_id, current_time):
        process.state = ProcessState.BLOCKED
        process.blocked_device = device_id
        if len(self.active[device_id]) < self.devices[device_id].simultaneous_uses:
            self._start(process, device_id, current_time)
        else:
            process.io_status = "aguardando"
            self.waiting[device_id].append(process)

    def advance(self, current_time):
        released = []
        for device_id, device in self.devices.items():
            finished = [
                process
                for process, end_time in self.active[device_id]
                if end_time <= current_time
            ]
            self.active[device_id] = [
                (process, end_time)
                for process, end_time in self.active[device_id]
                if end_time > current_time
            ]
            for process in finished:
                process.state = ProcessState.READY
                process.blocked_device = None
                process.io_status = None
                released.append(process)

            while self.waiting[device_id] and len(self.active[device_id]) < device.simultaneous_uses:
                self._start(self.waiting[device_id].popleft(), device_id, current_time)
        return released

    def next_completion(self):
        completion_times = []
        for operations in self.active.values():
            for _, end_time in operations:
                completion_times.append(end_time)
        return min(completion_times, default=None)

    def blocked_processes(self):
        blocked = []
        for operations in self.active.values():
            blocked.extend(process for process, _ in operations)
        for queue in self.waiting.values():
            blocked.extend(queue)
        return blocked

    def _start(self, process, device_id, current_time):
        process.io_status = "usando"
        end_time = current_time + self.devices[device_id].operation_time
        self.active[device_id].append((process, end_time))

    def describe(self):
        return [
            f"{device_id}: usando {[p.pid for p, _ in self.active[device_id]]}, "
            f"aguardando {[p.pid for p in self.waiting[device_id]]}"
            for device_id in self.devices
        ]
