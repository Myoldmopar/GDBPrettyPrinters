from typing import Iterator, Tuple, Optional

import gdb


class ArrayPrinter:
    def __init__(self, val: gdb.Value):
        self.val = val
        self.data_ptr = val["data_"]
        self.elem_type = self.data_ptr.type.target()

    def _add_rank_1(self) -> None:
        try:
            self.rank_1_lower = int(self.val["I_"]["l_"])
            self.rank_1_upper = int(self.val["I_"]["u_"])
        except (gdb.error, ValueError, TypeError):
            self.rank_1_lower = int(self.val["I1_"]["l_"])
            self.rank_1_upper = int(self.val["I1_"]["u_"])
        self.rank_1_size = self.rank_1_upper - self.rank_1_lower + 1
        self.size_string = f"{{{self.rank_1_lower}:{self.rank_1_upper}}}"

    def _add_rank_2(self) -> None:
        self.rank_2_lower = int(self.val["I2_"]["l_"])
        self.rank_2_upper = int(self.val["I2_"]["u_"])
        self.rank_2_size = self.rank_2_upper - self.rank_2_lower + 1
        self.size_string += f" x {{{self.rank_2_lower}:{self.rank_2_upper}}}"

    def _add_rank_3(self) -> None:
        self.rank_3_lower = int(self.val["I3_"]["l_"])
        self.rank_3_upper = int(self.val["I3_"]["u_"])
        self.rank_3_size = self.rank_3_upper - self.rank_3_lower + 1
        self.size_string += f" x {{{self.rank_3_lower}:{self.rank_3_upper}}}"

    def to_string(self) -> str:
        return f"{self.val.type} [{self.size_string}] at {self.data_ptr}"


class Array1Printer(ArrayPrinter):
    def __init__(self, val: gdb.Value):
        super().__init__(val)
        self._add_rank_1()
        self.total_size = self.rank_1_size

    def children(self) -> Iterator[Tuple[str, gdb.Value]]:
        for x in range(self.rank_1_size):
            objexx_index = str(x + self.rank_1_lower)
            child = (self.data_ptr + x).dereference().cast(self.elem_type)
            yield objexx_index, child


class Array2Printer(ArrayPrinter):

    def __init__(self, val: gdb.Value):
        super().__init__(val)
        self._add_rank_1()
        self._add_rank_2()
        self.total_size = self.rank_1_size * self.rank_2_size

    def children(self) -> Iterator[Tuple[str, gdb.Value]]:
        for j in range(self.rank_2_size):
            for i in range(self.rank_1_size):
                offset = j * self.rank_1_size + i
                elem = (self.data_ptr + offset).dereference().cast(self.elem_type)
                label = f"({j + self.rank_2_lower}, {i + self.rank_1_lower})"
                yield label, elem


class Array3Printer(ArrayPrinter):

    def __init__(self, val: gdb.Value):
        super().__init__(val)
        self._add_rank_1()
        self._add_rank_2()
        self._add_rank_3()
        self.total_size = self.rank_1_size * self.rank_2_size * self.rank_3_size

    def children(self) -> Iterator[Tuple[str, gdb.Value]]:
        for k in range(self.rank_3_size):
            for j in range(self.rank_2_size):
                for i in range(self.rank_1_size):
                    offset = (k * self.rank_2_size * self.rank_1_size) + (j * self.rank_1_size) + i
                    elem = (self.data_ptr + offset).dereference().cast(self.elem_type)
                    label = f"({k + self.rank_3_lower}, {j + self.rank_2_lower}, {i + self.rank_1_lower})"
                    yield label, elem


def array_3d_matcher(val) -> Optional[ArrayPrinter]:
    type_name = str(val.type.strip_typedefs())
    if type_name.startswith("ObjexxFCL::Array1"):
        return Array1Printer(val)
    elif type_name.startswith("ObjexxFCL::Array2"):
        return Array2Printer(val)
    elif type_name.startswith("ObjexxFCL::Array3"):
        return Array3Printer(val)
    return None


gdb.pretty_printers.append(array_3d_matcher)
