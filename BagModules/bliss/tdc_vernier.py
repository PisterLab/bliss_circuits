# -*- coding: utf-8 -*-

from typing import Dict, Mapping

import os
import pkg_resources

from bag.design.module import Module


# noinspection PyPep8Naming
class bliss__tdc_vernier(Module):
    """Module for library bliss cell tdc_vernier.

    Fill in high level description here.
    """
    yaml_file = pkg_resources.resource_filename(__name__,
                                                os.path.join('netlist_info',
                                                             'tdc_vernier.yaml'))


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
            start_delay_inv_params='Parameters for the START delay line inverters',
            stop_delay_inv_params='Parameters for the STOP delay line inverters',
            num_inv_dict='Number of inverters for each delay line. Keys vernier, dll_start/stop',
            early_late_params='Flip-flop parameters for the early-late detectors inthe vernier',
            pfd_params='Parameters for the phase frequency detector',
            cp_params='Parameters for the charge pump',
            clf_params='Parameters for the loop filter capacitor'
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
        start_inv_params    = params['start_delay_inv_params']
        stop_inv_params     = params['stop_delay_inv_params']
        num_inv_dict        = params['num_inv_dict']
        early_late_params   = params['early_late_params']
        pfd_params          = params['pfd_params']
        cp_params           = params['cp_params']
        clf_params          = params['clf_params']


        stop_ctrl_side = 'n' if stop_inv_params['nstack_params']['stack'] > 1 else 'p'
        start_ctrl_side = 'n' if start_inv_params['nstack_params']['stack'] > 1 else 'p'

        # Design Instances #
        dll_stop_params = dict(delay_line_params=dict(num_inv=num_inv_dict['dll_stop'],
                inv_tristate_params=stop_inv_params,
                export_outb=False),
            pfd_params=pfd_params,
            cp_params=cp_params,
            ctrl_side=stop_ctrl_side,
            clf_params=clf_params)

        dll_start_params = dict(delay_line_params=dict(num_inv=num_inv_dict['dll_start'],
                inv_tristate_params=start_inv_params,
                export_outb=False),
            pfd_params=pfd_params,
            cp_params=cp_params,
            ctrl_side=start_ctrl_side,
            clf_params=clf_params)

        self.instances['XDLL_START'].design(**dll_stop_params)
        self.instances['XDLL_STOP'].design(**dll_start_params)
        self.instances['XVERNIER'].design(num_inv=num_inv_dict['vernier'],
            start_delay_inv_params=start_inv_params,
            stop_delay_inv_params=stop_inv_params,
            export_inv=False,
            inv_params=None,
            early_late_params=early_late_params)

        # Renaming and removing pins # 
        self.remove_pin('QM')

        has_set = early_late_params.get('has_set', False)
        has_clr = early_late_params.get('has_clr', True)

        if not has_set:
            self.remove_pin('SETb')
        if not has_clr:
            self.remove_pin('CLRb')

        num_vernier = num_inv_dict['vernier']
        num_bit     = num_vernier // 2
        suffix_bit  = f'<{num_bit-1}:0>' if num_bit > 1 else ''
        suffix_bit_short = f'<{num_bit-2}:0>' if num_bit > 1 else ''

        if num_bit > 1:
            self.rename_pin('Q', f'Q{suffix_bit}')

        # Fixing wiring
        if num_bit > 1:
            self.reconnect_instance_terminal('XVERNIER', f'Q{suffix_bit}', f'Q{suffix_bit}')
            self.reconnect_instance_terminal('XVERNIER', 
                f'out_START{suffix_bit}', 
                f'out_START,out_STARTx{suffix_bit_short}')
            self.reconnect_instance_terminal('XVERNIER', 
                f'out_STOP{suffix_bit}', 
                f'out_STOP,out_STOPx{suffix_bit_short}')
            self.remove_pin('outb_START')
            self.remove_pin('outb_STOP')