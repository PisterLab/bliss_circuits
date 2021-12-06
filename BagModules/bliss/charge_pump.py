# -*- coding: utf-8 -*-

from typing import Dict

import os
import pkg_resources

from bag.design.module import Module


# noinspection PyPep8Naming
class bliss__charge_pump(Module):
    """Module for library bliss cell charge_pump.

    Fill in high level description here.
    """
    yaml_file = pkg_resources.resource_filename(__name__,
                                                os.path.join('netlist_info',
                                                             'charge_pump.yaml'))


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
            seg_dict='Number of fingers for each device. Keys {Keys {pinner, pouter_bias, pouter, ninner, nouter, nouter_bias}}',
            lch_dict='Channel lengths. Keys {pinner, pouter, ninner, nouter}',
            w_dict='Channel widths. Keys {pinner, pouter, ninner, nouter}',
            th_dict='Threshold flavors. Keys {pinner, pouter, ninner, nouter}'
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
        seg_dict    = params['seg_dict']
        lch_dict    = params['lch_dict']
        w_dict      = params['w_dict']
        th_dict     = params['th_dict']

        mirrn_params = dict(device_params=dict(l=lch_dict['nouter'],
                                                w=w_dict['nouter'],
                                                intent=th_dict['nouter']),
                            seg_in=seg_dict['nouter_bias'],
                            seg_out_list=[seg_dict['nouter']])
        mirrp_params = dict(device_params=dict(l=lch_dict['pouter'],
                                                w=w_dict['pouter'],
                                                intent=th_dict['pouter']),
                            seg_in=seg_dict['pouter_bias'],
                            seg_out_list=[seg_dict['pouter']])

        self.instances['XMIRRP'].design(**mirrp_params)
        self.instances['XMIRRN'].design(**mirrn_params)
        self.instances['XPINNER'].design(l=lch_dict['pinner'],
            w=w_dict['pinner'],
            intent=th_dict['pinner'],
            nf=seg_dict['pinner'])
        self.instances['XNINNER'].design(l=lch_dict['ninner'],
            w=w_dict['ninner'],
            intent=th_dict['ninner'],
            nf=seg_dict['ninner'])