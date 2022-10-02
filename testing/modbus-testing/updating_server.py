#!/usr/bin/env python3
# pylint: disable=missing-any-param-doc,differing-param-doc
"""Pymodbus Server With Updating Thread.

This is an example of having a background thread updating the
context while the server is operating. This can also be done with
a python thread::

    from threading import Thread
    Thread(target=updating_writer, args=(context,)).start()
"""
import asyncio
import logging

from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import StartAsyncTcpServer
from pymodbus.version import version


# --------------------------------------------------------------------------- #
# configure the service logging
# --------------------------------------------------------------------------- #
FORMAT = '%(asctime)s %(module)-15s:%(lineno)-8s %(message)s'
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# --------------------------------------------------------------------------- #
# define your callback process
# --------------------------------------------------------------------------- #
class ServerInfo():
    """Simple class to keep track of the server's info outside its creation method."""
    
    def __init__(self):
        self.context = None
        self.identity = None
        self.address = ("localhost", 5020)
    
    def getContext(self):
        return self.context
    
    def setContext(self, context):
        self.context = context
        
    def getIdentity(self):
        return self.identity
    
    def setIdentity(self, identity):
        self.identity = identity
    
    def getAddress(self):
        return self.address
    
    def setAddress(self, address):
        self.address = address
        


def updating_writer(extra, cycle):
    """Run every so often,

    and updates live values of the context. It should be noted
    that there is a lrace condition for the update.

    :param arguments: The input arguments to the call
    """
    log.debug("updating the context")
    # extract the slave (it's a single slave context, so first position)
    context = extra[0]
    # Registers: Coils (co), Discrete Inputs (di), Input Registers (ir), Holding Registers (hr)
    # di: 2
    register = 2
    # only one slave, so id = 0
    slave_id = 0x00
    # first two inputs, so starting point is 0x00
    address = 0x00
    values = context.getValues(register, address, count=2)
    txt = f"current values: {str(values)}"
    log.debug(txt)
    state = len(cycle) % 4
    if state == 0:
        cycle.clear()
        cycle.append(1)
    else:
        cycle.append(1)
    # update values based on the current state
    if state == 0:
        # turn on the lamp
        values = [1, 0]
    elif state == 1:
        # release the button, lamp still on
        values = [0, 0]
    elif state == 2:
        # turn off the lamp
        values = [0, 1]
    elif state == 3:
        # release all switches, lamp is off
        values = [0, 0]
    txt = f"new values: {str(values)}"
    log.debug(txt)
    context.setValues(register, address, values)


async def run_updating_server(server_info):
    """Run updating server."""
    

    # ----------------------------------------------------------------------- #
    # run the server you want
    # ----------------------------------------------------------------------- #
    log.debug("Start server")
    await StartAsyncTcpServer(
        context=server_info.getContext(), identity=server_info.getIdentity(), address=server_info.getAddress(), defer_start=False
    )
    log.debug("Done")


async def main():
    server_info = ServerInfo()
    # ----------------------------------------------------------------------- #
    # initialize your data store
    # ----------------------------------------------------------------------- #

    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [17] * 100),
        co=ModbusSequentialDataBlock(0, [17] * 100),
        hr=ModbusSequentialDataBlock(0, [17] * 100),
        ir=ModbusSequentialDataBlock(0, [17] * 100),
    )
    context = ModbusServerContext(slaves=store, single=True)

    # ----------------------------------------------------------------------- #
    # initialize the server information
    # ----------------------------------------------------------------------- #
    identity = ModbusDeviceIdentification(
        info_name={
            "VendorName": "pymodbus",
            "ProductCode": "PM",
            "VendorUrl": "https://github.com/riptideio/pymodbus/",
            "ProductName": "pymodbus Server",
            "ModelName": "pymodbus Server",
            "MajorMinorRevision": version.short(),
        }
    )
        
    server_info.setContext(context)
    server_info.setIdentity(identity)
    cycle = []
    server_ref = asyncio.create_task(run_updating_server(server_info))
    while True:
        updating_writer(server_info.getContext(), cycle)
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())