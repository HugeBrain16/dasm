"""Assembly stuff but this one is WAYTOODANK"""

# not an actual assembly though, but works just like it

import io
import re
import asyncio
import discord
import cmdtools

from cmdtools.ext.command import CommandWrapper

__version__ = "1.0.0"

# OTHER SYNTAX
COMMENT = re.compile(r"^#.*")
CODE_BLOCK = re.compile(r"\`{3}[a-zA-Z0-9_]?")

# INSTRUCTIONS
LOAD_A = re.compile(r"^LOAD_A\s*(?P<address>\d+)$")
ADD    = re.compile(r"^ADD\s*(?P<address>\d+)$")  # noqa: E221
SUB    = re.compile(r"^SUB\s*(?P<address>\d+)$")  # noqa: E221
STA    = re.compile(r"^STA\s*(?P<address>\d+)$")  # noqa: E221
STORE  = re.compile(r"^STORE\s*(?P<address>\d+)\s*(?P<value>\d+)$")  # noqa: E221, E501
LOAD_I = re.compile(r"^LOAD_I\s*(?P<value>\d+)$")
OUT    = re.compile(r"^OUT$")  # noqa: E221
NOP    = re.compile(r"^NOP$")  # noqa: E221
HALT   = re.compile(r"^HALT$")  # noqa: E221

# JUMP and conditional jumps
JUMP   = re.compile(r"^JUMP\s*(?P<address>\d+)$")  # noqa: E221
JLT    = re.compile(r"^JLT\s*(?P<address>\d+)\s*(?P<value>\d+)$")  # JUMP If less than # noqa: E221, E501
JGT    = re.compile(r"^JGT\s*(?P<address>\d+)\s*(?P<value>\d+)$")  # JUMP If greater than  # noqa: E221, E501
JZ     = re.compile(r"^JZ\s*(?P<address>\d+)$")  # noqa: E221
JE     = re.compile(r"^JE\s*(?P<address>\d+)\s*(?P<value>\d+)$")  # noqa: E221
JNE    = re.compile(r"^JNE\s*(?P<address>\d+)\s*(?P<value>\d+)$")  # noqa: E221
JGE    = re.compile(r"^JGE\s*(?P<address>\d+)\s*(?P<value>\d+)$")  # noqa: E221
JLE    = re.compile(r"^JLE\s*(?P<address>\d+)\s*(?P<value>\d+)$")  # noqa: E221


class Instruction:
    def __init__(self, name, *args):
        self.name = name
        self.args = args

    def __repr__(self):
        return f"{self.name} {' '.join(self.args)}"


class Runtime:
    def __init__(self, memsize: int = 8):
        self.A = 0
        self.B = 0
        self.memory = [Instruction("NOP")] * memsize
        self.outs = []
        self.error = None

    def load(self, text: str):
        """load assembly program from text"""
        if type(text) not in (io.StringIO, io.TextIOWrapper):
            text = io.StringIO(text)

        pc = 0
        for line in text.readlines():
            line = line.strip()

            if not line or COMMENT.match(line):
                continue
            else:
                if pc < len(self.memory):
                    for semline in line.split(";") if len(line.split(";")) >= 1 else (line,):
                        semline = semline.strip()

                        if not semline:
                            continue

                        if LOAD_A.match(semline):
                            self.memory[pc] = Instruction("LOAD_A", LOAD_A.match(semline).group("address"))
                            pc += 1
                        elif ADD.match(semline):
                            self.memory[pc] = Instruction("ADD", ADD.match(semline).group("address"))
                            pc += 1
                        elif SUB.match(semline):
                            self.memory[pc] = Instruction("SUB", SUB.match(semline).group("address"))
                            pc += 1
                        elif STA.match(semline):
                            self.memory[pc] = Instruction("STA", STA.match(semline).group("address"))
                            pc += 1
                        elif OUT.match(semline):
                            self.memory[pc] = Instruction("OUT")
                            pc += 1
                        elif NOP.match(semline):
                            self.memory[pc] = Instruction("NOP")
                            pc += 1
                        elif HALT.match(semline):
                            self.memory[pc] = Instruction("HALT")
                            pc += 1
                        elif STORE.match(semline):
                            self.memory[pc] = Instruction("STORE", STORE.match(semline).group("address"), STORE.match(semline).group("value"))
                            pc += 1
                        elif LOAD_I.match(semline):
                            self.memory[pc] = Instruction("LOAD_I", LOAD_I.match(semline).group("value"))
                            pc += 1
                        elif JUMP.match(semline):
                            self.memory[pc] = Instruction("JUMP", JUMP.match(semline).group("address"))
                            pc += 1
                        elif JZ.match(semline):
                            self.memory[pc] = Instruction("JZ", JUMP.match(semline).group("address"))
                            pc += 1
                        elif JLT.match(semline):
                            self.memory[pc] = Instruction("JLT", JLT.match(semline).group("address"), JLT.match(semline).group("value"))
                            pc += 1
                        elif JGT.match(semline):
                            self.memory[pc] = Instruction("JGT", JGT.match(semline).group("address"), JGT.match(semline).group("value"))
                            pc += 1
                        elif JE.match(semline):
                            self.memory[pc] = Instruction("JE", JE.match(semline).group("address"), JE.match(semline).group("value"))
                            pc += 1
                        elif JNE.match(semline):
                            self.memory[pc] = Instruction("JNE", JNE.match(semline).group("address"), JNE.match(semline).group("value"))
                            pc += 1
                        elif JLE.match(semline):
                            self.memory[pc] = Instruction("JLE", JLE.match(semline).group("address"), JLE.match(semline).group("value"))
                            pc += 1
                        elif JGE.match(semline):
                            self.memory[pc] = Instruction("JGE", JGE.match(semline).group("address"), JGE.match(semline).group("value"))
                            pc += 1
                        else:
                            self.error = f"Illegal Instruction: {semline}\nat address `{hex(pc)}`"
                            break
                else:
                    self.error = f"Couldn't store more instructions, Out of memory\nat address: `{hex(pc)}`"
                    break

    async def exec(self):
        """execute stored instructions from memory"""
        pc = 0
        while True:
            if pc == len(self.memory) or self.error:
                break

            if isinstance(self.memory[pc], Instruction):
                if self.memory[pc].name == "LOAD_A":
                    self.A = self.memory[
                        ((int(self.memory[pc].args[0]) + 1) % len(self.memory)) - 1
                    ]
                elif self.memory[pc].name == "JUMP":
                    pc = ((int(self.memory[pc].args[0]) + 1) % len(self.memory) - 1)
                    continue
                elif self.memory[pc].name == "JLT":
                    if self.A < int(self.memory[pc].args[1]):
                        pc = ((int(self.memory[pc].args[0]) + 1) % len(self.memory) - 1)
                        continue
                elif self.memory[pc].name == "JE":
                    if self.A == int(self.memory[pc].args[1]):
                        pc = ((int(self.memory[pc].args[0]) + 1) % len(self.memory) - 1)
                        continue
                elif self.memory[pc].name == "JNE":
                    if self.A != int(self.memory[pc].args[1]):
                        pc = ((int(self.memory[pc].args[0]) + 1) % len(self.memory) - 1)
                        continue
                elif self.memory[pc].name == "JGT":
                    if self.A > int(self.memory[pc].args[1]):
                        pc = ((int(self.memory[pc].args[0]) + 1) % len(self.memory) - 1)
                        continue
                elif self.memory[pc].name == "JGE":
                    if self.A >= int(self.memory[pc].args[1]):
                        pc = ((int(self.memory[pc].args[0]) + 1) % len(self.memory) - 1)
                        continue
                elif self.memory[pc].name == "JLE":
                    if self.A <= int(self.memory[pc].args[1]):
                        pc = ((int(self.memory[pc].args[0]) + 1) % len(self.memory) - 1)
                        continue
                elif self.memory[pc].name == "JZ":
                    if self.A == 0:
                        pc = ((int(self.memory[pc].args[0]) + 1) % len(self.memory) - 1)
                        continue
                elif self.memory[pc].name == "LOAD_I":
                    self.A = int(self.memory[pc].args[0])
                elif self.memory[pc].name == "ADD":
                    self.B = self.memory[
                        ((int(self.memory[pc].args[0]) + 1) % len(self.memory)) - 1
                    ]
                    self.A += self.B
                elif self.memory[pc].name == "SUB":
                    self.B = self.memory[
                        ((int(self.memory[pc].args[0]) + 1) % len(self.memory)) - 1
                    ]
                    self.A -= self.B
                elif self.memory[pc].name == "STA":
                    self.memory[((int(self.memory[pc].args[0]) + 1) % len(self.memory)) - 1] = self.A
                elif self.memory[pc].name == "OUT":
                    self.outs.append(self.A)
                elif self.memory[pc].name == "HALT":
                    break
                elif self.memory[pc].name == "STORE":
                    if int(self.memory[pc].args[0]) < len(self.memory):
                        self.memory[int(self.memory[pc].args[0])] = int(self.memory[pc].args[1])
                    else:
                        self.error = f"Address {hex(int(self.memory[pc].args[0]))} does not exists\nat address: `{hex(pc)}`"

            pc += 1
            await asyncio.sleep(0.001)

class SharedRuntime(Runtime):
    """runtime, but with timeout and stuff..."""
    def __init__(self, timeout: int, memsize: int = 8):
        self.timeout = timeout
        self.uptime = 0
        super().__init__(memsize=memsize)
        
    async def counter(self):
        while True:
            self.uptime += 1
            await asyncio.sleep(1)

class Worker:
    """Worker class for multithreading, sort of..."""
    def __init__(self, loop: asyncio.Event):
        self.loop = loop

    async def getruntime(self, data: dict):
        async def check_uptime():
            while True:
                await asyncio.sleep(0.001)
                if data['runtime'].uptime >= data['runtime'].timeout:
                    execute.cancel()

        cuptime = self.loop.create_task(check_uptime())
        counter = self.loop.create_task(data['runtime'].counter())
        execute = self.loop.create_task(data['runtime'].exec())
        
        try:
            await execute
        except asyncio.CancelledError:
            embed = discord.Embed(title="Result", color=0xFF0000)
            embed.description = "runtime timeout"
            embed.add_field(name="Output", value= "```" + "\n".join([str(out) for out in data['runtime'].outs]) + "```")
            return await data['message'].reply(embed=embed)
        counter.cancel()
        cuptime.cancel()
        
        embed = discord.Embed(title="Result")
        if not data['runtime'].error:
            embed.color = 0x00FF00
            embed.description = "Successfully executed!"
            embed.add_field(name="Output", value= "```" + "\n".join([str(out) for out in data['runtime'].outs]) + "```")
        else:
            embed.color = 0xFF0000
            embed.description = "Runtime caught an error!"
            embed.add_field(name="Error", value="```" + data['runtime'].error + "```")

        await data['message'].reply(embed=embed)

class Bot(discord.Client):
    group = CommandWrapper()
    prefix = "!#"

    async def on_ready(self):
        self.worker = Worker(self.loop)

        print(f"Ready, Logged in as {self.user}")

    async def on_message(self, message):
        # not accepting messages from bot
        if message.author.bot:
            return

        # init commands
        @self.group.command(name="exec", aliases=["run", "execute"])
        async def exec():
            runtime = SharedRuntime(256)
            await message.reply("Please send the assembly code")
            def check(msg):
                return msg.author == message.author and msg.channel == message.channel
            try:
                msg = await self.wait_for('message', check=check, timeout=30)
            except asyncio.TimeoutError:
                await message.reply("You didn't respond in time")
            else:
                runtime.load(msg.content)
                
                if runtime.error:
                    embed = discord.Embed(title="Terminated")
                    embed.color = 0xFF0000
                    embed.description = "Runtime caught an error!"
                    embed.add_field(name="Error", value="```" + runtime.error + "```")
                    return await msg.reply(embed=embed)

                await msg.reply("Running...")
                self.loop.create_task(self.worker.getruntime({"runtime": runtime, "message": msg}))

        cmd = cmdtools.AioCmd(message.content, prefix=self.prefix)
        if cmd.name:
            await self.group.run(cmd)
