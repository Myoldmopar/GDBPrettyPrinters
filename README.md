# GDB Pretty Printers

Right now this just supports Objexx Arrays up to 3D.

## Using

To use, check out this repo somewhere on your machine, or drop the `printers/array.py` file somewhere you can find it.
Then, in your `~/.gdbinit` file, add the following lines:

```
python
import sys
sys.path.insert(0, "/path/to/GDBPrettyPrinters/printers")
import array
print("Loaded Objexx Array pretty printer")
end
```

Next time you run gdb, the pretty printer should be loaded, and in a suitable context, you should see something like this:

![img.png](screenshot.png)

## Developing

If you open this project, it _should_ load up the stubs folder automatically for code completion.
The GDB stub file is not complete, but is sufficient for the API calls used in this pretty printer.
I welcome more printers and added GDB stubs if you want to contribute!
