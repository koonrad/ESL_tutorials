from pygmyhdl import *

@chunk
def dff(clk_i, d_i, q_o):

    @seq_logic(clk_i.posedge)
    def logic():
        q_o.next = d_i

@chunk
def register(clk_i, d_i, q_o):
    for k in range(len(d_i)):
        dff(clk_i, d_i.o[k], q_o.i[k])

@chunk
def full_adder_bit(a_i, b_i, c_i, s_o, c_o):
    @comb_logic
    def logic():
        # Exclusive-OR (^) the inputs to create the sum bit.
        s_o.next = a_i ^ b_i ^ c_i
        # Generate a carry output if two or more of the inputs are 1.
        # This uses the logic AND (&) and OR (|) operators.
        c_o.next = (a_i & b_i) | (a_i & c_i) | (b_i & c_i)


@chunk
def adder(a_i, b_i, s_o):

    c = Bus(len(a_i) + 1)

    c.i[0] = 0

    for k in range(len(a_i)):
        full_adder_bit(a_i=a_i.o[k], b_i=b_i.o[k], c_i=c.o[k], s_o=s_o.i[k], c_o=c.i[k + 1])


@chunk
def counter(clk_i, cnt_o):

    length = len(cnt_o)

    one = Bus(length, init_val=1)
    next_cnt = Bus(length)

    adder(one, cnt_o, next_cnt)

    register(clk_i, next_cnt, cnt_o)


@chunk
def blinker(clk_i, led_o, length):

    cnt = Bus(length, name='cnt')
    counter(clk_i, cnt)

    @comb_logic
    def output_logic():
        led_o.next = cnt[length - 1]

initialize()
clk = Wire(name='clk')
led = Wire(name='led')
blinker(clk, led, 3)
clk_sim(clk, num_cycles=16)
#show_waveforms()
toVerilog(blinker, clk_i=clk, led_o=led, length=22)
