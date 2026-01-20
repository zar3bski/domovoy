#!/usr/bin/python

# Copyright: (c) 2018, Terry Jones <terry.jones@example.org>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: nftables_rules

short_description: Set individual nftables rules

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: Set individual nftables rules in /etc/nftables.d/{input|forward|output}.{name}.rules

options:
    name:
        description: Set individual nftables rules.
        required: true
        type: str
    input:
        description:
            - osef
        required: false
        type: list
    forward:
        description:
            - osef
        required: false
        type: list
    output:
        description:
            - osef
        required: false
        type: list

author:
    - David Zarebski (@zar3bski)
"""

EXAMPLES = r"""
TODO
"""

RETURN = r"""
TODO
"""

from ansible.module_utils.basic import AnsibleModule
import os
#from ansible.builtin import systemd_service

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        name=dict(type="str", required=True),
        input=dict(type="list", elements="str", required=False, default=[]),
        forward=dict(type="list", elements="str", required=False, default=[]),
        output=dict(type="list", elements="str", required=False, default=[]),
    )
    module = AnsibleModule(argument_spec=module_args, supports_check_mode=True)

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(changed=False, message="")
    

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json(**result)

    # general logic
    for chain in ["input", "forward", "output"]:
        path = f"/etc/nftables.d/{chain}.{module.params['name']}.rules"
        if module.params[chain] != []:
            edit = False
            if os.path.exists(path) == False: 
                edit = True
            else:
                with open(path, "r") as file:
                    lines = [line.strip() for line in file.readlines() if line.strip() and not line.startswith('#')]
                    if module.params[chain] != lines:
                        edit = True
            if edit:
                with open(f"/etc/nftables.d/{chain}.{module.params['name']}.rules", "w") as file:
                    file.write("\n".join(module.params[chain])+"\n")
                    result["message"] += f"{path} updated\n"
                    result["changed"] = True
        else:
            if os.path.exists(path):
                os.remove(path)
                result["message"] += f"{path} remove\n"
                result["changed"] = True

    if result["changed"] == True:
        pass  # TODO: reload service from here

    module.exit_json(**result)


def main():
    run_module()


if __name__ == "__main__":
    main()
