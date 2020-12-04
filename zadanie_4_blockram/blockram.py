from pygmyhdl import *


@chunk
def ram(clk_i, wr_i, addr_i, data_i, data_o):


    mem = [Bus(len(data_i)) for _ in range(2 ** len(addr_i))]

    @seq_logic(clk_i.posedge)
    def logic():
        if wr_i:
            mem[addr_i.val].next = data_i
        else:
            data_o.next = mem[addr_i.val]
@chunk
def gen_reset(clk_i, reset_o):

    cntr = Bus(1)

    @seq_logic(clk_i.posedge)
    def logic():
        if cntr < 1:

            cntr.next = cntr.next + 1
            reset_o.next = 1
        else:

            reset_o.next = 0


@chunk
def sample_en(clk_i, do_sample_o, frq_in=12e6, frq_sample=100):

    from math import ceil, log2
    rollover = int(ceil(frq_in / frq_sample)) - 1
    cntr = Bus(int(ceil(log2(frq_in / frq_sample))))

    @seq_logic(clk_i.posedge)
    def counter():
        cntr.next = cntr + 1
        do_sample_o.next = 0
        if cntr == rollover:
            do_sample_o.next = 1
            cntr.next = 0


@chunk
def record_play(clk_i, button_a, button_b, leds_o):

    reset = Wire()
    gen_reset(clk_i, reset)

    do_sample = Wire()
    sample_en(clk_i, do_sample)

    wr = Wire()
    addr = Bus(11)
    end_addr = Bus(len(addr))
    data_i = Bus(1)
    data_o = Bus(1)
    ram(clk_i, wr, addr, data_i, data_o)

    state = Bus(3)
    INIT = 0
    WAITING_TO_RECORD = 1
    RECORDING = 2
    WAITING_TO_PLAY = 3
    PLAYING = 4

    @seq_logic(clk_i.posedge)
    def fsm():

        wr.next = 0

        if reset:
            state.next = INIT

        elif do_sample:

            if state == INIT:
                leds_o.next = 0b10101
                if button_a == 1:

                    state.next = WAITING_TO_RECORD

            elif state == WAITING_TO_RECORD:
                leds_o.next = 0b11010
                if button_a == 0:

                    addr.next = 0
                    data_i.next = button_b
                    wr.next = 1
                    state.next = RECORDING

            elif state == RECORDING:
                addr.next = addr + 1
                data_i.next = button_b
                wr.next = 1

                leds_o.next = concat(1, button_b, button_b, button_b, button_b)
                if button_a == 1:

                    end_addr.next = addr + 1
                    state.next = WAITING_TO_PLAY

            elif state == WAITING_TO_PLAY:
                leds_o.next = 0b10000
                if button_a == 0:

                    addr.next = 0
                    state.next = PLAYING

            elif state == PLAYING:
                leds_o.next = concat(1, data_o[0], data_o[0], data_o[0], data_o[0])
                addr.next = addr + 1
                if addr == end_addr:

                    addr.next = 0
                if button_a == 1:

                    state.next = WAITING_TO_RECORD

toVerilog(record_play, clk_i=Wire(), button_a=Wire(), button_b=Wire(), leds_o=Bus(5))
