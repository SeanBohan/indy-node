import pytest
from stp_core.loop.eventually import eventually
from sovrin_node.server.upgrader import Upgrader
import functools

whitelist = [
    'Upgrade to version {} scheduled on {} failed because timeout exceeded']


def testTimeoutWorks(nodeSet, looper, monkeypatch):
    """
    Checks that after some timeout upgrade is marked as failed if
    it not started
    """
    async def mock(*x):
        return None

    # patch get_timeout not to wait one whole minute
    monkeypatch.setattr(Upgrader, 'get_timeout', lambda self, timeout: timeout)
    # patch _open_connection_and_send to make node think it sent upgrade
    # successfully
    monkeypatch.setattr(Upgrader, '_open_connection_and_send', mock)
    pending = {node.name for node in nodeSet}
    when = 0
    version = '1.5.1'
    timeout = 1

    def chk():
        nonlocal pending
        assert len(pending) == 0

    def upgrade_failed_callback_test(nodeName):
        nonlocal pending
        pending.remove(nodeName)

    for node in nodeSet:
        monkeypatch.setattr(
            node.upgrader,
            '_upgradeFailedCallback',
            functools.partial(
                upgrade_failed_callback_test,
                node.name))
        looper.run(node.upgrader._sendUpdateRequest(when, version, timeout))

    looper.run(eventually(chk))
