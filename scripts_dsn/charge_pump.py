# -*- coding: utf-8 -*-

from typing import Mapping, Tuple, Any, List

import os
import pkg_resources
import numpy as np

from bag.design.module import Module
from . import DesignModule, get_mos_db, estimate_vth, parallel, verify_ratio, num_den_add, enable_print, disable_print
from bag.data.lti import LTICircuit, get_w_3db, get_stability_margins
from .amp_diff_mirr_bias import bag2_analog__amp_diff_mirr_bias_dsn
from .constant_gm import bag2_analog__constant_gm_dsn

# noinspection PyPep8Naming
class bliss__charge_pump_dsn(DesignModule):
    """Module for library bliss cell charge_pump.

    Fill in high level description here.
    """

    @classmethod
    def get_params_info(cls) -> Mapping[str,str]:
        # type: () -> Dict[str, str]
        """Returns a dictionary from parameter names to descriptions.

        Returns
        -------
        param_info : Optional[Dict[str, str]]
            dictionary from parameter names to descriptions.
        """
        ans = super().get_params_info()
        # TODO: add resistors to specfile_dict and th_dict 
        ans.update(dict(
            specfile_dict = 'Transistor database spec file names for each device. Keys {pinner, pouter, ninner, nouter}',
            th_dict = 'Transistor flavor dictionary. Keys {pinner, pouter, ninner, nouter}',
            l_dict = 'Transistor channel length dictionary. Keys {pinner, pouter, ninner, nouter}',
            sim_env = 'Simulation environment',
            vdd = 'Supply voltage in volts.',
            ipump = 'Target charge pump current in either direction.',
            iref_min = 'Minimum quantization of the reference current.',
            iref_max = 'Maximum reference current',
            optional_params = 'error_tol, vstar_min, res_vstep, vdiff_switch'
        ))
        return ans

    def meet_spec(self, **params) -> Tuple[Mapping[str,Any],Mapping[str,Any]]:
        """To be overridden by subclasses to design this module.

        Raises a ValueError if there is no solution.
        """
        ### Get DBs for each device
        specfile_dict = params['specfile_dict']
        l_dict = params['l_dict']
        th_dict = params['th_dict']
        sim_env = params['sim_env']
        
        # Databases
        db_dict = {k:get_mos_db(spec_file=specfile_dict[k],
                                intent=th_dict[k],
                                lch=l_dict[k],
                                sim_env=sim_env) for k in specfile_dict.keys()}

        vdd = params['vdd']
        ipump = params['ipump']
        iref_min = params['iref_min']
        iref_max = params['iref_max']

        optional_params = params['optional_params']
        vstar_min = optional_params.get('vstar_min',0.1)
        res_vstep = optional_params.get('res_vstep', vdd/1e3)
        error_tol = optional_params.get('error_tol', 0.05)
        vdiff_switch = optional_params.get('vdiff_switch', vdd/100)

        self.other_params = dict(l_dict=l_dict,
            w_dict=w_dict,
            th_dict=th_dict)

        # Keep track of viable ops
        viable_op_list = []

        # Check if you'll need more current than allowed for biasing
        ratio_ok, nf_ratio = verify_ratio(ipump, iref_min, 1, error_tol)
        if nf_ratio * iref_min > iref_max:
            return viable_op_list

        # Sweep possible gate voltages
        vth_pouter = estimate_vth(db=db_dict['pouter'], is_nch=False, vgs=-vdd/2, vbs=0, lch=l_dict['pouter'])
        vth_nouter = estimate_vth(db=db_dict['nouter'], is_nch=True, vgs=vdd/2, vbs=0, lch=l_dict['nouter'])
        vg_min = vth_nouter + vstar_min
        vg_max = vdd + vth_pouter - vstar_min
        vg_vec = np.arange(vg_min, vg_max, res_vstep)

        iref_mult_max = iref_max / iref_min
        iref_mult_vec = np.arange(1, iref_mult_max, 1)

        viable_n_list = []
        viable_p_list = []

        for iref_mult in iref_mult_vec:
            iref = iref_mult * iref_min

            # Design mirror devices
            for vg in vg_vec:
                # NMOS
                op_nmirr = db_dict['nouter'].query(vgs=vg, vds=vg, vbs=0)
                nmirr_ok, nf_nmirr = verify_ratio(iref, op_nmirr['ibias'], 1, error_tol)
                
                if nmirr_ok:
                    # Get viable vdn range
                    vdn_clear = False
                    vdn_vec = np.arange(vstar_min, vdd, res_vstep)
                    for vdn in vdn_vec:
                        op_nouter = db_dict['nouter'].query(vgs=vgn, vds=vdn, vbs=0)
                        idn = op_nouter['ibias'] * nf_ratio
                        if abs(idn-ipump)/ipump > error_tol:
                            if vdn_clear:
                                vdn_max = vdn
                                break
                            else:
                                vdn_min = vdn
                        else:
                            op_nsw = db_dict['ninner'].query(vgs=vdd-vdn_max, vds=vdiff_switch, vbs=-vdn_max)
                            nf_nsw = np.ceil(ipump/op_nsw['ibias'])
                            viable_n = dict(nf_nmirr=nf_nmirr,
                                nf_nouter=nf_nmirr*nf_ratio,
                                nf_nsw=nf_nsw,
                                irefn=iref,
                                vgn=vgn,
                                vdn=vdn,
                                vdn_min=vdn_min,
                                vdn_max=vdn_max)
                            viable_n_list.append(viable_n)

                # PMOS
                op_pmirr = db_dict['pouter'].query(vgs=vg-vdd, vds=vg-vdd, vbs=0)
                pmirr_ok, nf_pmirr = verify_ratio(irefp, op_pmirr['ibias'], 1, error_tol)

                if pmirr_ok:
                    # Get viable vdp range
                    vdp_clear = False
                    vdp_vec = np.arange(0, vdd-vstar_min, res_vstep)
                    for vdp in vdp_vec:
                        op_pouter = db_dict['pouter'].query(vgs=vgp-vdd, vds=vdp-vdd, vbs=0)
                        idp = op_pouter['ibias'] * nf_ratio
                        if abs(idp-ipump)/ipump > error_tol:
                            if vdp_clear:
                                vdp_max = vdp
                                break
                            else:
                                vdp_min = vdp
                        else:
                            op_psw = db_dict['pinner'].query(vgs=-vdp_min, vds=-vdiff_switch, vbs=vdd-vdp_min)
                            nf_psw = np.ceil(ipump/op_psw['ibias'])
                            viable_p = dict(nf_pmirr=nf_pmirr,
                                nf_pouter=nf_pmirr*nf_ratio,
                                nf_psw=nf_psw,
                                irefp=iref,
                                vgp=vgp,
                                vdp=vdp,
                                vdp_min=vdp_min,
                                vdp_max=vdp_max)
                            viable_p_list.append(viable_p)



        return viable_op_list

    def op_compare(self, op1:Mapping[str,Any], op2:Mapping[str,Any]):
        """Returns the best operating condition based on 
        minimizing bias current.
        """
        # return op2 if op1['ibias'] > op2['ibias'] else op1

    def get_sch_params(self, op):
        for k,lch in self.other_params['l_dict'].items():
            self.other_params['l_dict'][k] = float(lch)

        for k,wch in self.other_params['w_dict'].items():
            self.other_params['w_dict'][k] = float(wch)

        return dict(seg_dict=,
            lch_dict=self.other_params['l_dict'],
            w_dict=self.other_params['w_dict'],
            th_dict=self.other_params['th_dict'])