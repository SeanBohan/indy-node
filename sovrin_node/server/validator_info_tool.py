import importlib

from sovrin_node.__metadata__ import __version__ as node_pgk_version
from plenum.server.validator_info_tool import none_on_fail, \
    ValidatorNodeInfoTool as PlenumValidatorNodeInfoTool


class ValidatorNodeInfoTool(PlenumValidatorNodeInfoTool):

    @property
    def info(self):
        info = super().info
        info['metrics']['transaction-count'].update(
            config=self.__config_ledger_size
        )
        info.update(
            software={
                'indy-node': self.__node_pkg_version,
                'sovrin': self.__sovrin_pkg_version,
            }
        )
        return info

    @property
    @none_on_fail
    def __config_ledger_size(self):
        return self._node.configLedger.size

    @property
    @none_on_fail
    def __node_pkg_version(self):
        return node_pgk_version

    @property
    @none_on_fail
    def __sovrin_pkg_version(self):
        return importlib.import_module('sovrin').__version__
