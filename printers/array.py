from typing import Iterator, Tuple, Optional
import gdb


class ArrayPrinter:
    def __init__(self, val: gdb.Value):
        self.val = val
        self.data_ptr = val["data_"]
        self.elem_type = self.data_ptr.type.target()

        # Detect ranks dynamically
        self.ranks: list[Tuple[int, int]] = []
        for n in range(1, 5):
            for key in (f"I{n}_", "I_"):
                try:
                    l = int(val[key]["l_"])
                    u = int(val[key]["u_"])
                    self.ranks.append((l, u))
                    break
                except (gdb.error, ValueError, TypeError):
                    continue

        self.rank_sizes = [u - l + 1 for l, u in self.ranks]
        self.total_size = 1
        for size in self.rank_sizes:
            self.total_size *= size

    def to_string(self) -> str:
        sizes = " x ".join(f"{{{l}:{u}}}" for l, u in self.ranks)
        return f"{self.val.type} [{sizes}] at {self.data_ptr}"

    def children(self) -> Iterator[Tuple[str, gdb.Value]]:
        """Yield all elements with multidimensional indices (column-major)."""
        num_ranks = len(self.rank_sizes)
        indices = [0] * num_ranks

        for _ in range(self.total_size):
            # Compute column-major offset
            offset = 0
            stride = 1
            for dim in range(num_ranks):
                offset += indices[dim] * stride
                stride *= self.rank_sizes[dim]

            elem = (self.data_ptr + offset).dereference().cast(self.elem_type)
            label = "(" + ", ".join(str(indices[d] + self.ranks[d][0]) for d in range(num_ranks)) + ")"
            yield label, elem

            # Increment indices (like nested loops)
            for dim in range(num_ranks):
                indices[dim] += 1
                if indices[dim] < self.rank_sizes[dim]:
                    break
                indices[dim] = 0


def lookup_type(val) -> Optional[ArrayPrinter]:
    type_name = str(val.type.strip_typedefs())
    if type_name.startswith("ObjexxFCL::Array"):
        return ArrayPrinter(val)
    return None


gdb.pretty_printers.append(lookup_type)
