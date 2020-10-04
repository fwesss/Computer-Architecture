"""CPU functionality."""

from typing import List, Optional


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self._ram = [0] * 256
        self._reg = [0] * 8

        self._pc = 0
        self._ir = 0
        self._running = False

    @property
    def running(self) -> bool:
        return self._running

    @running.setter
    def running(self, value: bool) -> None:
        self._running = value

    @property
    def pc(self) -> int:
        return self._pc

    @pc.setter
    def pc(self, value: int) -> None:
        self._pc = value

    @property
    def ram(self) -> List[int]:
        return self._ram

    @property
    def reg(self) -> List[int]:
        return self._reg

    @property
    def ir(self) -> int:
        return self._ir

    @ir.setter
    def ir(self, value: int) -> None:
        self._ir = value

    def ram_read(self, mar: int) -> int:
        try:
            return self.ram[mar]
        except IndexError:
            print("Error: MAR out of bounds")
            return -1

    def ram_write(self, mar: int, mdr: int) -> Optional[int]:
        try:
            self.ram[mar] = mdr & 0xFF
        except IndexError:
            print("Error: MAR out of bounds")
            return -1

    def load(self, ins_file: str):
        """Load a program into memory."""
        program = []
        try:
            with open(ins_file) as f:
                for line in f:
                    if line[0] not in ["#", "\n"]:
                        program.append(int(line[:8], 2))
        except FileNotFoundError:
            print(f"Error: {ins_file} not found")
            return -1

        address = 0

        for instruction in program:
            self.ram[address] = instruction
            address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(
            f"TRACE: %02X | %02X %02X %02X |"
            % (
                self.pc,
                # self.fl,
                # self.ie,
                self.ram_read(self.pc),
                self.ram_read(self.pc + 1),
                self.ram_read(self.pc + 2),
            ),
            end="",
        )

        for i in range(8):
            print(" %02X" % self.reg[i], end="")

        print()

    def run(self):
        """Run the CPU."""
        self.running = True
        while self.running:
            self.ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            binary_ir = bin(self.ir)[2:].zfill(0)
            operand_count = int(binary_ir[:2], 2)

            def HLT():
                self.running = False

            def LDI():
                self.reg[operand_a] = operand_b

            def PRN():
                print(self.reg[operand_a])

            dispatch = dict()
            dispatch[int("00000001", 2)] = HLT()
            dispatch[int("10000010", 2)] = LDI()
            dispatch[int("01000111", 2)] = PRN()

            try:
                dispatch[self.ir]
            except KeyError:
                print("Error: command not found")

            self.pc += 1 + operand_count
