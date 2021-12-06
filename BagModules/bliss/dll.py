# -*- coding: utf-8 -*-

from typing import Dict

import os
import pkg_resources

from bag.design.module import Module


# noinspection PyPep8Naming
class bliss__dll(Module):
    """Module for library bliss cell dll.

    Fill in high level description here.
    """
    yaml_file = pkg_resources.resource_filename(__name__,
                                                os.path.join('netlist_info',
                                                             'dll.yaml'))


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
            delay_line_params='Parameters for the delay line.',
            pfd_params='Parameters for the phase frequency detector',
            cp_params='Parameters for the charge pump',
            ctrl_side='p or n for which side tunes the delay on the delay line.'
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
        delay_line_params   = params['delay_line_params']
        pfd_params          = params['pfd_params']
        cp_params           = params['cp_params']
        ctrl_side           = params['ctrl_side']

        delay_nstack = delay_line_params['inv_tristate_params']['nstack_params']['stack']
        delay_pstack = delay_line_params['inv_tristate_params']['pstack_params']['stack']
        has_ngate = delay_nstack > 1
        has_pgate = delay_pstack > 1

        assert (has_ngate and ctrl_side=='n') or (has_pgate and ctrl_side=='p'), "Attempting to control from a device that doesn't exist"

        if ctrl_side=='p':
            self.reconnect_instance_terminal('XDELAY', 'VP', 'VPD')
            self.reconnect_instance_terminal('XDELAY', 'VN', 'VN')


        self.instances['XDELAY'].design(**delay_line_params)
        self.instances['XPFD'].design(**pfd_params)
        self.instances['XCP'].design(**cp_params)

