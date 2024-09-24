# CHIP Fuzzer
This python based fuzzing tool allows dynamic blackbox fuzzing of Matter based IoT devices. The fuzzing tool sends 
inputs to IoT devices using modified chip-tool. The ZCL schema(s) are modified to allow fuzzing of input data.

# Future Work
Instead of modifying ZCL and rebuilding chip-tool, the chip tool itself should be modified such that it allows client
to send arbitrary fuzzed input data to IoT devices. This will allow integration with traditional fuzzing software such
as AFL.