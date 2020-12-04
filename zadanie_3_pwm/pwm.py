from pygmyhdl import *


@chunk
def pwm_glitchless(clk_i, pwm_o, threshold, interval):
    import math
    length = math.ceil(math.log(interval, 2))
    cnt = Bus(length)

    threshold_r = Bus(length, name='threshold_r')  # Create a register to hold the threshold value.

    @seq_logic(clk_i.posedge)
    def cntr_logic():
        cnt.next = cnt + 1
        if cnt == interval - 1:
            cnt.next = 0
            threshold_r.next = threshold  # The threshold only changes at the end of a pulse.

    @comb_logic
    def output_logic():
        pwm_o.next = cnt < threshold_r

def test_bench(num_cycles):
    clk.next = 0
    threshold.next = 3  # Start with threshold of 3.
    yield delay(1)
    for cycle in range(num_cycles):
        clk.next = 0
        # Raise the threshold to 8 after 15 cycles.
        if cycle >= 14:
            threshold.next = 8
        yield delay(1)
        clk.next = 1
        yield delay(1)
initialize()
clk = Wire(name='clk')
pwm = Wire(name='pwm')
threshold = Bus(4, name='threshold')
pwm_glitchless(clk, pwm, threshold, 10)

simulate(test_bench(22))
#show_waveforms(tick=True, start_time=19)

toVerilog(pwm_glitchless, clk, pwm, threshold, 227)
