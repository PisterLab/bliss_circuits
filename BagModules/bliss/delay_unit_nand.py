# -*- coding: utf-8 -*-

from typing import Dict, Mapping

import os
import pkg_resources

from bag.design.module import Module


# noinspection PyPep8Naming
class bliss__delay_unit_nand(Module):
    """Module for library bliss cell delay_unit_nand.

    Fill in high level description here.
    """
    yaml_file = pkg_resources.resource_filename(__name__,
                                                os.path.join('netlist_info',
                                                             'delay_unit_nand.yaml'))


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
            has_p = 'Boolean. True to include an additional P device on the outside. False removes the possibility of P-side control or biasing.',
            has_n = 'Boolean. True to include an additional N device on the outside. False removes possibility of N-side control or biasing.',
            pstack_params = 'pmos4_astack parameters. Stack will be 2 for has_p, 1 otherwise.',
            nstack_params = 'nmos4_astack parameters. STack will be 3 for has_n, 2 otherwise.'
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
        has_p = params['has_p']
        has_n = params['has_n']

        assert has_p or has_n, '(delay_unit) Must have P or N side control'

        pstack_params = params['pstack_params']
        nstack_params = params['nstack_params']

        ### Design instances
        num_p = 2 if has_p else 1
        num_n = 3 if has_n else 2
        suffix_p = f'<1:0>' if has_p else ''
        suffix_n = f'<{num_n-1}:0>'
        
        gp0_lst = ['in<0>']
        gp1_lst = ['in<1>']
        if has_p:
            gp0_lst = ['VP'] + gp0_lst
            gp1_lst = ['VP'] + gp1_lst

        gn_lst = ['in<0>', 'in<1>']
        if has_n:
            gn_lst = ['VN'] + gn_lst

        # PMOS side
        self.instances['XP'].design(**pstack_params, stack=num_p, export_mid=False)
        self.array_instance('XP', ['XP<0>', 'XP<1>'], [{'S': 'VDD',
            'B' : 'VDD',
            'D' : 'out',
            f'G{suffix_p}' : ','.join(gp0_lst)
            }, {'S': 'VDD',
            'B' : 'VDD',
            'D' : 'out',
            f'G{suffix_p}' : ','.join(gp1_lst)}])

        # NMOS side
        self.instances['XN'].design(**nstack_params, stack=num_n, export_mid=False)
        self.reconnect_instance_terminal('XN', f'G{suffix_n}', ','.join(gn_lst))

        ### Removing unnecessary pins
        if not has_p:
            self.remove_pin('VP')
        if not has_n:
            self.remove_pin('VN')

