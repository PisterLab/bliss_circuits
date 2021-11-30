# -*- coding: utf-8 -*-

from typing import Dict, Mapping
from warnings import warn

import os
import pkg_resources

from bag.design.module import Module


# noinspection PyPep8Naming
class bliss__vernier_core(Module):
    """Module for library bliss cell vernier_core.

    Fill in high level description here.
    """
    yaml_file = pkg_resources.resource_filename(__name__,
                                                os.path.join('netlist_info',
                                                             'vernier_core.yaml'))


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
            num_inv='Number of inverters to include in delay lines.',
            start_delay_inv_params='Start delay line inverter parameters',
            stop_delay_inv_params='Stop delay line inverter parameters',
            export_inv='True to probe the intermediate inverters and early-late those as well.',
            inv_params='Only necessary if export_inv is True. Inverter parameters for feeding to the early-late detectors.',
            early_late_params='Flip-flop parameters.'
        )

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
        num_inv             = params['num_inv']
        start_inv_params    = params['start_delay_inv_params']
        stop_inv_params     = params['stop_delay_inv_params']
        export_inv          = params['export_inv']
        ff_params           = params['early_late_params']

        start_nstack      = start_inv_params['nstack_params']['stack']
        start_pstack      = start_inv_params['pstack_params']['stack']
        start_has_ngate   = start_nstack > 1
        start_has_pgate   = start_pstack > 1

        stop_nstack      = stop_inv_params['nstack_params']['stack']
        stop_pstack      = stop_inv_params['pstack_params']['stack']
        stop_has_ngate   = stop_nstack > 1
        stop_has_pgate   = stop_pstack > 1

        ff_has_clr      = ff_params['has_clr']
        ff_has_set      = ff_params['has_set']

        num_out     = num_inv // 2
        num_outb    = num_inv - num_out if export_inv else 0

        suffix_out  = f'<{num_out-1}:0>' if num_out > 1 else ''
        suffix_outb = f'<{num_outb-1}:0>' if num_outb > 1 else ''

        # Remove unnecessary pins
        if num_outb < 1:
            self.remove_pin('QM')
        if not start_has_ngate:
            self.remove_pin('VN_START')
        if not start_has_pgate:
            self.remove_pin('VP_START')
        if not stop_has_ngate:
            self.remove_pin('VN_STOP')
        if not stop_has_pgate:
            self.remove_pin('VP_STOP')
        if not ff_has_clr:
            self.remove_pin('CLRb')
        if not ff_has_set:
            self.remove_pin('SETb')

        # Fixing pin indexing
        if num_out > 1:
            self.rename_pin('Q', f'Q{suffix_out}')
        if num_outb > 1:
            self.rename_pin('QM', f'QM{suffix_outb}')

        # Design and reconnect wiring for instances
        ## delay lines
        self.instances['XDELAY_START'].design(num_inv=num_inv,
            inv_tristate_params=start_inv_params,
            export_outb=export_inv)
        self.instances['XDELAY_STOP'].design(num_inv=num_inv,
            inv_tristate_params=stop_inv_params,
            export_outb=export_inv)

        if num_out > 1:
            for line in ('START', 'STOP'):
                self.reconnect_instance_terminal(f'XDELAY_{line}', 
                    f'out{suffix_out}',
                    f'out_{line}{suffix_out}')
        if num_outb > 1:
            for line in ('START', 'STOP'):
                self.reconnect_instance_terminal('XDELAY_{line}',
                    f'outb{suffix_outb}',
                    f'outb_{line}{suffix_outb}')

        ## noninverting output earlylate
        inst_earlylate = self.instances['XEARLYLATE']
        if num_out > 1:
            self.array_instance('XEARLYLATE', [f'XEARLYLATE{suffix_out}'], [dict(D=f'out_START{suffix_out}',
                CLK=f'out_STOP{suffix_out}',
                Q=f'Q{suffix_out}',
                Qb=f'Qb{suffix_out}',
                CLRb='CLRb',
                SETb='SETb',
                VDD='VDD',
                VSS='VSS')])
            inst_earlylate = self.instances['XEARLYLATE'][0]
        inst_earlylate.design(**ff_params)

        # inverting output earlylate and associated inverters
        if not export_inv:
            # removing unnecessary elements
            for inst in ('XINV_START', 'XINV_STOP', 'XEARLYLATEb'):
                self.delete_instance(inst)
        else:
            # arraying devices if necessary
            inst_earlylateb = self.instances['XEARLYLATEb']
            inst_inv_start  = self.instances['XINV_START']
            inst_inv_stop   = self.instances['XINV_STOP']

            if num_outb > 1:
                self.array_instance('XEARLYLATEb', [f'XEARLYLATEbb{suffix_outb}'], [dict(D=f'outbb_START{suffix_outb}',
                    CLK=f'outbb_STOP{suffix_outb}',
                    Q=f'QM{suffix_outb}',
                    Qb=f'QMb{suffix_outb}',
                    CLRb='SETb',
                    SETb='CLRb',
                    VDD='VDD',
                    VSS='VSS')])
                for line in ('START', 'STOP'):
                    self.array_instance(f'XINV_{line}', [f'XINV_{line}{suffix_outb}'], [{'in' : f'outb_{line}{suffix_outb}',
                        'out' : f'outbb_{line}{suffix_outb}'}])
                
                inst_earlylateb = self.instances['XEARLYLATEb'][0]
                inst_inv_start  = self.instances['XINV_START'][0]
                inst_inv_stop   = self.instances['XINV_STOP'][0]
            
            # design devices
            inst_earlylateb.design(**ff_params)
            inst_inv_start.design(**inv_params)
            inst_inv_stop.design(**inv_params)
