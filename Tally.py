from periphery import GPIO
import simpleobsws
import asyncio
import os

red_led = 72 # CHANGE TO YOUR NEEDS
yellow_led = 64 

led = GPIO(red_led, "out")


class ObsStudio:

    def __init__(self, ip, port, inpt, inpt_type):
        self.ip = ip
        self.port = port
        self.inpt_type = inpt_type
        self.inpt = inpt
        self.ws = None
        self.conf_path = "/home/pico/Tally/tally.conf"   # CHANGE TO YOUR NEEDS
        self.last_mod = os.path.getmtime(self.conf_path)

    def file_changed(self):
        ret = True
        if os.path.exists(self.conf_path):
            current_mod = os.path.getmtime(self.conf_path)
            if current_mod == self.last_mod:
                ret = False
            self.last_mod = current_mod
        return ret

    async def obs_event_callback(self, data):

        ignore = [
            "CurrentPreviewSceneChanged",
            "InputSettingsChanged",
            "InputShowStateChanged",
            "InputMuteStateChanged",
            "InputVolumeChanged",
            "InputAudioBalanceChanged",
            "InputAudioSyncOffsetChanged",
            "InputAudioTracksChanged",
            "InputAudioMonitorTypeChanged"
        ]

        if data["eventType"] == "CurrentProgramSceneChanged":
            scene_name = data["eventData"]["sceneName"]
            if self.inpt == scene_name:
                print("TALLY True")
                led.write(True)
            else:
                print("TALLY False")
                led.write(False)

        elif data["eventType"] == "InputActiveStateChanged":
            source_name = data["eventData"]["inputName"]
            if self.inpt == source_name:
                print("TALLY", data["eventData"]["videoActive"])
                led.write(data["eventData"]["videoActive"])

        elif data["eventType"] in ignore:
            return

        else:
            try:
                await self.set_status()
            except Exception as e:
                print(e)

    async def set_status(self):

        if self.inpt_type == "source":
            req = simpleobsws.Request('GetSourceActive', {"sourceName": self.inpt})
            res = await self.ws.call(req)
            if res.ok():
                res = res.responseData
                print("TALLY", res["videoActive"])
                led.write(res["videoActive"])
            else:
                print("req failed TALLY OFF")
                led.write(False)

        elif self.inpt_type == "scene":
            req = simpleobsws.Request('GetCurrentProgramScene')
            res = await self.ws.call(req)
            if res.ok():
                res = res.responseData
                if res["currentProgramSceneName"] == self.inpt:
                    print("TALLY ON")
                    led.write(True)
                else:
                    print("TALLY OFF")
                    led.write(False)
            else:
                print("req failed TALLY OFF")
                led.write(False)

    async def start_tally(self):

        parameters = simpleobsws.IdentificationParameters(ignoreNonFatalRequestChecks=False)

        if self.inpt_type == "source":
            parameters.eventSubscriptions = (1 << 17) | (1 << 3)
        elif self.inpt_type == "scene":
            parameters.eventSubscriptions = (1 << 2)

        self.ws = simpleobsws.WebSocketClient(url=f'ws://{self.ip}:{self.port}', password='', identification_parameters=parameters)
        self.ws.register_event_callback(self.obs_event_callback)

        while True:
            if self.file_changed():
                return

            if not self.ws.is_identified():
                try:
                    await asyncio.wait_for(self.ws.connect(), timeout=2)
                    await self.ws.wait_until_identified()
                    await asyncio.sleep(0.5)
                    await self.set_status()
                except Exception as e:
                    print("TALLY OFF on connection error", e)
                    led.write(False)
                    return

            await asyncio.sleep(0)


class Vmix:

    def __init__(self, ip, port, inpt):
        self.ip = ip
        self.port = port
        self.inpt = int(inpt)
        self.reader = None
        self.writer = None
        self.con_up = False
        self.subscribed = False
        self.conf_path = "/home/pico/Tally/tally.conf"   # CHANGE TO YOUR NEEDS
        self.last_mod = os.path.getmtime(self.conf_path)

    def file_changed(self):
        ret = True
        if os.path.exists(self.conf_path):
            current_mod = os.path.getmtime(self.conf_path)
            if current_mod == self.last_mod:
                ret = False
            self.last_mod = current_mod
        return ret

    def tally_handler(self, data):
        tally_data = data.split()[-1]

        if int(self.inpt) > len(tally_data):
            print("TALLY OFF")
            led.write(False)
            return

        elif tally_data[self.inpt - 1] == "1":
            print("TALLY ON")
            led.write(True)

        else:
            print("TALLY OFF")
            led.write(False)

    async def subscribe_tally(self):

        attempt = 0
        while True:
            try:
                msg = b"SUBSCRIBE TALLY\r\n"
                self.writer.write(msg)
                await self.writer.drain()

                data = await self.reader.readline()
                data = data.decode().strip()

                if "SUBSCRIBE OK TALLY Subscribed" in data:
                    self.subscribed = True
                    return
                else:
                    self.subscribed = False
                    attempt += 1

                if attempt == 3:
                    return

            except Exception as e:
                print(e)
                self.subscribed = False
                self.con_up = False
                return

    async def start_tally(self):

        while True:
            if self.file_changed():
                return

            if not self.con_up:

                if self.writer is not None:
                    self.writer.close()
                    await self.writer.wait_closed()
                    self.writer = None
                    self.reader = None

                try:
                    self.reader, self.writer = await asyncio.wait_for(asyncio.open_connection(self.ip, int(self.port)), timeout=2)
                    self.con_up = True
                except Exception as e:
                    print("TALLY OFF on connection error", e)
                    led.write(False)
                    self.con_up = False
                    self.subscribed = False
                    return

            else:
                try:
                    data = await self.reader.readline()
                    data = data.decode().strip()

                    if "VERSION OK" in data and not self.subscribed:
                        await self.subscribe_tally()

                    elif "TALLY OK" in data:
                        self.tally_handler(data)

                    elif data == "":
                        print("TALLY OFF")
                        led.write(False)
                        self.con_up = False
                        self.subscribed = False
                        return

                except Exception as e:
                    print("error in receiving", e)
                    self.con_up = False
                    self.subscribed = False
                    return


async def main():
    while True:

        with open("/home/pico/Tally/tally.conf", "r", encoding="utf-8") as file:   # CHANGE TO YOUR NEEDS
            lines = file.readlines()

        ip = ""
        port = 4455
        source = ""
        source_kind = ""
        software = ""

        for line in lines:
            line = line.strip()
            if "ip:" in line.lower():
                start = line.find('"') + 1
                end = line.find('"', start)
                ip = line[start:end].strip()

            elif "port:" in line.lower():
                start = line.find('"') + 1
                end = line.find('"', start)
                port = line[start:end].strip()

            elif "source:" in line.lower():
                if source_kind == "":
                    start = line.find('"', ) + 1
                    end = line.find('"', start)
                    source = line[start:end]
                    source_kind = "source"

            elif "scene:" in line.lower():
                if source_kind == "":
                    start = line.find('"', ) + 1
                    end = line.find('"', start)
                    source = line[start:end].strip()
                    source_kind = "scene"

            elif "input:" in line.lower():
                start = line.find('"') + 1
                end = line.find('"', start)
                source = line[start:end].strip()

            elif "software:" in line:
                start = line.find('"') + 1
                end = line.find('"', start)
                software = line[start:end].strip()

        if software == "obs":
            Tally = ObsStudio(ip, port, source, source_kind)
            await Tally.start_tally()
            print("read file again obs")
        elif software == "vmix":
            Tally = Vmix(ip, port, source)
            await Tally.start_tally()
            print("read file again vmix")


asyncio.run(main())
