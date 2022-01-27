# -*- coding: utf-8 -*-

from typing import Dict, Mapping

import os
import pkg_resources

from bag.design.module import Module


# noinspection PyPep8Naming
class bliss__delay_line_looped(Module):
    """Module for library bliss cell delay_line_looped.

    Fill in high level description here.
    """
    yaml_file = pkg_resources.resource_filename(__name__,
                                                os.path.join('netlist_info',
                                                             'delay_line_looped.yaml'))


    def __init__(self, database, parent=None, prj=None, **kwargs):
        Module.__init__(self, database, self.yaml_file, parent=parent, prj=prj, **kwargs)

    @classmethod
    def get_params_info(cls) -> Mapping[str,str]:
        # type: () -> Dict[str, str]
        """Returns a dictionary from parameter names to descriptions.

        Returns
        -------
        param_info : Optional[Dict[str, str]]
            dictionary from parameter names to descriptions.
        """
        return dict(
            delay_unit_params = 'delay_unit(_nand) parameters.',
            num_inv = 'Number of inverters in the loop, not including the NAND. Must be even.'
        )

    def design(self, **params):
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
        unit_params = params['delay_unit_params']
        num_inv = params['num_inv']

        array_inv = num_inv > 2
        suffix_inv = f'<{num_inv//2 - 1}:0>' if array_inv else ''
        suffix_outb_short = f'<{num_inv//2}:1>' if array_inv else '<1>'
        suffix_outb_long = f'<{num_inv//2}:0>'

        assert (num_inv%2 == 0) and (num_inv>1), '(delay_line_looped) Need an even number of inverters'

        ### Designing instances with proper wiring
        self.instances['XNAND'].design(**unit_params)
        self.instances['XINV'].design(**unit_params)
        self.instances['XINVb'].design(**unit_params)
        if array_inv:
            self.array_instance('XINV', [f'XINV{suffix_inv}'], [{'in' : f'outb{suffix_inv}',
                'out' : f'out{suffix_inv}'}])
            self.array_instance('XINVb', [f'XINVb{suffix_inv}'], [{'in' : f'out{suffix_inv}',
                'out' : f'outb{suffix_outb_short}'}])
            self.reconnect_instance_terminal('XNAND', 'in<0>', f'outb<{num_inv//2}>')
            self.rename_pin('out', f'out{suffix_inv}')
            self.rename_pin('outb<1:0>', f'outb{suffix_outb_long}')

        ### Adjusting pins
        has_p = unit_params['has_p']
        has_n = unit_params['has_n']
        if not has_p:
            self.remove_pin('VP')
        if not has_n:
            self.remove_pin('VN')