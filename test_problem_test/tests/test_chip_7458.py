import cocotb
from cocotb.triggers import Timer, RisingEdge, FallingEdge
from cocotb.clock import Clock

async def reset_dut(dut):
    """Reset the DUT"""
    dut.nvdla_core_rstn.value = 0
    await RisingEdge(dut.nvdla_core_clk)
    await RisingEdge(dut.nvdla_core_clk)
    dut.nvdla_core_rstn.value = 1
    await RisingEdge(dut.nvdla_core_clk)

@cocotb.test()
async def test_csb_request_pipeline_basic(dut):
    """Test basic CSB request path through 3-stage pipeline"""
    # Start clock
    cocotb.start_soon(Clock(dut.nvdla_core_clk, 10, unit="ns").start())
    
    # Initialize inputs
    dut.csb2cacc_req_src_pvld.value = 0
    dut.csb2cacc_req_src_pd.value = 0
    dut.cacc2csb_resp_src_valid.value = 0
    dut.cacc2csb_resp_src_pd.value = 0
    dut.csb2cacc_req_dst_prdy.value = 1
    
    # Reset
    await reset_dut(dut)
    
    # Send a CSB request with test pattern (fits in 63-bit signal)
    test_data = 0x3EDCBA9876543210  # 62-bit test pattern (safe for 63-bit signal)
    dut.csb2cacc_req_src_pvld.value = 1
    dut.csb2cacc_req_src_pd.value = test_data
    
    # Check that prdy is always 1
    assert dut.csb2cacc_req_src_prdy.value == 1, "csb2cacc_req_src_prdy should always be 1"
    
    await RisingEdge(dut.nvdla_core_clk)
    dut.csb2cacc_req_src_pvld.value = 0
    
    # Wait for 3 clock cycles (3-stage pipeline)
    await RisingEdge(dut.nvdla_core_clk)
    await RisingEdge(dut.nvdla_core_clk)
    await RisingEdge(dut.nvdla_core_clk)
    
    # Check output after 3 cycles
    dut._log.info("csb2cacc_req_dst_pvld = %d, csb2cacc_req_dst_pd = 0x%x",
                  dut.csb2cacc_req_dst_pvld.value, dut.csb2cacc_req_dst_pd.value)
    
    assert dut.csb2cacc_req_dst_pvld.value == 1, "Valid signal should propagate through pipeline"
    assert dut.csb2cacc_req_dst_pd.value == test_data, f"Data mismatch: expected 0x{test_data:x}, got 0x{int(dut.csb2cacc_req_dst_pd.value):x}"
