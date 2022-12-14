"""Pymodbus Server With Updating Thread.
Based on this example 
https://pymodbus.readthedocs.io/en/dev/source/example/updating_server.html

This server is used alongside the demo.st code to test if the OpenPLC 
runtime is working as intended.
The purpose of this server is to expose two discrete inputs, whose values
change periodically, to the runtime which will read them and then change
the value of the output (the coil exposed) according to the behavior 
written in the demo code.

usage: updating_server.py [-h] [--host HOST] [--port PORT] [--log {critical,error,warning,info,debug}]

Self-updating modbus server to test the on OpenPLC.

options:
  -h, --help            show this help message and exit
  --host HOST           Host private network address for the server (avoid loopback address)
  --port PORT           The port to use for the server (default 5020)
  --log {critical,error,warning,info,debug}
                        Logging level for the logger (default INFO)
"""
import asyncio
import logging
import argparse

from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import StartAsyncTcpServer
from pymodbus.version import version

class ServerInfo():
    
    def __init__(self, context, identity, address):
        """Simple class to keep track of the server's info outside its creation method.
        
        :param context: ModbusServerContext object
        :param identity: ModbusDeviceIdentification object
        :param address: (str, int) containing host's address and port
        """
        self.context = context
        self.identity = identity
        self.address = address
    
    def getContext(self):
        return self.context
        
    def getIdentity(self):
        return self.identity
    
    def getAddress(self):
        return self.address


# configure the service logging
FORMAT = '%(asctime)s %(module)-15s:%(lineno)-8s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger()

 
def updating_writer(server_context, cycle):
    """Run every so often,
    and updates live values of the context. It should be noted
    that there is a lrace condition for the update.
    Changes the value of the first two discrete inputs based on
    the current cycle state.

    :param server_context: master collection of slave contexts
    :param cycle: list saving the cycle state (single integer value)
    """
    logger.debug("updating the context")
    # extract the slave (it's a single slave context, so first position)
    slave_context = server_context[0]
    # Registers: Coils (co), Discrete Inputs (di), Input Registers (ir), Holding Registers (hr)
    # fc_as_hex mappings
    # di: 2
    # ir: 4
    # co: 1, 5, 15
    # hr: 3, 6, 16, 22, 23
    register = 2
    # "In a MODBUS PDU each data is addressed from 0 to 65535"
    # The inputs of interest are the first two, so starting point is 0x00
    # zero_mode is set to False, which internally translates the final address to 1
    address = 0x00
    values = slave_context.getValues(register, address, count=2)
    txt = f"current values: {str(values)}"
    logger.debug(txt)
    state = cycle[0]
    # update cycle values (valid values: 0, 1, 2, 3, 4)
    cycle[0] = state + 1 if state != 4 else 0
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
        # all switches on, lamp is off
        values = [1, 1]
    elif state == 4:
        # all switches off, lamp is off
        values = [0, 0]
    txt = f"new values: {str(values)}"
    logger.info(txt)
    slave_context.setValues(register, address, values)


async def run_updating_server(server_info):
    """Run updating server.
    
    :param server_info: collection of server's info (context, identity, address)
    """
    
    logger.info(f'Starting server "{server_info.getIdentity().ProductName}"  @{server_info.getAddress()[0]}:{server_info.getAddress()[1]}...')
    await StartAsyncTcpServer(
        context=server_info.getContext(), identity=server_info.getIdentity(), address=server_info.getAddress(), defer_start=False
    )
    logger.debug("Done")


def get_commandline():
    """Read command line arguments and set logger level.
    
    :returns: a tuple (host, port) containing the address read.
    """
    
    parser = argparse.ArgumentParser(description="Self-updating modbus server to test the on OpenPLC.")
    parser.add_argument(
        "--host",
        help="Host private network address for the server (avoid loopback address)",
        type=str,
        default=""
    )
    parser.add_argument(
        "--port",
        help="The port to use for the server (default 5020)",
        type=int,
        default=5020
    )
    parser.add_argument(
        "--log",
        choices=["critical", "error", "warning", "info", "debug"],
        help="Logging level for the logger (default INFO)",
        type=str,
        default="INFO"
    )    
    args = parser.parse_args()
    
    logger.setLevel(args.log.upper())

    return (args.host, args.port)


async def main(args=None):
    """Initialize the server and call the writer to update the server's context.
    
    :param args: (host, port) tuple containing the address and the port for the server.
    """
    
    # retrieve address tuple (host, port)
    if not args:
        args = get_commandline()

    # initialize data store
    # Following the modbus application protocol specification section 4.4
    # (https://modbus.org/docs/Modbus_Application_Protocol_V1_1b3.pdf)
    # which states "In a MODBUS PDU each data is addressed from 0 to 65535" and
    # "In the MODBUS data Model each element within a data block is numbered from 1 to n"
    # the chosen starting address for the data blocks is "1" with 
    # ModbusSequentialDataBlock.zero_mode set to "False" (default value).
    # This means that the first value of the blocks is in position "1".
    # To change this behavior and have the first value in position "0",
    # the starting address must be "0" and the "zero_mode" must be enabled.

    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(1, [17] * 8),
        co=ModbusSequentialDataBlock(1, [17] * 8),
        hr=ModbusSequentialDataBlock(1, [17] * 16),
        ir=ModbusSequentialDataBlock(1, [17] * 16),
    )
    
    # create server context, single slave
    context = ModbusServerContext(slaves=store, single=True)

    # initialize the server information
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
    
    # save context and identity in a ServerInfo object
    server_info = ServerInfo(context, identity, args)
    cycle = [0]
    server_ref = asyncio.create_task(run_updating_server(server_info))
    while True:
        updating_writer(server_info.getContext(), cycle)
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())