"""CPU functionality."""

from typing import List, Optional


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self._ram = [0] * 256
        self._reg = [0] * 8
        self._reg[7] = 0xF4

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
            print(f"Error: Cannot read. MAR '{mar}' out of bounds")
            return -1

    def ram_write(self, mar: int, mdr: int) -> Optional[int]:
        try:
            self.ram[mar] = mdr & 0xFF
        except IndexError:
            print(f"Error: Cannot write. MAR '{mar}' out of bounds")
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
        def run_instruction():
            """ALU operations."""

            def ADD():
                self.reg[reg_a] += self.reg[reg_b]

            def MUL():
                self.reg[reg_a] *= self.reg[reg_b]

            dispatch = {"ADD": ADD, "MUL": MUL}

            try:
                dispatch[op]()
            except KeyError:
                raise Exception("Unsupported ALU operation")

        return run_instruction

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(
            f"TRACE: %02X | %02X %02X %02X |"
            % (
                self.pc,
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

            operand_count = self.ir >> 6
            is_alu = self.ir >> 5 & 0b1
            command = self.ir & 0b111

            def HLT():
                self.running = False

            def LDI():
                self.reg[operand_a] = operand_b

            def PRN():
                print(self.reg[operand_a])

            def PUSH():
                self.reg[7] -= 1
                self.ram_write(self.reg[7], self.reg[operand_a])

            def POP():
                self.reg[operand_a] = self.ram_read(self.reg[7])
                self.reg[7] += 1

            dispatch = dict()
            dispatch[0b1] = HLT
            dispatch[0b10] = LDI
            dispatch[0b111] = PRN
            dispatch[0b101] = PUSH
            dispatch[0b110] = POP

            alu_dispatch = dict()
            alu_dispatch[0b10] = self.alu("MUL", operand_a, operand_b)

            if is_alu:
                try:
                    alu_dispatch[command]()
                except KeyError:
                    print(f"Error: command {command} not found")
            else:
                try:
                    dispatch[command]()
                except KeyError:
                    print(f"Error: command {command} not found")

            self.pc += 1 + operand_count
