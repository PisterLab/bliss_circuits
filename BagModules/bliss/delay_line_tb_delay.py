# -*- coding: utf-8 -*-

from typing import Dict

import os
import pkg_resources

from bag.design.module import Module


# noinspection PyPep8Naming
class bliss__delay_line_tb_delay(Module):
    """Module for library bliss cell delay_line_tb_delay.

    Fill in high level description here.
    """
    yaml_file = pkg_resources.resource_filename(__name__,
                                                os.path.join('netlist_info',
                                                             'delay_line_tb_delay.yaml'))


    def __init__(self, database, parent=None, prj=None, **kwargs):
        Module.__init__(self, database, self.yaml_file, parent=parent, prj=prj, **kwargs)

    @classmethod
    def get_params_info(cls):
        # type: () -> Dict[str, str]
        """Returns a dictionary from parameter names to descriptions.

        Returns
        -------
        param_info : Optional[Dict[str, str]]
            dictionary from parameter names to descriptions.
        """
        return dict(
            dut_params='Parameters for the design under test')

    def design(self, **params) -> None:
        """To be overridden by subclasses to design this module.

        This method should fill in values for all parameters in
        self.parameters.  To design instances of this module, you can
        call their design() method or any other ways you coded.

        To modify schematic structure, call:

        rename_pin()
        delete_instance()
        replace_instance_master()
        reconnect_instance_terminal()
        restore_instance()
        array_instance()
        """
        dut_params = params['dut_params']
        dut_num_inv = dut_params['num_inv']
        has_outb = dut_params['export_outb']
        num_out = dut_num_inv // 2
        num_outb = dut_num_inv - num_out if has_outb else 0

        suffix_out_long     = f'<{num_out-1}:0>' if num_out > 1 else ''
        suffix_outb_long    = f'<{num_bout-1}:0>' if num_outb > 1 else ''
        suffix_out_short    = f'<{num_out-2}:0>' if num_out > 2 else ''
        suffix_outb_short   = f'<{num_outb-2}:0>' if num_outb > 2 else ''

        # Design DUT
        self.instances['XDUT'].design(**dut_params)

        # Fix wiring
        if num_outb < 1:
            self.delete_instance('C0')
        elif num_outb > 1:
            self.array_instance('C0', [f'C0{suffix_outb_long}'], [dict(PLUS=f'outb,outbx{suffix_outb_short}',
                                                                MINUS='VSS')])
            self.reconnect_instance_terminal('XDUT', f'outb{suffix_outb_long}', f'outb,outbx{suffix_outb_short}')
        if num_out > 1:
            self.array_instance('CL', [f'CL{suffix_out_long}'], [dict(PLUS=f'out,outx{suffix_out_short}',
                                                                MINUS='VSS')])
            self.reconnect_instance_terminal('XDUT', f'out{suffix_out_long}', f'out,outx{suffix_out_short}')